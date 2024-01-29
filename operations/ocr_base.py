import os
import sys

from .boundingbox import BoundingBox

from abc import ABC, abstractmethod
from . import PAGE_LEVEL, WORD_LEVEL, NO_LEVEL
from . import OCR_VERTICAL_DIRECTION, OCR_HORIZONTAL_DIRECTION
import functools


class TextInfo:
    # Refer - https://stackoverflow.com/questions/472000/usage-of-slots
    __slots__ = [
        "text",
        "level",
        "text_direction",
        "position",
        "block_num",
        "par_num",
        "line_num",
        "word_num",
        "angle",
        "block_cord",
        "para_cord",
        "line_cord",
        "word_cord",
        "is_normalized",
    ]

    def __init__(
        self,
        text="",
        position=None,
        level=NO_LEVEL,
        text_direction=OCR_HORIZONTAL_DIRECTION,
        block_num=-1,
        par_num=-1,
        line_num=-1,
        word_num=-1,
        word_cord=[],
        angle=0,
        para_cord=[],
        block_cord=[],
        line_cord=[],
    ):
        """
        Co-ordinate/<block/para/word/line>_cord in [[top, left], [top, right], [bottom, right], [bottom, left]]
        BoundingBox - type(Postion(top, left, bottom, right))

        # Structure of ocr data
        # - Block/Paragraph - 1...n
        #   -   Line - 1...n
        #       -   Word - 1...n
        #   -   Line
        #       -   word - 1...n
        # RawLine - 1...n

        """
        self.text = text
        self.position = position
        self.level = level
        self.text_direction = text_direction

        self.block_num = block_num
        self.par_num = par_num
        self.line_num = line_num
        self.word_num = word_num
        self.angle = angle

        self.block_cord = block_cord
        self.para_cord = para_cord
        self.line_cord = line_cord
        self.word_cord = word_cord
        self.is_normalized = False

    def __getitem__(self, key):
        return self.__dict__.get(key)

    def normalize(self, width, height):
        out = self.__dict__.copy()
        out.update(
            {
                "position": BoundingBox(
                    self.position.top / float(height),
                    self.position.left / float(width),
                    self.position.height / float(height),
                    self.position.width / float(width),
                ),
                "block_cord": [
                    [cord[0] / float(height), cord[1] / float(width)]
                    for cord in self.block_cord
                ],
                "para_cord": [
                    [cord[0] / float(height), cord[1] / float(width)]
                    for cord in self.para_cord
                ],
                "word_cord": [
                    [cord[0] / float(height), cord[1] / float(width)]
                    for cord in self.word_cord
                ],
                "line_cord": [
                    [cord[0] / float(height), cord[1] / float(width)]
                    for cord in self.line_cord
                ],
            }
        )

        out.pop("top")
        out.pop("left")
        out.pop("width")
        out.pop("height")

        return TextInfo(**out)

    @property
    def __dict__(self):
        if self.level == PAGE_LEVEL:
            return {
                "level": self.level,
                "text": self.text,
                "width": self.position.width,
                "height": self.position.height,
                "angle": self.angle,
                "is_normalized": self.is_normalized,
            }

        return {
            "level": self.level,
            "text": self.text,
            "top": self.position.top,
            "left": self.position.left,
            "width": self.position.width,
            "height": self.position.height,
            "block_num": self.block_num,
            "par_num": self.par_num,
            "line_num": self.line_num,
            "word_num": self.word_num,
            "angle": self.angle,
            "para_cord": self.para_cord,
            "block_cord": self.block_cord,
            "line_cord": self.line_cord,
            "word_cord": self.word_cord,
            "text_direction": "h"
            if self.text_direction == OCR_HORIZONTAL_DIRECTION
            else "v",
        }


class OCRBase(ABC):
    def __init__(self):
        self._ocrinfo = []

    def add(self, textinfo):
        """
        set textinfo into ocrinfo

        Parameters:
            textinfo : Object from TextInfo
        """
        self._ocrinfo.append(textinfo)

    def sort_cord(self, v1, v2):
        SMALL_PIX_THREH_ALLOWED = 8
        if abs(v1["top"] - v2["top"]) <= SMALL_PIX_THREH_ALLOWED:
            return v1["left"] - v2["left"]
        return v1["top"] - v2["top"]

    @property
    def ocrinfo(self, is_normalized=False):
        if len(self._ocrinfo) == 0:
            raise ValueError("Please set ocrinfo or call add to insert textinfo object")

        # We can assume that first record belongs to level=PAGE_LEVEL, contains size of image/page
        page_level_record = self._ocrinfo[0].__dict__
        ocrinfo_out = [page_level_record]

        for text_info in sorted(
            self._ocrinfo[1:], key=functools.cmp_to_key(self.sort_cord)
        ):
            if is_normalized:
                page_level_record["is_normalized"] = True
                text_info = text_info.normalize(
                    width=self._ocrinfo[0]["width"], height=self._ocrinfo[0]["height"]
                )
            ocrinfo_out.append(text_info.__dict__)

        return ocrinfo_out

    @property
    def raw_text(self):
        if len(self._ocrinfo) == 0:
            raise ValueError("Please set ocrinfo or call add to insert textinfo object")
        return self._ocrinfo[0]["text"]

    @abstractmethod
    def perform(self, data_byte):
        """
        data_byte: type(io.ByteIO) can be image or single page pdf
        """
        pass

    def load(ocrinfo):
        self._ocrinfo = []
        for textinfo in ocrinfo:
            textinfo_obj = TextInfo(**textinfo)
            self._ocrinfo.append(textinfo_obj)
