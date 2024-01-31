from augmatrix.block_service.data_context import encode, decode 
from augmatrix.datasets import variable_def_to_dataclass
from hyper import HTTPConnection
import ssl
import msgpack
import bson
import json


def send_request(connection, url, data, method='POST', content_type='application/msgpack'):
    """
    Send data to the Twisted HTTP/2 server using MessagePack as the content type.
    """
    connection.request(method, url, body=data, headers={'content-type': content_type})
    response = connection.get_response()
    return response.read()

def main():

    # Specify the server's hostname and port
    host = 'localhost'
    port = 8083
    # Set up the SSL context (assuming your server uses SSL)
    # ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # ssl_context.load_cert_chain(certfile="certificates/cert.pem", keyfile="certificates/private.pem", password=None)
    # Create an HTTP/2 connection using hyper
    connection = HTTPConnection(host, port, secure=False, ssl_context=None)

    inputs = None
    with open("testdata/single_pdf.pdf", "rb") as fr, open("structure.json", "r") as fr_struct:
        structure = json.loads(fr_struct.read())
        func_args_dataclass = variable_def_to_dataclass(structure['func_args_schema'], 'FunctionArugments')
        inputs_dataclass = variable_def_to_dataclass(structure['inputs_schema'], 'Inputs')
        outputs_dataclass = variable_def_to_dataclass(structure['outputs_schema'], 'Outputs')

        inputs = inputs_dataclass(pdf=fr.read())
        func_arguments = func_args_dataclass(properties=json.dumps(structure['block_properties']), credentials=json.dumps({}))

        func_args_data = encode(func_arguments)
        inputs_data = encode(inputs)
        data_dict = {'func_args': func_args_data, 'inputs': inputs_data}

        b_data = bson.dumps(data_dict)

        # Send data to the server and process the response
        response_data = send_request(connection, '/', data=b_data)

        outputs = decode(response_data, outputs_dataclass)

        print(outputs.ocr_json)
        print(outputs.raw_text)

if __name__ == "__main__":
    main()
