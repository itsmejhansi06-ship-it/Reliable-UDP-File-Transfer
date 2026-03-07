# Reliable File Transfer Protocol (Custom FTP)

Secure UDP-based resumable file transfer.


# Problem Definition and Architecture           
Problem           
Traditional UDP communication is unreliable because:           
-packets can be lost                     
-packets can arrive out of order           
-packets can be duplicated           
However, UDP is faster than TCP.

# Objectives           
The system aims to:           
-implement reliable file transfer over UDP           
-implement sliding window protocol           
-handle out-of-order packets           
-support multiple concurrent clients           
-ensure data integrity using SHA256           
-provide secure control communication using SSL           



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

# Core Implementation           
The project uses low-level socket programming.           
-Socket Creation           
Client UDP socket:           
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)           
Server UDP socket:           
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)           
udp.bind((UDP_IP, UDP_PORT))           
TCP socket for SSL control:           
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)           



# Feature Implementation           
-Reliable Data Transfer           
The system implements Sliding Window Protocol.           
Client sends multiple packets before waiting for acknowledgment.           
-Packet Retransmission           
If ACK is not received within timeout:The entire window is retransmitted.           
-Out-of-Order Packet Handling           
The server uses a packet buffer.           
Packets are written only when the correct sequence number arrives.           
-SSL Security           
Control channel uses TLS encryption.                      
-Multiple Client Support           
The server uses multithreading.
Each packet is processed in a new thread.                      
This allows multiple clients to send files simultaneously.           



#  Protocol Design:  
  
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
   


# Performance Evaluation           
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
Round Trip Time is measured for each packet.
Measured latency was approximately:           
10–20 ms on the local network.    

5.Scalability           
The server uses multi-threading, allowing it to support multiple concurrent clients.                      
Test results show that the system scales well with up to 10 simultaneous clients.           

6. Observations            
The system was tested with increasing numbers of concurrent clients. As the number of clients increased, transfer time increased slightly due to network bandwidth sharing and server thread scheduling. However, the system continued to operate correctly without data corruption, demonstrating scalability and reliable concurrent handling.


          

# Optimization and Fixes           
Several improvements were made during testing.
-Bug Fixes           
Problem:           
Out-of-order packets caused file corruption.           
Solution:           
Added packet buffer mechanism.           
           
-Thread Safety           
Problem:           
Concurrent threads caused race conditions.           
Solution:           
lock = threading.Lock()           
All buffer and progress updates are protected.           

-Improved Error Handling           
Examples:           
Packet error: KeyError           
ConnectionResetError           
Timeout retransmission                      

-Handled using:           
try / except blocks 

-Resume Support           
Client resumes transfer from last received packet.           

-Server tracks progress:           
         

