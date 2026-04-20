import argparse
from pathlib import Path

import cv2
import numpy as np

from .MarkerLocator import MarkerLocator
from .MarkerTracker import MarkerTracker


def video_type(string: str) -> int | Path:
    """Determine video type for argparse."""
    try:
        return int(string)
    except ValueError:
        return Path(string)


def track_markers() -> None:
    """Function for cmd to track markers in video."""
    parser = argparse.ArgumentParser("track-markers", description="Track Markers in Video.")
    parser.add_argument(
        "video", type=video_type, help="Video on which to track markers. Or an id to capture video from."
    )
    parser.add_argument("--order", type=int, nargs="*", default=5, help="Order of Markers to Track.")
    parser.add_argument("--kernel-size", type=int, default=55, help="Kernel size to use for marker location")
    parser.add_argument("--scale-factor", type=float, default=1000, help="Scale factor to scale video by.")
    parser.add_argument("-o", "--output", type=Path, help="Location to csv file with marker location for each frame.")
    parser.add_argument("--output-video", type=Path, help="Location to save video with marker location drawn on.")
    parser.add_argument("--show", action="store_true", help="Show Video with located markers.")
    args = parser.parse_args()
    marker_locators = tuple(MarkerLocator(order, args.kernel_size, args.scale_factor) for order in args.order)
    mt = MarkerTracker(marker_locators, show_video=args.show)
    mt.track(args.video, save_video_path=args.output_video, save_csv_path=args.output)


def locate_markers() -> None:
    """Function for locating markers in image."""
    parser = argparse.ArgumentParser("locate-markers", description="Locate Markers in image.")
    parser.add_argument("image", type=Path, help="Image on which to locate markers. Or folder with images.")
    parser.add_argument("--order", type=int, nargs="*", default=5, help="Order of Markers to locate.")
    parser.add_argument("--kernel-size", type=int, default=55, help="Kernel size to use for marker location")
    parser.add_argument("--scale-factor", type=float, default=1000, help="Scale factor to scale image by.")
    parser.add_argument("-o", "--output", type=Path, help="Location to save image with markers drawn on.")
    args = parser.parse_args()
    if args.image.is_dir():
        image_files = []
        image_files.extend(args.image.glob("**/*.png"))
        image_files.extend(args.image.glob("**/*.jpg"))
        image_files.extend(args.image.glob("**/*.jpeg"))
    else:
        image_files = [args.image]
    if len(image_files) > 1 and not args.output.is_dir():
        print("When input is multiple images output must be a directory!")
        return
    for image_file in image_files:
        image = cv2.imread(image_file)
        if image is None:
            print("Image not found!")
            continue
        gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        for order in args.order:
            ml = MarkerLocator(order, args.kernel_size, args.scale_factor)
            marker_pose = ml.locate_marker(gray_image)
            print(marker_pose)
            if args.output is not None:
                xm = int(marker_pose.x)
                ym = int(marker_pose.y)
                orientation = marker_pose.theta
                if marker_pose.quality < 0.9:
                    cv2.circle(image, (xm, ym), 4, (55, 55, 255), 1)
                else:
                    cv2.circle(image, (xm, ym), 4, (55, 55, 255), 3)
                xm2 = int(xm + 50 * np.cos(orientation))
                ym2 = int(ym + 50 * np.sin(orientation))
                cv2.line(image, (xm, ym), (xm2, ym2), (255, 0, 0), 2)
        if args.output is not None:
            if args.output.is_dir():
                out_file = args.output.joinpath(image_file.name)
            else:
                out_file = args.output
            cv2.imwrite(out_file, image)
