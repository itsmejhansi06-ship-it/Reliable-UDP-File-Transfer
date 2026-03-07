import subprocess
import time

NUM_CLIENTS = 10   # change this number

processes = []

for i in range(NUM_CLIENTS):
    p = subprocess.Popen(["python", "client.py"])
    processes.append(p)
    time.sleep(0.2)   # small delay so they start almost together

for p in processes:
    p.wait()