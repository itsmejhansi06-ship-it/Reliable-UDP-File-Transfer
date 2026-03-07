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

send_times = {}
latencies = []


def make_packet(header, payload=b""):
    h = json.dumps(header).encode()
    return len(h).to_bytes(2, "big") + h + payload


filename = "test_files/" + input("Enter file name: ")

# ---------- SSL CONTROL CHANNEL ----------
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

start_time = time.perf_counter()

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
        print("Sent packet", seq)

        send_times[seq] = time.perf_counter()

        window.append((seq, packet))

        seq += 1

        while len(window) >= WINDOW_SIZE:

            try:

                ack, _ = udp.recvfrom(1024)

                ack = json.loads(ack.decode())
                ack_seq = ack["seq"]

                rtt = (time.perf_counter() - send_times[ack_seq]) * 1000
                latencies.append(rtt)

                print(f"Packet {ack_seq} latency: {round(rtt,2)} ms")

                window = [w for w in window if w[0] != ack_seq]

            except socket.timeout:

                print("Timeout → Retransmitting window")

                for _, pkt in window:
                    udp.sendto(pkt, (SERVER_IP, UDP_PORT))


# ---------- END ----------
udp.sendto(make_packet({
    "type": "END",
    "filename": filename,
    "total_packets": seq
}), (SERVER_IP, UDP_PORT))

end_time = time.perf_counter()

transfer_time = end_time - start_time
file_size = os.path.getsize(filename) / (1024 * 1024)

throughput = file_size / transfer_time

print("\nTransfer Time:", round(transfer_time, 2), "seconds")
print("Throughput:", round(throughput, 2), "MB/s")

if latencies:
    print("Average Latency:", round(sum(latencies)/len(latencies), 2), "ms")
    print("Max Latency:", round(max(latencies), 2), "ms")

# ---------- SHA256 ----------
h = hashlib.sha256()

with open(filename, "rb") as f:
    h.update(f.read())

print("Client SHA256:", h.hexdigest())
