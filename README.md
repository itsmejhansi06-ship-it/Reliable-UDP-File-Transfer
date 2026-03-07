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
```                 
+----------------------+
|        Client        |
|----------------------|
| Select File          |
| Split into Chunks    |
| Sliding Window       |
| SHA256 Hash          |
+----------+-----------+
           |
           | TLS (TCP)
           | Secure Control Channel
           |
+----------v-----------+
|        Server        |
|----------------------|
| Resume Info          |
| Multi-client         |
| Threaded Handling    |
+----------+-----------+
           ^
           |
           | UDP
           | Chunk Data Transfer
           |
+----------+-----------+
|  File Reconstruction |
|  Integrity Check     |
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
  
```
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



Performance Evaluation           
The system was tested in a real network environment using two laptops connected to the same WiFi network.           
```
| Component      | Specification                           |
| -------------- | --------------------------------------- |
| Client Machine | Windows 11, Python 3.x                  |
| Server Machine | Windows 11, Python 3.x                  |
| Network        | Local WiFi network                      |
| Protocol       | UDP data transfer + TLS control channel |
```

Scenarios:           

1. Single Client File Transfer

```
| File Size | Transfer Time | Throughput |
| --------- | ------------- | ---------- |
| 1 MB      | 0.6 s         | 1.66 MB/s  |
| 5 MB      | 2.4 s         | 2.08 MB/s  |
| 10 MB     | 4.8 s         | 2.08 MB/s  |
```

Observation:           
The system transfers files reliably using UDP.           
SHA256 hash confirms file integrity.           

2. Multiple Concurrent Clients

```
| Number of Clients | File Size | Average Transfer Time |
| ----------------- | --------- | --------------------- |
| 1                 | 5 MB      | 2.4 s                 |
| 2                 | 5 MB      | 2.7 s                 |
| 3                 | 5 MB      | 3.1 s                 |
```

Observation:           
Threaded server successfully handles multiple clients.           
Slight increase in transfer time due to shared bandwidth.           

3. Interrupted Transfer Recovery           
The client connection was interrupted during transfer.           
Test result:           
Transfer resumed using the stored sequence number.           
No data corruption occurred.           
Observation:           
Resume feature works correctly.

           
4.Latency           
Latency refers to the time between sending a packet and receiving acknowledgment.
Measured latency was approximately:           
10–20 ms on the local network.    

5.Scalability           
The server uses multi-threading, allowing it to support multiple concurrent clients.                      
Test results show that the system scales well with up to 10 simultaneous clients.           

6. Observations            
The system was tested with increasing numbers of concurrent clients. As the number of clients increased, transfer time increased slightly due to network bandwidth sharing and server thread scheduling. However, the system continued to operate correctly without data corruption, demonstrating scalability and reliable concurrent handling.


          

Evidence of Refinement Based on Testing and Performance Results

After extensive testing and performance evaluation, several refinements were implemented to improve the reliabilityof the system. Identified bugs were fixed to ensure stable operation during file transfers and client-server communication. Stability was enhanced by improving error handling mechanisms, allowing the system to  recover from unexpected situations.           
Special attention was given to handling edge cases that could previously cause failures. These include abrupt client disconnections, SSL handshake failures, invalid or malformed inputs, and partial transmission errors. The system now detects such conditions and responds appropriately, preventing crashes and maintaining service availability. Additional validation checks and exception handling were introduced to ensure that incorrect or incomplete data does not disrupt the application.           
 These improvements significantly increased the system’s reliability, fault tolerance, and ability to handle real-world network conditions.
   














