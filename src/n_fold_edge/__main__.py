"""CLI for running marker locator and tracker."""

import argparse
import csv
from pathlib import Path

import cv2
import numpy as np

from n_fold_edge.checkerboard import CheckerBoard
from n_fold_edge.marker_locator import MarkerLocator
from n_fold_edge.marker_tracker import MarkerTracker


def video_type(string: str) -> int | Path:
    """Determine video type for argparse."""
    try:
        return int(string)
    except ValueError:
        return Path(string)


def get_track_markers_arg_parser() -> argparse.ArgumentParser:
    """Get arg parser for track markers."""
    parser = argparse.ArgumentParser("track-markers", description="Track Markers in Video.")
    parser.add_argument(
        "video", type=video_type, help="Video on which to track markers. Or an id to capture video from."
    )
    parser.add_argument("--order", type=int, nargs="*", default=[5], help="Order of Markers to Track.")
    parser.add_argument("--kernel-size", type=int, default=55, help="Kernel size to use for marker location")
    parser.add_argument("--scale-factor", type=float, default=1000, help="Scale factor to scale video by.")
    parser.add_argument("-o", "--output", type=Path, help="Location to csv file with marker location for each frame.")
    parser.add_argument(
        "--output-video", type=Path, help="Location to save video with marker location drawn on. Good for debugging."
    )
    parser.add_argument("--show", action="store_true", help="Show Video with located markers.")
    return parser


def track_markers() -> None:
    """Function for CLI to track markers in video."""
    parser = get_track_markers_arg_parser()
    args = parser.parse_args()
    marker_locators = tuple(MarkerLocator(order, args.kernel_size, args.scale_factor) for order in args.order)
    mt = MarkerTracker(marker_locators, show_video=args.show)
    mt.track(args.video, save_video_path=args.output_video, save_csv_path=args.output)


def get_locate_markers_arg_parser() -> argparse.ArgumentParser:
    """Get arg parser for locate markers."""
    parser = argparse.ArgumentParser("locate-markers", description="Locate Markers in image.")
    parser.add_argument("image", type=Path, help="Image on which to locate markers. Or folder with images.")
    parser.add_argument("--order", type=int, nargs="*", default=[5], help="Order of Markers to locate.")
    parser.add_argument("--kernel-size", type=int, default=55, help="Kernel size to use for marker location")
    parser.add_argument("--scale-factor", type=float, default=1000, help="Scale factor to scale image by.")
    parser.add_argument(
        "-o", "--output", type=Path, help="Location to save csv file with marker location for each image."
    )
    parser.add_argument(
        "--output-image", type=Path, help="Location to save image with markers drawn on. Good for debugging."
    )
    return parser


def locate_markers() -> None:
    """Function for CLI to locating markers in image."""
    parser = get_locate_markers_arg_parser()
    args = parser.parse_args()
    if args.image.is_dir():
        image_files = []
        image_files.extend(args.image.glob("**/*.png"))
        image_files.extend(args.image.glob("**/*.jpg"))
        image_files.extend(args.image.glob("**/*.jpeg"))
    else:
        image_files = [args.image]
    if len(image_files) > 1 and args.output_image is not None and not args.output_image.is_dir():
        print("When input is multiple images output must be a directory!")
        return
    if args.output is not None:
        if args.output.exists():
            raise FileExistsError("csv file already exist. Choose another filename.")
        with open(args.output, "a") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Image", "x", "y", "direction", "quality", "order"])
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
                with open(args.output, "a") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow([image_file] + marker_pose.as_list())
            if args.output_image is not None:
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
        if args.output_image is not None:
            if args.output_image.is_dir():
                out_file = args.output_image.joinpath(image_file.name)
            else:
                out_file = args.output_image
            cv2.imwrite(out_file, image)


def get_checkerboard_arg_parser() -> argparse.ArgumentParser:
    """Get arg parser for locate markers."""
    parser = argparse.ArgumentParser("checkerboard", description="Locate All corners of a checkerboard in image.")
    parser.add_argument("image", type=Path, help="Image on which to locate markers. Or folder with images.")
    parser.add_argument("--kernel-size", type=int, default=101, help="Kernel size to use for marker location")
    parser.add_argument("--scale-factor", type=float, default=40, help="Scale factor to scale image by.")
    parser.add_argument("--distance-scale", type=float, default=40, help="Distance scale of the checkerboard pattern.")
    parser.add_argument(
        "--threshold-level", type=float, default=0.5, help="Threshold level to apply for individual corners."
    )
    parser.add_argument(
        "-o", "--output", type=Path, help="Location to save csv file with checkerboard corner location for each image."
    )
    parser.add_argument(
        "--output-image", type=Path, help="Location to save image with markers drawn on. Good for debugging."
    )
    return parser


def get_checkerboard() -> None:
    """Function for CLI to locating markers in image."""
    parser = get_checkerboard_arg_parser()
    args = parser.parse_args()
    if args.image.is_dir():
        image_files = []
        image_files.extend(args.image.glob("**/*.png"))
        image_files.extend(args.image.glob("**/*.jpg"))
        image_files.extend(args.image.glob("**/*.jpeg"))
    else:
        image_files = [args.image]
    if len(image_files) > 1 and args.output_image is not None and not args.output_image.is_dir():
        print("When input is multiple images output must be a directory!")
        return
    if args.output is not None:
        if args.output.exists():
            raise FileExistsError("csv file already exist. Choose another filename.")
        with open(args.output, "a") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Image", "image x", "image y", "object x", "object y"])
    cb = CheckerBoard(args.kernel_size, args.scale_factor, args.distance_scale, args.threshold_level)
    for image_file in image_files:
        image = cv2.imread(image_file)
        if image is None:
            print("Image not found!")
            continue
        img_points, obj_points = cb.find_corners(image)
        if args.output is not None:
            with open(args.output, "a") as csv_file:
                writer = csv.writer(csv_file)
                for img_point, obj_point in zip(img_points, obj_points, strict=True):
                    writer.writerow([image_file] + img_point.tolist() + obj_point[:2].tolist())
        if args.output_image is not None:
            for x, y in img_points:
                xm = int(x)
                ym = int(y)
                cv2.circle(image, (xm, ym), 10, (55, 55, 255), 3)
        if args.output_image is not None:
            if args.output_image.is_dir():
                out_file = args.output_image.joinpath(image_file.name)
            else:
                out_file = args.output_image
            cv2.imwrite(out_file, image)
