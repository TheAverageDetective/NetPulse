'''
 the module is responsible for fetching the file from the host(cloud service)
 records the timestamps for every download and computes the throughput
 writes the result to a .csv file in `data/` 
'''

import csv
import os
import socket
import time
import uuid
import requests
from zoneinfo import ZoneInfo
from datetime import datetime, timezone
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


def stream_download(url: str) -> dict:
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",         # resource expires immediately
        "Connection": "close"   # for non-persistent http
    }

    # invoke a GET request for the current session, with the above headers
    response = requests.get(
        url=url,
        headers=headers,
        stream=True,
        timeout=REQUEST_TIMEOUT,
        allow_redirects=True,
    )

    response.raise_for_status()

    start_time = time.perf_counter()
    total_bytes = 0
    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
        total_bytes += len(chunk)

    elapsed_time = time.perf_counter() - start_time

    throughput = (total_bytes * 8) / (elapsed_time * 1e6) if elapsed_time > 0 else 0.0

    return {
        "http_status": response.status_code,
        "elapsed_transfer_s": round(elapsed_time, 4),   # seconds
        "filesize_bytes": total_bytes,
        "throughput_mbps": round(throughput, 4),
    }

# insert a header if not present
def create_csv_header(path: str) -> None:
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

    ist = ZoneInfo.timezone('Asia/Kolkata')
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