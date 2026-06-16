"""Define marker position and orientation."""


class MarkerPose:
    """
    Define Marker Position and Orientation.

    Parameters
    ----------
    x : float
        X coordinate of marker position.
    y : float
        y coordinate of marker position.
    theta : float
        Orientation of marker.
    quality : float
        The quality score of the marker.
    order : int
        The Order type of the marker.
    """

    def __init__(self, x: float, y: float, theta: float, quality: float, order: int) -> None:
        self.x = x
        self.y = y
        self.theta = theta
        self.quality = quality
        self.order = order

    def scale_position(self, scale_factor: float) -> None:
        """Scale the marker position by a scale factor."""
        self.x = self.x * scale_factor
        self.y = self.y * scale_factor

    def __str__(self) -> str:
        """Return string representation."""
        return f"x: {self.x:.2f}, y: {self.y:.2f}, theta: {self.theta:.2f}, quality: {self.quality:.2f}, order: {self.order:.2f}"

    def as_list(self) -> list[float | int]:
        """
        Return a list representation.

        Returns
        -------
        x : float
        y : float
        theta : float
        quality : float
        order : int
        """
        return [self.x, self.y, self.theta, self.quality, self.order]
