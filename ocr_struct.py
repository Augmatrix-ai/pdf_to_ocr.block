from typing import Dict, List, Union
from dataclasses import dataclass
import msgpack
import zlib

class AugmatrixDataType:
    def to_dict(self):
        # Get all attributes of the object
        obj_attributes = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]

        # Create a dictionary to store the attributes and their values
        obj_dict = {}
        for attr in obj_attributes:
            obj_dict[attr] = getattr(self, attr)

        return obj_dict

@dataclass
class OCRElement(AugmatrixDataType):
    level: int
    text: str
    width: float
    height: float
    top: Union[float, None] = None
    left: Union[float, None] = None
    block_num: Union[float, None] = None
    par_num: Union[float, None] = None
    line_num: Union[float, None] = None
    word_num: Union[float, None] = None
    angle: Union[float, None] = None
    para_cord: Union[List[List[float]], None] = None
    block_cord: Union[List[List[float]], None] = None
    line_cord: Union[List[List[float]], None] = None
    word_cord: Union[List[List[float]], None] = None
    text_direction: Union[bool, None] = None
    is_normalized: Union[bool, None] = None

@dataclass
class FunctionArguments(AugmatrixDataType):
    credentials: Dict[str, str]
    properties: Dict[str, str]

    def to_dict(self):
        # Get all attributes of the object
        obj_attributes = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]

        # Create a dictionary to store the attributes and their values
        obj_dict = {}
        for attr in obj_attributes:
            obj_dict[attr] = getattr(self, attr)

        return obj_dict

@dataclass
class Inputs(AugmatrixDataType):
    pdf: bytes

@dataclass
class Outputs(AugmatrixDataType):
    ocr_json: List[OCRElement]
    raw_text: str

def encode(obj):
    # Serialize the object to MessagePack
    msgpack_data = msgpack.packb(obj, default=lambda x: x.__dict__, use_bin_type=True)
    
    # Compress the MessagePack data using zlib
    compressed_data = zlib.compress(msgpack_data)

    return compressed_data

def decode(data, cls):
    # Decompress the compressed data using zlib
    decompressed_data = zlib.decompress(data)

    # Deserialize the decompressed data from MessagePack
    if isinstance(decompressed_data, bytes):
        decompressed_data = msgpack.unpackb(decompressed_data, raw=False)
    
    # Get the dictionary keys from the class's attributes
    cls_attributes = cls.__annotations__.keys()

    # Create a dictionary containing only the relevant keys and values
    obj_data = {key: decompressed_data[key] for key in cls_attributes if key in decompressed_data}

    # Instantiate the class with the extracted data
    return cls(**obj_data)