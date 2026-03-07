import socket
import ssl
import threading
import json
import hashlib
import os

UDP_IP = "0.0.0.0"
UDP_PORT = 5001
TCP_PORT = 5002

os.makedirs("recv_test_files", exist_ok=True)

progress = {}
buffers = {}
lock = threading.Lock()

# ---------- SSL CONTROL CHANNEL ----------
def control_server():

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")

    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind((UDP_IP, TCP_PORT))
    tcp.listen(5)

    print("SSL Control Channel running...")

    while True:

        client, addr = tcp.accept()

        try:

            secure = context.wrap_socket(client, server_side=True)

            data = secure.recv(1024).decode()
            req = json.loads(data)

            filename = req["filename"]

            with lock:
                last = progress.get(filename, -1)

            secure.send(json.dumps({
                "resume_from": last
            }).encode())

            secure.close()

        except Exception as e:
            print("Control channel error:", e)


# ---------- UDP DATA CHANNEL ----------
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind((UDP_IP, UDP_PORT))

print("UDP Data Channel running...")


def handle_packet(data, addr):

    try:

        header_len = int.from_bytes(data[:2], "big")
        header = json.loads(data[2:2+header_len].decode())
        payload = data[2+header_len:]

        filename = header["filename"]
        recv_path = os.path.join("recv_test_files", os.path.basename(filename))

        if filename not in buffers:
            buffers[filename] = {}

        # ---------- DATA ----------
        if header["type"] == "DATA":

            seq = header["seq"]

            buffers[filename][seq] = payload

            with lock:
                last = progress.get(filename, -1)

            # write packets in correct order
            while True:

                next_seq = last + 1

                if next_seq not in buffers[filename]:
                    break

                if next_seq == 0:
                    open(recv_path, "wb").close()

                with open(recv_path, "ab") as f:
                    f.write(buffers[filename].pop(next_seq))

                last = next_seq

                with lock:
                    progress[filename] = last

                print(f"{addr} -> packet {last}")

            ack = json.dumps({
                "type": "ACK",
                "seq": seq
            }).encode()

            udp.sendto(ack, addr)

        # ---------- END ----------
        elif header["type"] == "END":

            total_packets = header.get("total_packets")

            if total_packets is not None:

                while True:

                    with lock:
                        last = progress.get(filename, -1)

                    if last >= total_packets - 1:
                        break

            print("\nTransfer completed for:", filename)

            if os.path.exists(recv_path):

                h = hashlib.sha256()

                with open(recv_path, "rb") as f:
                    h.update(f.read())

                print("Server SHA256:", h.hexdigest())

            with lock:
                progress.pop(filename, None)

            buffers.pop(filename, None)

    except Exception as e:
        print("Packet error:", type(e).__name__, e)


# ---------- START CONTROL SERVER ----------
threading.Thread(target=control_server, daemon=True).start()

# ---------- UDP RECEIVE LOOP ----------
while True:

    try:

        data, addr = udp.recvfrom(4096)

        threading.Thread(
            target=handle_packet,
            args=(data, addr),
            daemon=True
        ).start()

    except ConnectionResetError:
        continue
