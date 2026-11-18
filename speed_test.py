"""Measure HTTP download throughput across ten sequential GET requests."""

import argparse
import http.client
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

REQUEST_COUNT = 10
CHUNK_SIZE = 64 * 1024
TIMEOUT_SECONDS = 30


def download(url):
    """Return the response body size in bytes and elapsed time in seconds."""
    request = urllib.request.Request(url, headers={"Accept-Encoding": "identity"})
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        expected_size = response.length
        size = 0
        while chunk := response.read(CHUNK_SIZE):
            size += len(chunk)

    elapsed = time.perf_counter() - started
    if expected_size is not None and size != expected_size:
        raise OSError(f"Incomplete response: received {size} of {expected_size} bytes")
    return size, elapsed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="HTTP or HTTPS URL of the file to download")
    args = parser.parse_args()

    try:
        url = urllib.parse.urlsplit(args.url)
    except ValueError as error:
        parser.error(str(error))
    if url.scheme not in ("http", "https") or not url.hostname:
        parser.error("provide a full URL starting with http:// or https://")

    total_bytes = 0
    total_seconds = 0.0
    for number in range(1, REQUEST_COUNT + 1):
        try:
            size, elapsed = download(args.url)
        except (OSError, ValueError, http.client.HTTPException) as error:
            print(f"Request {number}/{REQUEST_COUNT} failed: {error}", file=sys.stderr)
            return 1
        total_bytes += size
        total_seconds += elapsed

    average_ms = total_seconds / REQUEST_COUNT * 1000
    speed_mbps = total_bytes * 8 / total_seconds / 1_000_000
    print(f"Completed requests: {REQUEST_COUNT}")
    print(f"Average request time: {average_ms:.2f} ms")
    print(f"Total downloaded: {total_bytes:,} bytes")
    print(f"Download speed: {speed_mbps:.2f} Mbps")
    return 0


if __name__ == "__main__":
    sys.exit(main())
