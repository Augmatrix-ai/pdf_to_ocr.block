import sys, os
import io
from .dict_to_object import DictToObject
from .ocr_base import OCRBase, TextInfo

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import (
    LAParams,
    LTChar,
    LTTextLineHorizontal,
    LTTextLineVertical,
    LTImage,
    LTLine,
    LTTextBox,
    LTTextLine,
    LTText,
    LTTextContainer,
    LTAnno,
)
from . import PAGE_LEVEL, WORD_LEVEL, NO_LEVEL
from . import OCR_VERTICAL_DIRECTION, OCR_HORIZONTAL_DIRECTION

from .boundingbox import BoundingBox


def get_page_layout(
    data_byte,
    line_overlap=0.5,
    char_margin=0.6,
    line_margin=0.5,
    word_margin=0.1,
    boxes_flow=0.5,
    detect_vertical=True,
    all_texts=True,
):
    """Returns a PDFMiner LTPage object and page dimension of a single
    page pdf. To get the definitions of kwargs, see
    https://pdfminersix.rtfd.io/en/latest/reference/composable.html.

    Parameters
    ----------
    data_byte : type(io.ByteIO)
        Path to pdf file.
    line_overlap : float
    char_margin : float
    line_margin : float
    word_margin : float
    boxes_flow : float
    detect_vertical : bool
    all_texts : bool

    Returns
    -------
    layout : object
        PDFMiner LTPage object.
    dim : tuple
        Dimension of pdf page in the form (width, height).

    """
    buf = io.BytesIO()
    buf.write(data_byte)
    buf.seek(0)

    parser = PDFParser(buf)
    document = PDFDocument(parser)
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed(f"Text extraction is not allowed")
    laparams = LAParams(
        line_overlap=line_overlap,
        char_margin=char_margin,
        line_margin=line_margin,
        word_margin=word_margin,
        boxes_flow=boxes_flow,
        detect_vertical=detect_vertical,
        all_texts=all_texts,
    )
    rsrcmgr = PDFResourceManager()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.create_pages(document):
        interpreter.process_page(page)
        layout = device.get_result()
        width = layout.bbox[2]
        height = layout.bbox[3]
        dim = (width, height)
    return page, layout, dim


def get_pdfminer_objects(layout, ltype):
    """Recursively parses pdf layout to get a list of
    PDFMiner text objects.

    Parameters
    ----------
    layout : object
        PDFMiner LTPage object.
    ltype : string
        Specify 'char', 'lh', 'lv' to get LTChar, LTTextLineHorizontal,
        and LTTextLineVertical objects respectively.
    t : list

    Returns
    -------
    t : list
        List of PDFMiner text objects.

    """
    res = []

    def _get_pdfminer_objects(layout, ltype, res=None):
        if ltype == "char":
            LTObject = LTChar
        elif ltype == "image":
            LTObject = LTImage
        elif ltype == "horizontal_text":
            LTObject = LTTextLineHorizontal
        elif ltype == "vertical_text":
            LTObject = LTTextLineVertical
        elif ltype == "line_text":
            LTObject = LTTextLine
        elif ltype == "line":
            LTObject = LTLine
        elif ltype == "text":
            LTObject = LTText
        elif ltype == "block_text":
            LTObject = LTTextBox

        try:
            for obj in layout._objs:
                if isinstance(obj, LTObject):
                    res.append(obj)
                else:
                    _get_pdfminer_objects(obj, ltype, res)
        except AttributeError:
            pass
        return res

    return _get_pdfminer_objects(layout, ltype, res=res)


class DigitizedPDFOCR(OCRBase):
    def __init__(self):
        OCRBase.__init__(self)

    def convert_to_ocrinfo(self, response):
        # First is the page level
        text_info = TextInfo(
            response["full_text"],
            position=BoundingBox(0, 0, response["page_height"], response["page_width"]),
            level=PAGE_LEVEL,
            block_num=-1,
            par_num=-1,
            line_num=-1,
            word_num=-1,
            angle=response["page_rotate"],
            para_cord=[],
            block_cord=[],
            line_cord=[],
            word_cord=[],
        )
        self.add(text_info)

        for paragraph in response["paragraph_lst"]:
            para_top = response["page_height"] - paragraph["obj"].y1
            para_left = paragraph["obj"].x0
            para_bottom = response["page_height"] - paragraph["obj"].y0
            para_right = paragraph["obj"].x1

            para_cord = [
                [para_top, para_left],
                [para_top, para_right],
                [para_bottom, para_right],
                [para_bottom, para_left],
            ]

            for line in paragraph["line_lst"]:
                line_top = response["page_height"] - line["obj"].y1
                line_left = line["obj"].x0
                line_bottom = response["page_height"] - line["obj"].y0
                line_right = line["obj"].x1

                line_cord = [
                    [line_top, line_left],
                    [line_top, line_right],
                    [line_bottom, line_right],
                    [line_bottom, line_left],
                ]
                for widx, word in enumerate(line["word_lst"]):
                    # x0 - Distance of left side of character from left side of page.
                    # x1 - Distance of right side of character from left side of page.
                    # y0 - Distance of bottom of character from bottom of page.
                    # y1 - Distance of top of character from bottom of page.
                    # Note - BoundingBox is based on top, left as (0, 0), but here it is based on bottom, left as (0, 0)
                    # Hence substract page height - y0 or y1

                    # Also (x0, y0) is (left, bottom) and (x1, y1) is (right, left)
                    # hence change to (x0, y1) as (left, top) and (x1, y0) as (right, bottom)
                    top = response["page_height"] - min([c_obj.y1 for c_obj in word])
                    left = min([c_obj.x0 for c_obj in word])

                    bottom = response["page_height"] - max([c_obj.y0 for c_obj in word])
                    right = max([c_obj.x1 for c_obj in word])

                    word_cord = [
                        [top, left],
                        [top, right],
                        [bottom, right],
                        [bottom, left],
                    ]

                    text_info = TextInfo(
                        "".join([c_obj._text for c_obj in word]),
                        position=BoundingBox(top, left, bottom, right),
                        level=WORD_LEVEL,
                        block_num=1,
                        par_num=paragraph["paragraph_num"],
                        line_num=line["line_num"],
                        word_num=widx + 1,
                        angle=response["page_rotate"],
                        word_cord=word_cord,
                        para_cord=para_cord,
                        block_cord=para_cord,
                        line_cord=line_cord,
                        text_direction=line["text_direction"],
                    )
                    self.add(text_info)

    def perform(self, data_byte):
        pdf_page, layout, dim = get_page_layout(data_byte)

        block_text_obj_lst = get_pdfminer_objects(layout, "block_text")

        full_text = ""
        response = {}
        paragraph_lst = []
        for bidx, block_text in enumerate(block_text_obj_lst):
            line_lst = []
            for lidx, line_obj in enumerate(block_text._objs):
                word_lst = []
                char_lst = []
                for char_obj in line_obj._objs:
                    if (char_obj._text == " " or isinstance(char_obj, LTAnno)) and len(
                        char_lst
                    ) != 0:
                        word_lst.append(char_lst)
                        char_lst = []
                    elif not isinstance(char_obj, LTAnno):
                        char_lst.append(char_obj)

                    full_text += char_obj._text

                if len(char_lst) != 0:
                    word_lst.append(char_lst)

                if isinstance(line_obj, LTTextLineVertical):
                    line_lst.append(
                        {
                            "word_lst": word_lst,
                            "text_direction": OCR_VERTICAL_DIRECTION,
                            "line_num": lidx + 1,
                            "obj": line_obj,
                        }
                    )
                elif isinstance(line_obj, LTTextLineHorizontal):
                    line_lst.append(
                        {
                            "word_lst": word_lst,
                            "text_direction": OCR_HORIZONTAL_DIRECTION,
                            "line_num": lidx + 1,
                            "obj": line_obj,
                        }
                    )

            paragraph_lst.append(
                {"line_lst": line_lst, "paragraph_num": bidx + 1, "obj": block_text}
            )

        _, _, page_width, page_height = pdf_page.mediabox
        response["page_width"] = page_width
        response["page_height"] = page_height
        response["page_rotate"] = pdf_page.rotate
        response["paragraph_lst"] = paragraph_lst
        response["full_text"] = full_text

        self.convert_to_ocrinfo(response)
