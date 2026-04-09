"""Main file for N-fold-edge."""

import math
import os
import signal
from collections.abc import Iterable
from time import strftime, time
from typing import Any

import cv2
import numpy as np

from .MarkerLocator import MarkerLocator
from .MarkerPose import MarkerPose

# parameters
print_debug_messages = False
show_image = True
list_of_markers_to_find = [4, 5]
get_images_to_flush_cam_buffer = 5

# global variables
stop_flag = False


# define ctrl-c handler
def signal_handler(signal: int, frame: Any) -> None:
    """Handle signal to terminate program."""
    global stop_flag
    stop_flag = True


# install ctrl-c handler
signal.signal(signal.SIGINT, signal_handler)


def set_camera_focus() -> None:
    """Set Camera Focus."""
    # Disable autofocus
    os.system("v4l2-ctl -d 1 -c focus_auto=0")

    # Set focus to a specific value. High values for nearby objects and
    # low values for distant objects.
    os.system("v4l2-ctl -d 1 -c focus_absolute=0")

    # sharpness (int)    : min=0 max=255 step=1 default=128 value=128
    os.system("v4l2-ctl -d 1 -c sharpness=200")


class CameraDriver:
    """
    Purpose: capture images from a camera and delegate processing of the
    images to a different class.
    """

    def __init__(
        self,
        marker_orders: Iterable[int] = (6,),
        default_kernel_size: int = 21,
        scaling_parameter: float = 2500,
        downscale_factor: float = 1,
    ) -> None:
        # Initialize camera driver.
        # Open output window.
        if show_image is True:
            cv2.namedWindow("filterdemo", cv2.WINDOW_AUTOSIZE)

        # Select the camera where the images should be grabbed from.
        set_camera_focus()
        self.camera = cv2.VideoCapture(0)
        self.set_camera_resolution()

        # Storage for image processing.
        self.current_frame: np.ndarray
        self.processed_frame: np.ndarray
        self.running = True
        self.downscale_factor = downscale_factor

        # Storage for trackers.
        self.trackers: list[MarkerLocator] = []
        self.old_locations: list[MarkerPose] = []

        # Initialize trackers.
        for marker_order in marker_orders:
            temp = MarkerLocator(marker_order, default_kernel_size, scaling_parameter)
            temp.track_marker_with_missing_black_leg = False
            self.trackers.append(temp)
            self.old_locations.append(MarkerPose(0, 0, 0, 0, 0))

    def set_camera_resolution(self) -> None:
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    def get_image(self) -> None:
        # Get image from camera.
        for _ in range(get_images_to_flush_cam_buffer):
            self.current_frame = self.camera.read()[1]

    def process_frame(self) -> None:
        self.processed_frame = self.current_frame
        # Locate all markers in image.
        frame_gray = cv2.cvtColor(self.current_frame, cv2.COLOR_RGB2GRAY)
        reduced_image = cv2.resize(
            frame_gray,
            (0, 0),
            fx=1.0 / self.downscale_factor,
            fy=1.0 / self.downscale_factor,
        )
        for k in range(len(self.trackers)):
            # Previous marker location is unknown, search in the entire image.
            self.old_locations[k] = self.trackers[k].locate_marker(reduced_image)
            self.old_locations[k].scale_position(self.downscale_factor)

    def draw_detected_markers(self) -> None:
        if self.processed_frame is not None:
            for k in range(len(self.trackers)):
                xm = int(self.old_locations[k].x)
                ym = int(self.old_locations[k].y)
                orientation = self.old_locations[k].theta
                if self.old_locations[k].quality < 0.9:
                    cv2.circle(self.processed_frame, (xm, ym), 4, (55, 55, 255), 1)
                else:
                    cv2.circle(self.processed_frame, (xm, ym), 4, (55, 55, 255), 3)

                xm2 = int(xm + 50 * math.cos(orientation))
                ym2 = int(ym + 50 * math.sin(orientation))
                cv2.line(self.processed_frame, (xm, ym), (xm2, ym2), (255, 0, 0), 2)

    def show_processed_frame(self) -> None:
        if show_image is True and self.processed_frame is not None:
            cv2.imshow("filterdemo", self.processed_frame)

    def reset_all_locations(self) -> None:
        # Reset all markers locations, forcing a full search on the next iteration.
        for k in range(len(self.trackers)):
            self.old_locations[k] = MarkerPose(0, 0, 0, 0, 0)

    def handle_keyboard_events(self) -> None:
        if show_image is True:
            # Listen for keyboard events and take relevant actions.
            key = cv2.waitKey(100)
            # Discard higher order bit, http://permalink.gmane.org/gmane.comp.lib.opencv.devel/410
            key = key & 0xFF
            if key == 27:  # Esc
                self.running = False
            if key == 114:  # R
                print("Resetting")
                self.reset_all_locations()
            if key == 115:  # S
                # save image
                print("Saving image")
                filename = strftime("%Y-%m-%d %H-%M-%S")
                if self.current_frame is not None:
                    cv2.imwrite(f"output/{filename}.png", self.current_frame)

    def return_positions(self) -> list[MarkerPose]:
        # Return list of all marker locations.
        return self.old_locations


def main() -> None:
    """Main function for running n-fold-edge on video."""
    cd = CameraDriver(
        list_of_markers_to_find,
        default_kernel_size=55,
        scaling_parameter=1000,
        downscale_factor=1,
    )  # Best in robolab.
    # cd = ImageDriver(list_of_markers_to_find, defaultKernelSize = 21)
    t0 = time()

    while cd.running and stop_flag is False:
        (t1, t0) = (t0, time())
        if print_debug_messages is True:
            print("time for one iteration: %f" % (t0 - t1))
        cd.get_image()
        cd.process_frame()
        cd.draw_detected_markers()
        cd.show_processed_frame()
        cd.handle_keyboard_events()
        y = cd.return_positions()
        for k in range(len(y)):
            try:
                # pose_corrected = perspective_corrector.convertPose(y[k])
                pose_corrected = y[k]
                print(
                    f"{pose_corrected.x:8.3f} {pose_corrected.y:8.3f} {pose_corrected.theta:8.3f} {pose_corrected.quality:8.3f} {pose_corrected.order}"
                )
            except Exception as e:
                print(e)

    print("Stopping")
