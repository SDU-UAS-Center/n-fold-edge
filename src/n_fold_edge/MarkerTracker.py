"""Main file for N-fold-edge."""

import csv
import math
import signal
from collections.abc import Sequence
from pathlib import Path
from time import strftime
from typing import Any

import cv2
import numpy as np

from .MarkerLocator import MarkerLocator
from .MarkerPose import MarkerPose


class MarkerTracker:
    """Track markers in video file or video stream."""

    def __init__(self, marker_locators: MarkerLocator | Sequence[MarkerLocator], show_video: bool = False) -> None:
        if isinstance(marker_locators, Sequence):
            self.marker_locators = marker_locators
        else:
            self.marker_locators = (marker_locators,)
        self.show_video = show_video
        self.stop_flag = False
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signal: int, frame: Any) -> None:
        self.stop_flag = True

    def handle_keyboard_events(self, frame: np.ndarray) -> bool:
        if self.stop_flag:
            return True
        if self.show_video is True:
            # Listen for keyboard events and take relevant actions.
            key = cv2.waitKey(1)
            # Discard higher order bit, http://permalink.gmane.org/gmane.comp.lib.opencv.devel/410
            key = key & 0xFF
            if key == 27 or key == 113:  # Esc/q
                return True
            elif key == 115:  # S
                # save image
                print("Saving image")
                filename = strftime("%Y-%m-%d %H-%M-%S")
                cv2.imwrite(f"output/{filename}.png", frame)
        return False

    def draw_detected_markers(self, frame: np.ndarray, marker_pose: MarkerPose) -> np.ndarray:
        xm = int(marker_pose.x)
        ym = int(marker_pose.y)
        orientation = marker_pose.theta
        if marker_pose.quality < 0.9:
            cv2.circle(frame, (xm, ym), 4, (55, 55, 255), 1)
        else:
            cv2.circle(frame, (xm, ym), 4, (55, 55, 255), 3)
        xm2 = int(xm + 50 * math.cos(orientation))
        ym2 = int(ym + 50 * math.sin(orientation))
        cv2.line(frame, (xm, ym), (xm2, ym2), (255, 0, 0), 2)
        return frame

    def prepare_csv_file(self, csv_file_path: Path) -> None:
        if csv_file_path.exists():
            raise FileExistsError("csv file already exist. Choose another filename.")
        with open(csv_file_path, "a") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Frame", "x", "y", "direction", "quality", "order"])

    def save_marker_to_csv(self, csv_file_path: Path, marker_pose: MarkerPose, frame_number: float) -> None:
        with open(csv_file_path, "a") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([frame_number] + marker_pose.as_list())

    def track(self, video: Path | int, save_video_path: Path | None = None, save_csv_path: Path | None = None) -> None:
        cap = cv2.VideoCapture(video)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        if save_csv_path is not None:
            self.prepare_csv_file(save_csv_path)
        if save_video_path is not None:
            if isinstance(video, int):
                fourcc = cv2.VideoWriter.fourcc(*"DIVX")
                if save_video_path.suffix != ".avi":
                    raise OSError("Only video with avi extension is supported as output.")
            else:
                fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            video_out = cv2.VideoWriter(save_video_path, fourcc, fps, (frame_width, frame_height))
        else:
            video_out = None
        if not cap.isOpened():
            raise OSError(f"Could not open video {video}.")
        internal_frame_number = 0
        if self.show_video:
            cv2.namedWindow("Marker Tracker", cv2.WINDOW_AUTOSIZE)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            for ml in self.marker_locators:
                marker_pose = ml.locate_marker(frame_gray)
                frame = self.draw_detected_markers(frame, marker_pose)
                if save_csv_path is not None:
                    frame_number = cap.get(cv2.CAP_PROP_POS_FRAMES)
                    if frame_number < 0:
                        frame_number = internal_frame_number
                    self.save_marker_to_csv(save_csv_path, marker_pose, frame_number)
            if self.show_video:
                cv2.imshow("Marker Tracker", frame)
            if video_out is not None:
                video_out.write(frame)
            stop = self.handle_keyboard_events(frame)
            if stop:
                break
            internal_frame_number += 1
        if video_out is not None:
            video_out.release()
        cap.release()
        cv2.destroyAllWindows()
