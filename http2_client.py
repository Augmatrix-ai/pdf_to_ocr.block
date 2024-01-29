from ocr_struct import encode, decode, FunctionArguments, Inputs, Outputs
from hyper import HTTPConnection
import ssl
import msgpack
import bson

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
    port = 8089

    # Set up the SSL context (assuming your server uses SSL)
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile="certificates/cert.pem", keyfile="certificates/private.pem", password=None)

    # Create an HTTP/2 connection using hyper
    connection = HTTPConnection(host, port, secure=True, ssl_context=ssl_context)

    inputs = None
    with open("testdata/single_pdf.pdf", "rb") as fr:
        inputs = Inputs(pdf=fr.read())
    
    func_arguments = FunctionArguments(credentials={}, properties={})

    func_args_data = encode(func_arguments)
    inputs_data = encode(inputs)
    data_dict = {'func_args': func_args_data, 'inputs': inputs_data}
    b_data = bson.dumps(data_dict)

    # Send data to the server and process the response
    response_data = send_request(connection, '/', data=b_data)

    outputs = decode(response_data, Outputs)

    print(outputs.ocr_json)
    print(outputs.raw_text)

if __name__ == "__main__":
    main()
