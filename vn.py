import os
import subprocess
import time
import select
import re

ports = (
    list(range(10001, 10010)) +
    list(range(1001, 1010)) +
    list(range(4002, 4010)) +
    list(range(5101, 5110)) +
    list(range(7001, 7010))
)

SCAN_DURATION = 90
OUTPUT_FILE = "output.txt"
INTERMEDIATE_FILE = ".1.txt"
AGGREGATOR_FILE = "http.txt"
VERBOSE = False

ANSI_ESCAPE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
def strip_ansi_codes(s):
    return ANSI_ESCAPE.sub('', s)

def clear_file(filename):
    with open(filename, "w") as f:
        f.truncate(0)

def run_scan(port):
    clear_file(OUTPUT_FILE)
    print(f"[INFO] Starting scan on port {port}...")
    command = f"zmap -p {port} -w vn.txt --rate=1000000000 --cooldown-time=10 | ./prox -p {port}"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    start_time = time.time()
    early_stop = False
    consecutive_zero_http = 0
    while True:
        if process.poll() is not None:
            break
        ready, _, _ = select.select([process.stdout], [], [], 1.0)
        if ready:
            line = process.stdout.readline()
            if line:
                clean_line = strip_ansi_codes(line).strip()
                if VERBOSE:
                    print(f"[DEBUG] {clean_line}")
                if "with 0 open http threads" in clean_line.lower():
                    consecutive_zero_http += 1
                else:
                    consecutive_zero_http = 0
                if consecutive_zero_http >= 3:
                    print("[INFO] Detected 3 consecutive '0 open http threads' messages. Stopping scan...")
                    process.kill()
                    early_stop = True
                    break
        if time.time() - start_time > SCAN_DURATION:
            print(f"[INFO] Timeout reached ({SCAN_DURATION} seconds), stopping scan on port {port}.")
            process.kill()
            break
    try:
        stdout, _ = process.communicate(timeout=5)
    except Exception as e:
        print(f"[ERROR] Exception during communicate: {e}")
    print(f"[INFO] Port {port} scan completed.")
    time.sleep(2)
    return early_stop

def process_results(port):
    if not os.path.exists(OUTPUT_FILE):
        print(f"[WARN] The file {OUTPUT_FILE} does not exist!")
        return
    with open(OUTPUT_FILE, "r") as f:
        content = f.read().strip()
    proxies = content.splitlines() if content else []
    count = len(proxies)
    print(f"[INFO] Port {port} scan completed, found {count} proxies.")
    
    with open(INTERMEDIATE_FILE, "w") as f:
        f.write(content)
    
    with open(AGGREGATOR_FILE, "a") as agg:
        if content:
            agg.write(content + "\n")

def process_aggregated_results():
    if not os.path.exists(AGGREGATOR_FILE):
        print("[WARN] Aggregator file does not exist!")
        return
    with open(AGGREGATOR_FILE, "r") as f:
        content = f.read().strip()
    proxies = content.splitlines() if content else []
    total_count = len(proxies)
    print(f"[INFO] Aggregated result contains {total_count} proxies.")
    
    with open(AGGREGATOR_FILE, "w") as f:
        f.write(content)
    
    print(f"[DEBUG] All results stored in {AGGREGATOR_FILE}")

for port in ports:
    run_scan(port)
    process_results(port)
process_aggregated_results()
