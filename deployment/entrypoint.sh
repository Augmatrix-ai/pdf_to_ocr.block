#!/bin/bash
pushd /pdf_to_ocr.block 
python3 main.py
popd
exec "$@"
