import os, sys

class BoundingBox:
    def __init__(self, top, left, bottom, right):
        """
        BoundingBox is based on
        top and left of file as (0, 0)
        bottom, right of file as (width, and height)
        """
        self.top = top
        self.left = left
        self.bottom = bottom
        self.right = right

    def __iter__(self):
        return [(self.top, self.left), (self.bottom, self.right)]

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.bottom - self.top

    def merge(self, boundingbox):
        if not isinstance(boundingbox, BoundingBox):
            raise ValueError(
                f"Argument must be a instance of BoundingBox but given {boundingbox}"
            )

        return BoundingBox(
            top=min(boundingbox.top, self.top),
            left=min(boundingbox.left, self.left),
            bottom=max(boundingbox.bottom, self.bottom),
            right=max(boundingbox.right, self.right),
        )
