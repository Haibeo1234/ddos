import requests

urls = [
    "https://proxyspace.pro/https.txt",
    "https://proxyspace.pro/http.txt"
]

output_file = "http.txt"

def get_proxies_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        proxies = response.text.strip().split('\n')
        return [p for p in proxies if p.strip().endswith(":3128")]
    except Exception as e:
        return []

try:
    with open(output_file, "r") as f:
        existing_proxies = set(line.strip() for line in f if line.strip())
except FileNotFoundError:
    existing_proxies = set()

new_proxies = set()
for url in urls:
    proxies = get_proxies_from_url(url)
    new_proxies.update(proxies)

unique_new_proxies = new_proxies - existing_proxies

if unique_new_proxies:
    with open(output_file, "a") as f:
        for proxy in unique_new_proxies:
            f.write(proxy + "\n")

print(f"Success get new proxy {len(unique_new_proxies)}")
