from typing import Dict, Union
from operations import digitized_pdf_ocr
from http2_service_runner import ServerManager, ServiceRunner
from ocr_struct import Outputs, OCRElement
import msgpack

class OCRTask(ServiceRunner):
    def __init__(self, logger: object) -> None:
        """
        Initialize OCR Task object.

        Parameters:
        logger (object): A logger object to log messages and errors.
        """
        self.logger = logger
        super().__init__()

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

#        new_ocrinfo = []
#        for ocr_elm in ocr_engine.ocrinfo:
#            new_ocrinfo.append(OCRElement(**ocr_elm))

        return {"ocr_json": ocr_json, "raw_text": raw_text}

if __name__ == "__main__":
    ServerManager(OCRTask(logger=None)).start(
        host="0.0.0.0",
        port=80,
#        private_key="certificates/private.pem",
 #       cert_key="certificates/cert.pem"
    )
