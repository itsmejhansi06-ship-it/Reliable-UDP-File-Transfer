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


System Architecture:  
                    +--------------------+  
                   |        Client      |  
                    |--------------------|  
                    | Select File        |  
                    | Split into Chunks  |  
                    | Sliding Window     |  
                    | SHA256 Hash        |  
                    +---------+----------+  
                              |  
                              | TLS (TCP)  
                              | Secure Control Channel  
                              |  
                    +---------v----------+    
                    |        Server      |  
                    |--------------------|  
                    | Resume Info        |  
                    | Multi-client       |  
                    | Threaded Handling  |  
                    +---------+----------+  
                              ^  
                              |  
                              | UDP  
                              | Chunk Data Transfer  
                              |  
                    +---------+----------+  
                    |   File Reconstruction |    
                    |   Integrity Check    |  
                    +----------------------+  

  Communication Flow:  
  Client                         Server  
  |                               |  
  |--- TLS request (filename) --->|  
  |                               |  
  |<--- resume_from sequence -----|  
  |                               |  
  |------ UDP file chunks ------->|  
  |                               |  
  |<--------- ACK packets --------|  
  |                               |  
  |---------- END message ------->|  
  |                               |  
  |<--- SHA256 verification ------|    
  

  Protocol Design:  
  
  Control Channel (TCP + TLS)  
     Purpose:  
             Secure communication  
            Resume transfer support  

            
Data Channel (UDP)    
Packet format:   
   | Header Length | JSON Header | Payload |  
 1. Header Length (2 bytes)  
   Indicates the size of the JSON header.  
 2. JSON Header  
   Contains metadata including packet type, filename, and sequence number.  
3. Payload  
   Raw binary chunk of the file being transferred.  
   
 Example Output                                                               
 

Client:

Enter file name: test.txt                                                                 
Resume from seq: -1  
Client SHA256: 9766a8d62ab8cf2e72cc682788c77cb2a37210d8ce34c33495f818c3c8a48e8b

Server:

SSL Control Channel running...  
UDP Data Channel running...  
Finished: test.txt  
Server SHA256: 9766a8d62ab8cf2e72cc682788c77cb2a37210d8ce34c33495f818c3c8a48e8b




