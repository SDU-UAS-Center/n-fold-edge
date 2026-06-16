"""Detect a checkerboard in images."""

from __future__ import annotations

import collections
import math

import cv2
import numpy as np
from sklearn.neighbors import KDTree

from n_fold_edge.marker_locator import MarkerLocator


class CheckerBoard:
    """
    Detect corners of a checkerboard in images.

    Parameters
    ----------
    kernel_size
        Kernel size used by marker locator to detect corners.
    scale_factor
        Scale factor used by marker locator.
    distance_scale
        Distance scale of the corners relative to each other.
    relative_threshold_level
        Threshold level to apply at each corner.
    """

    def __init__(
        self,
        kernel_size: int = 55,
        scale_factor: float = 1000,
        distance_scale: int = 40,
        relative_threshold_level: float = 0.5,
    ) -> None:
        self.ml = MarkerLocator(2, kernel_size, scale_factor)
        self.distance_scale = distance_scale
        self.relative_threshold_level = relative_threshold_level

    def _local_normalization(self, response: np.ndarray, neighborhood_size: int) -> np.ndarray:
        _, max_val, _, _ = cv2.minMaxLoc(response)
        response_relative_to_neighborhood = self._peaks_relative_to_neighborhood(
            response, neighborhood_size, 0.05 * max_val
        )
        return response_relative_to_neighborhood

    def _peaks_relative_to_neighborhood(
        self, response: np.ndarray, neighborhood_size: int, value_to_add: float
    ) -> np.ndarray:
        local_min_image = self._minimum_image_value_in_neighborhood(response, neighborhood_size)
        local_max_image = self._maximum_image_value_in_neighborhood(response, neighborhood_size)
        response_relative_to_neighborhood = (response - local_min_image) / (
            value_to_add + local_max_image - local_min_image
        )
        return response_relative_to_neighborhood

    @staticmethod
    def _minimum_image_value_in_neighborhood(response: np.ndarray, neighborhood_size: float) -> np.ndarray:
        kernel_1 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        orig_size = response.shape
        for _ in range(int(math.log(neighborhood_size, 2))):
            eroded_response = cv2.morphologyEx(response, cv2.MORPH_ERODE, kernel_1)
            response = cv2.resize(eroded_response, None, fx=0.5, fy=0.5)
        local_min_image_temp = cv2.resize(response, (orig_size[1], orig_size[0]))
        return local_min_image_temp

    @staticmethod
    def _maximum_image_value_in_neighborhood(response: np.ndarray, neighborhood_size: float) -> np.ndarray:
        kernel_1 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        orig_size = response.shape
        for _ in range(int(math.log(neighborhood_size, 2))):
            eroded_response = cv2.morphologyEx(response, cv2.MORPH_DILATE, kernel_1)
            response = cv2.resize(eroded_response, None, fx=0.5, fy=0.5)
        local_min_image_temp = cv2.resize(response, (orig_size[1], orig_size[0]))
        return local_min_image_temp

    def _threshold_responses(self, response_relative_to_neighborhood: np.ndarray) -> np.ndarray:
        _, relative_responses_threshold = cv2.threshold(
            response_relative_to_neighborhood,
            self.relative_threshold_level,
            255,
            cv2.THRESH_BINARY,
        )
        return relative_responses_threshold

    @staticmethod
    def _get_center_of_mass(contour: np.ndarray) -> np.ndarray:
        m = cv2.moments(contour)
        if m["m00"] > 0:
            cx = m["m10"] / m["m00"]
            cy = m["m01"] / m["m00"]
            result = np.array([cx, cy])
        else:
            result = np.array([contour[0][0][0], contour[0][0][1]])
        return result

    def _locate_centers_of_peaks(self, relative_responses_threshold: np.ndarray) -> np.ndarray:
        contours, _ = cv2.findContours(
            relative_responses_threshold.astype(np.uint8),
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE,
        )
        centers = []
        for contour in contours:
            val = self._get_center_of_mass(contour)
            area = cv2.contourArea(contour)
            if area > 0:
                perimeter = cv2.arcLength(contour, closed=True)
                measure = 4 * np.pi * area / (perimeter * perimeter)
                if measure > 0.6:
                    centers.append(val)
        return np.array(centers)

    def find_corners(self, image: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Find corners of a checkerboard in the image.

        Parameters
        ----------
        image : ndarray
            Image of a checkerboard.

        Returns
        -------
        image_points : ndarray
            corners in image coordinates.
        object_points : ndarray
            corners in coordinates relative to each other.
        """
        gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        corner_response = self.ml.apply_convolution_with_complex_kernel(gray_image)
        response_relative_to_neighborhood = self._local_normalization(corner_response, self.distance_scale)
        relative_responses_threshold = self._threshold_responses(response_relative_to_neighborhood)
        centers = self._locate_centers_of_peaks(relative_responses_threshold)
        pe = _PeakEnumerator()
        calibration_points = pe.enumerate_peaks(centers)
        obj_points = []
        img_points = []
        for x, val in calibration_points.items():
            for y, uv in val.items():
                obj_points.append(np.array([x, y, 0]))
                img_points.append(uv)
        return np.array(img_points), np.array(obj_points)

    @staticmethod
    def image_coverage(image_shape: tuple[int, int], img_points: np.ndarray) -> int:
        """
        Estimate how much of the image is covered by the checkerboard.
        The image is divided into 100 equal regions and each region with a least one corner is counted.

        Parameters
        ----------
        image_shape : tuple[int, int]
            Image shape in height, width.
        img_points : ndarray
            The image points of the detected corners as returned from find_corners.

        Returns
        -------
        coverage : int
            Number of the 100 regions in image with a least one corner.

        """
        h = image_shape[0]
        w = image_shape[1]
        score = np.zeros((10, 10))
        for x, y in img_points:
            x_bin, _ = divmod(x, w / 10)
            y_bin, _ = divmod(y, h / 10)
            if x_bin == 10:
                x_bin = 9
            if y_bin == 10:
                y_bin = 9
            score[int(x_bin)][int(y_bin)] += 1
        return int(np.count_nonzero(score))


class _PeakEnumerator:
    def __init__(self, distance_threshold: float = 0.06) -> None:
        self.distance_threshold = distance_threshold

    @staticmethod
    def select_central_peak_location(centers: np.ndarray) -> np.ndarray:
        mean_position_of_centers = np.mean(centers, axis=0)
        central_center = np.array(
            sorted(
                centers,
                key=lambda c: np.sqrt(
                    (c[0] - mean_position_of_centers[0]) ** 2 + (c[1] - mean_position_of_centers[1]) ** 2
                ),
            )
        )
        return central_center[0]

    def enumerate_peaks(self, centers: np.ndarray) -> dict[int, dict[int, np.ndarray]]:
        central_peak_location = self.select_central_peak_location(centers)
        self.centers_kdtree = KDTree(np.array(centers))
        self.calibration_points = self.initialize_calibration_points(centers, central_peak_location)
        self.enumerate_central_square(centers)
        self.build_examination_queue()
        self.analyse_elements_in_queue(centers)
        return self.calibration_points

    def initialize_calibration_points(
        self, centers: np.ndarray, selected_center: np.ndarray
    ) -> dict[int, dict[int, np.ndarray]]:
        closest_neighbor, _ = self.locate_nearest_neighbor(centers, selected_center)
        direction = selected_center - closest_neighbor
        rotation_matrix = np.array([[0, 1], [-1, 0]])
        hat_vector = np.matmul(direction, rotation_matrix)
        # Check if selected_center and direction_b_neighbor are identical.
        # If that is the case, search for a point further away.
        ratio = 1.0
        while True:
            direction_b_neighbor, _ = self.locate_nearest_neighbor(
                centers,
                selected_center + hat_vector * ratio,
                minimum_distance_from_selected_center=-1,
            )
            distance = np.linalg.norm(direction_b_neighbor - selected_center)
            if distance < 1:
                ratio = ratio + 0.3
            else:
                break

            if ratio > 2.5:
                raise Exception("Square locator failed")
        calibration_points: dict[int, dict[int, np.ndarray]] = collections.defaultdict(dict)
        calibration_points[0][0] = selected_center
        calibration_points[1][0] = closest_neighbor
        calibration_points[0][1] = direction_b_neighbor
        return calibration_points

    def enumerate_central_square(self, centers: np.ndarray) -> None:
        p00 = self.calibration_points[0][0]
        p01 = self.calibration_points[0][1]
        p10 = self.calibration_points[1][0]
        reference_distance = np.linalg.norm(p01 - p00)
        p11_expected_position = p01 + p10 - p00
        p11, distance = self.locate_nearest_neighbor(centers, p11_expected_position)
        error_ratio = distance / reference_distance
        if error_ratio < 0.4:
            self.calibration_points[1][1] = p11
        else:
            raise Exception("enumerate_central_square failed")

    def build_examination_queue(self) -> None:
        self.points_to_examine_queue = []
        for x_key, value in self.calibration_points.items():
            for y_key, _ in value.items():
                self.points_to_examine_queue.append((x_key, y_key))

    def analyse_elements_in_queue(self, centers: np.ndarray) -> None:
        for x_index, y_index in self.points_to_examine_queue:
            self.expand_calibration_grid(centers, x_index, y_index)

    def expand_calibration_grid(self, centers: np.ndarray, x_index: int, y_index: int) -> None:
        # This rule tries to estimate the perspective distortion of four points
        # and then use this distortion model to locate new points of the
        # chessboard pattern.
        try:
            p00 = self.calibration_points[x_index][y_index]
            p01 = self.calibration_points[x_index][y_index + 1]
            p10 = self.calibration_points[x_index + 1][y_index]
            p11 = self.calibration_points[x_index + 1][y_index + 1]
        except Exception:
            return
        reference_distance: float = float(np.linalg.norm(p01 - p00))
        src = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
        dst = np.array([p00, p01, p10, p11], dtype=float)
        H, _mask = cv2.findHomography(src, dst)
        self.search_for_point(centers, x_index, y_index, reference_distance, H, (0, 2))
        self.search_for_point(centers, x_index, y_index, reference_distance, H, (1, 2))
        self.search_for_point(centers, x_index, y_index, reference_distance, H, (2, 1))
        self.search_for_point(centers, x_index, y_index, reference_distance, H, (2, 0))
        self.search_for_point(centers, x_index, y_index, reference_distance, H, (1, -1))
        self.search_for_point(centers, x_index, y_index, reference_distance, H, (0, -1))
        self.search_for_point(centers, x_index, y_index, reference_distance, H, (-1, 0))
        self.search_for_point(centers, x_index, y_index, reference_distance, H, (-1, 1))

    def search_for_point(
        self,
        centers: np.ndarray,
        x_index: int,
        y_index: int,
        reference_distance: float,
        H: np.ndarray,
        point: tuple[int, int],
    ) -> None:
        x_idx = x_index + point[0]
        y_idx = y_index + point[1]
        if y_idx not in self.calibration_points[x_idx]:
            pxx = H @ np.array([[point[0]], [point[1]], [1]])
            pxx = pxx / pxx[2]
            location, distance = self.locate_nearest_neighbor(
                centers, pxx[0:2], minimum_distance_from_selected_center=-1
            )
            if distance / reference_distance < self.distance_threshold:
                self.calibration_points[x_idx][y_idx] = location
                self.points_to_examine_queue.append((x_idx, y_idx))

    def locate_nearest_neighbor(
        self, centers: np.ndarray, selected_center: np.ndarray, minimum_distance_from_selected_center: float = 0
    ) -> tuple[np.ndarray, np.ndarray]:
        reshaped_query_array = np.array(selected_center).reshape(1, -1)
        (distances, indices) = self.centers_kdtree.query(reshaped_query_array, 2)
        if distances[0][0] <= minimum_distance_from_selected_center:
            return centers[indices[0][1]], distances[0][1]
        else:
            return centers[indices[0][0]], distances[0][0]
