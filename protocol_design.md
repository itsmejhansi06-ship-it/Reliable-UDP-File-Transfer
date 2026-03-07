# Reliable File Transfer Protocol (Custom FTP)

Transport:
- UDP for data
- SSL/TLS TCP channel for control (resume handshake)

## Packet Structure
[Header Length][JSON Header][Payload]

Header Fields:
- type : DATA / ACK / END
- filename
- seq : chunk number

## Reliability
- Sliding window transmission
- ACK based retransmission

## Resume
Client connects via SSL control channel.
Server replies with last received sequence number.

## Integrity
SHA256 calculated on both sides.
