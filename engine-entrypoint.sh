#!/bin/bash
pushd /ModuleEngine 
python3 http2_service.py
popd
exec "$@"
