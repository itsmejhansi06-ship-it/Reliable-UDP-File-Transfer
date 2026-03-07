import socket
import ssl
import json
import hashlib
import time
import os

SERVER_IP = "127.0.0.1"
UDP_PORT = 5001
TCP_PORT = 5002

CHUNK_SIZE = 1024
WINDOW_SIZE = 5

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.settimeout(1)


def make_packet(header, payload=b""):
    h = json.dumps(header).encode()
    return len(h).to_bytes(2, "big") + h + payload


filename = input("Enter file name: ")

# ---------- SECURE CONTROL CHANNEL ----------
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
secure = context.wrap_socket(tcp)

secure.connect((SERVER_IP, TCP_PORT))

secure.send(json.dumps({"filename": filename}).encode())

resp = json.loads(secure.recv(1024).decode())

resume_from = resp["resume_from"]

secure.close()

print("Resume from seq:", resume_from)

# ---------- PERFORMANCE TIMER START ----------
start_time = time.time()

# ---------- FILE TRANSFER ----------
with open(filename, "rb") as f:

    f.seek((resume_from + 1) * CHUNK_SIZE)

    seq = resume_from + 1
    window = []

    while True:

        chunk = f.read(CHUNK_SIZE)

        if not chunk:
            break

        header = {
            "type": "DATA",
            "filename": filename,
            "seq": seq
        }

        packet = make_packet(header, chunk)

        udp.sendto(packet, (SERVER_IP, UDP_PORT))

        window.append((seq, packet))

        seq += 1

        # Sliding Window ACK handling
        if len(window) >= WINDOW_SIZE:

            while True:

                try:

                    ack, _ = udp.recvfrom(1024)

                    ack = json.loads(ack.decode())

                    window = [w for w in window if w[0] != ack["seq"]]

                    break

                except socket.timeout:

                    for _, pkt in window:
                        udp.sendto(pkt, (SERVER_IP, UDP_PORT))


# ---------- END MESSAGE ----------
udp.sendto(make_packet({
    "type": "END",
    "filename": filename
}), (SERVER_IP, UDP_PORT))

# ---------- PERFORMANCE TIMER END ----------
end_time = time.time()

transfer_time = end_time - start_time

# ---------- FILE SIZE ----------
file_size = os.path.getsize(filename) / (1024 * 1024)  # MB

# ---------- THROUGHPUT ----------
throughput = file_size / transfer_time

print("Transfer Time:", round(transfer_time, 2), "seconds")
print("Throughput:", round(throughput, 2), "MB/s")

# ---------- INTEGRITY CHECK ----------
h = hashlib.sha256()

with open(filename, "rb") as f:
    h.update(f.read())

print("Client SHA256:", h.hexdigest())
