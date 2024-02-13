from augmatrix.block_service.client_runner import ClientRunner

def main():
    # Initialize the client with the server's URL
    client = ClientRunner(url='http://localhost:8083/')

    # Load the PDF file and specify properties and credentials
    with open("testdata/single_pdf.pdf", "rb") as fr:
        inputs = {
            "pdf": fr.read()
        }
        properties = {
            "selected_ocr_type": {
                "ocr_name": "Digital PDF OCR",
                "ocr_id": "digitized_pdf_ocr"
            }
        }
        credentials = {}

        # Call the function with the specified inputs, properties, and credentials
        outputs = client.call_function(
            structure="structure.json",
            func_args=properties,
            inputs=inputs,
            credentials=credentials
        )

        print(outputs)

if __name__ == "__main__":
    main()
