'''
 the module is responsible for fetching the file from the host(cloud service)
 records the timestamps for every download and computes the throughput
 writes the result to a .csv file in `data/` 
'''

import csv
import os
import time
import uuid
import ssl
import socket
from zoneinfo import ZoneInfo
from datetime import datetime
from urllib.parse import urlparse, urlencode, urlunparse, parse_qs

# Some constants
CHUNK_SIZE = 8*1024         # in bytes
REQUEST_TIMEOUT = 60        # in seconds

CSV_HEADERS = [
    "timestamp",
    "hour_of_day",
    "http_status",
    "download_start_time",
    "download_end_time",
    "elapsed_transfer_s",
    "filesize_bytes",
    "throughput_mbps",
    "result",       # report error if download fails
    "url",          # needed to verify cache busting(dynamic query strings)
]

# force a fresh DNS resolution for the hostname, handy if the hosting is across CDNs(overkill tbh)
def resolve_ip(hostname: str) -> str:
    results = socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
    return results[0][4][0]     # refer the return type of getaddrinfo, we are looking at ip and port num, and we're interested in ip addr


# the following function implements dynamic query string to deter caching resources on servers
# makes use of uuid to generate a 4-character identifier each time
def bust_cache(url: str) -> str:
    parsed_url = urlparse(url)
    params = parse_qs(parsed_url.query, keep_blank_values=True)
    params["_cbt"] = [uuid.uuid4().hex]
    new_query = urlencode(params, doseq=True)
    return urlunparse(parsed_url._replace(query=new_query))     # _replace() takes kwargs


# initiates a https GET request over an established secure TCP socket
# streams the body in chunks, while maintaining a perf_counter and total byte count
# computes throughput and elapsed time and the function returns it
def stream_download(url: str) -> dict:
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    port = parsed_url.port or 443
    query = parsed_url.query
    path = parsed_url.path

    # if the path contains query strings(handling authentication token such as SAS), include it in path
    path = f"{path}?{query}" if query else path

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context()

    try:
        # wrap the socket with SSL context for HTTPS
        secure_tcp_socket = context.wrap_socket(tcp_socket, server_hostname=hostname)
        secure_tcp_socket.connect((hostname, port))

        headers = [
            f"GET {path} HTTP/1.1",
            f"Host: {hostname}",
            "User-Agent: Python-Socket-Client/1.0",
            "Cache-Control: no-cache, no-store, must-revalidate",
            "Pragma: no-cache",
            "Expires: 0",
            "Connection: close",

            # since the request header ends with 2 newlines
            "",
            ""
        ]

        # append a newline(with carriage return) for each header line
        request = "\r\n".join(headers)
        secure_tcp_socket.sendall(request.encode("utf-8"))

        raw_response = b""
        start_time = time.perf_counter()
        while True:
            data = secure_tcp_socket.recv(CHUNK_SIZE)
            if not data:
                break
            raw_response += data
        elapsed_time = time.perf_counter() - start_time     # a minor inaccuracy here: we're including the time taken to parse the header but its negligible

    except Exception as e:
        raise
    finally:
        secure_tcp_socket.close()

    header_part, body = raw_response.split(b"\r\n\r\n", 1)

    status_line = header_part.split(b"\r\n")[0].decode()
    http_status = int(status_line.split(" ")[1])

    total_bytes = len(body)

    throughput = (total_bytes * 8) / (elapsed_time * 1e6) if elapsed_time > 0 else 0.0

    return {
        "http_status": http_status,
        "elapsed_transfer_s": round(elapsed_time, 4),
        "filesize_bytes": total_bytes,
        "throughput_mbps": round(throughput, 4),
    }

# insert a header if not present
def create_csv_header(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)   # create data/ if missing
    if not os.path.exists(path):
        with open(path, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=CSV_HEADERS)
            writer.writeheader()


# append the recorded metric to an existing csv
def append_csv_row(path: str, row: dict) -> None:
    with open(path, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_HEADERS)
        writer.writerow(row)


# runner initiates the pipeline by invoking the above helpers in order
def runner(url: str, path: str) -> None:
    if not url:
        print("Invalid URL, try with a different one")
        return

    if not path:
        path = "./data/test_set.csv"

    ist = ZoneInfo('Asia/Kolkata')
    current_time = datetime.now(ist)

    csv_row = {h: "" for h in CSV_HEADERS}
    csv_row["timestamp"] = current_time.isoformat()
    csv_row["hour_of_day"] = current_time.hour
    csv_row["url"] = url

    try:
        hostname = urlparse(url).hostname
        resolve_ip(hostname)    
    except Exception as e:
        print(f"Failed to resolve IP from hostname: {e}")
        return

    try:
        busted_url = bust_cache(url)
        csv_row["url"] = busted_url     # overwrite with cache-busted URL
    except Exception as e:
        print(f"Failed to generate cache-busted URL: {e}")
        busted_url = url

    try:
        download_start = datetime.now(ist)
        metrics = stream_download(busted_url)
        download_end = datetime.now(ist)

        csv_row["download_start_time"] = download_start.isoformat()
        csv_row["download_end_time"] = download_end.isoformat()
        csv_row["http_status"] = metrics["http_status"]
        csv_row["filesize_bytes"] = metrics["filesize_bytes"]
        csv_row["elapsed_transfer_s"] = metrics["elapsed_transfer_s"]
        csv_row["throughput_mbps"] = metrics["throughput_mbps"]
        csv_row["result"] = "success"

    except Exception as e:
        csv_row["result"] = "failed"
        print(f"Failed to stream download: {e}")
    
    create_csv_header(path)
    append_csv_row(path, csv_row)