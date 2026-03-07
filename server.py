import socket, ssl, threading, json, hashlib

UDP_IP = "0.0.0.0"
UDP_PORT = 5001
TCP_PORT = 5002

progress = {}
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

        secure = context.wrap_socket(client, server_side=True)

        data = secure.recv(1024).decode()

        req = json.loads(data)

        filename = req["filename"]

        with lock:
            last = progress.get(filename, -1)

        secure.send(json.dumps({"resume_from": last}).encode())

        secure.close()


# ---------- UDP DATA CHANNEL ----------
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind((UDP_IP, UDP_PORT))

print("UDP Data Channel running...")


def handle_packet(data, addr):

    header_len = int.from_bytes(data[:2], "big")

    header = json.loads(data[2:2+header_len].decode())

    payload = data[2+header_len:]

    filename = header["filename"]

    if header["type"] == "DATA":

        seq = header["seq"]

        with lock:
            last = progress.get(filename, -1)

        if seq == last + 1:

            if seq == 0:
                open("recv_"+filename, "wb").close()

            with open("recv_"+filename, "ab") as f:
                f.write(payload)

            with lock:
                progress[filename] = seq

        ack = json.dumps({"type": "ACK", "seq": seq}).encode()

        udp.sendto(ack, addr)


    elif header["type"] == "END":

        print("Finished:", filename)

        h = hashlib.sha256()

        with open("recv_"+filename, "rb") as f:
            h.update(f.read())

        print("Server SHA256:", h.hexdigest())


threading.Thread(target=control_server, daemon=True).start()

while True:

    data, addr = udp.recvfrom(4096)

    threading.Thread(target=handle_packet, args=(data, addr), daemon=True).start()