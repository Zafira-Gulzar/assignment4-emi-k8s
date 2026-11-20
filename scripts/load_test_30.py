import json
import urllib.request
from collections import Counter

url = "http://emi.local/api/emi"
counts = Counter()

print("Sending 30 requests through Ingress (http://emi.local)...\n")
for i in range(1, 31):
    data = json.dumps({"principal": 100000, "rate": 10, "months": 12}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode())
            pod = res.get("servedBy", "Unknown")
            counts[pod] += 1
            print(f"Request {i:02d}: served by {pod}")
    except Exception as e:
        print(f"Request {i:02d} FAILED: {e}")

print("\n--- Load Distribution Summary (3 Replicas) ---")
for pod, count in counts.items():
    print(f"{pod}: {count} requests")
