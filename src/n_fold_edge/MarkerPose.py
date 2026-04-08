"""Define marker position and orientation."""


class MarkerPose:
    """Define Marker Position and Orientation."""

    def __init__(self, x: float, y: float, theta: float, quality: float, order: int | None = None) -> None:
        self.x = x
        self.y = y
        self.theta = theta
        self.quality = quality
        self.order = order

    def scale_position(self, scale_factor: float) -> None:
        self.x = self.x * scale_factor
        self.y = self.y * scale_factor
