from typing import Dict, Union
from ocr_struct import Inputs, Outputs
from augmatrix.block_service.data_context import encode, decode, FunctionArguments
from operations import digitized_pdf_ocr
from augmatrix.block_service.service_runner import ServerManager, ServiceRunner
import msgpack

class OCRTask(ServiceRunner):
    def __init__(self, logger: object) -> None:
        """
        Initialize OCR Task object.

        Parameters:
        logger (object): A logger object to log messages and errors.
        """
        self.logger = logger
        super().__init__(Inputs, Outputs, FunctionArguments)

    def run(self, pdf: bytes) -> Dict:
        """
        Perform OCR on a PDF.

        Parameters:
        pdf (bytes): A bytes object containing the input PDF data.

        Returns:
        Dict: A dictionary containing the OCR results.
            The keys are "ocr_json" and "raw_text", and the values are the OCR data (List[OCRElement]) and raw text (str),
            respectively.
        """
        ocr_engine = digitized_pdf_ocr.DigitizedPDFOCR()
        ocr_engine.perform(pdf)
        ocr_json = ocr_engine.ocrinfo
        raw_text = ocr_engine.raw_text

        return {"ocr_json": ocr_json, "raw_text": raw_text}

if __name__ == "__main__":
    ServerManager(OCRTask(logger=None)).start(
        host="localhost",
        port=8083,
        # private_key="certificates/private.pem",
        # cert_key="certificates/cert.pem"
    )
