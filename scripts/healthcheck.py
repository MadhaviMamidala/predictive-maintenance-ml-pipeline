import sys
import http.client

try:
    conn = http.client.HTTPConnection("localhost", 8000, timeout=10)
    conn.request("GET", "/health")
    response = conn.getresponse()
    if 200 <= response.status < 300:
        print("Health check passed.")
        sys.exit(0)
    else:
        print(f"Health check failed with status: {response.status}")
        sys.exit(1)
except Exception as e:
    print(f"Health check failed with error: {e}")
    sys.exit(1)
finally:
    conn.close() 