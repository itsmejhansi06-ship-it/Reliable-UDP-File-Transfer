# Reliable File Transfer Protocol (Custom FTP)

Secure UDP-based resumable file transfer.

## Features
- Custom reliable UDP protocol
- SSL/TLS secure control channel
- Multi-client threaded server
- Resume interrupted transfers
- Sliding window throughput optimization
- SHA256 integrity check

## Requirements
Python 3.x

Generate SSL cert:
openssl req -new -x509 -days 365 -nodes -out server.crt -keyout server.key

## Run
Start server:
python server.py

Run client:
python client.py
