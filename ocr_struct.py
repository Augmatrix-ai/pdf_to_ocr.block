from typing import Dict, List, Union
from dataclasses import dataclass
from augmatrix.block_service.data_context import AugmatrixDataType

# @dataclass
# class OCRElement(AugmatrixDataType):
#     level: int
#     text: str
#     width: float
#     height: float
#     top: Union[float, None] = None
#     left: Union[float, None] = None
#     block_num: Union[float, None] = None
#     par_num: Union[float, None] = None
#     line_num: Union[float, None] = None
#     word_num: Union[float, None] = None
#     angle: Union[float, None] = None
#     para_cord: Union[List[List[float]], None] = None
#     block_cord: Union[List[List[float]], None] = None
#     line_cord: Union[List[List[float]], None] = None
#     word_cord: Union[List[List[float]], None] = None
#     text_direction: Union[bool, None] = None
#     is_normalized: Union[bool, None] = None


@dataclass
class Inputs(AugmatrixDataType):
    pdf: bytes

@dataclass
class Outputs(AugmatrixDataType):
    ocr_json: str
    raw_text: str