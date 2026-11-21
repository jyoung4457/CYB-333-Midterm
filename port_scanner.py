#!/usr/bin/env python3


from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import socket
import sys

# Common structural ports for standard testing defaults
COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 443, 3389, 8080]

def scan_single_port(host: str, port: int, timeout: float = 1.0) -> tuple:
    """
    Attempts to establish a TCP connection to a specific port on a target host.
    Returns a tuple of (port, status_string).
    """
    # AF_INET specifies IPv4; SOCK_STREAM specifies TCP stream connections
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Prevent the scanner from hanging indefinitely on closed or filtered ports
        sock.settimeout(timeout)
        
        # connect_ex returns 0 if the connection succeeded, or an error code if it failed
        result = sock.connect_ex((host, port))
        
        if result == 0:
            return port, "OPEN"
        else:
            return port, "CLOSED"

def execute_port_scan(target_host: str, ports_to_scan: list, max_threads: int = 50):
    """
    Orchestrates the multi-threaded scanning process across the resolved target.
    """
    # Verify and resolve hostname to an IP address safely
    try:
        target_ip = socket.gethostbyname(target_host)
    except socket.gaierror:
        print(f"\n[ERROR] Unreachable Host: Could not resolve address '{target_host}'.")
        return

    print("-" * 65)
    print(f"Scanning Target : {target_host} ({target_ip})")
    print(f"Time Started    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 65)

    open_ports = []
    closed_ports_count = 0

    # Leverage a thread pool context manager to scale out scanning performance concurrently
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        # Submit all tasks into the execution pipeline queue
        futures = {executor.submit(scan_single_port, target_ip, port): port for port in ports_to_scan}
        
        # Dynamically process completed worker threads as they yield responses
        for future in as_completed(futures):
            try:
                port, status = future.result()
                if status == "OPEN":
                    print(f" Port {port:5d} : [ OPEN ]")
                    open_ports.append(port)
                else:
                    # Echoing closed ports individually can saturate logs; summarizing keeps terminal clean
                    closed_ports_count += 1
            except Exception as e:
                print(f" [ERROR] Unexpected failure scanning port: {e}")

    # Display clean visual report cards summary
    print("\n" + "=" * 30 + " SCAN SUMMARY " + "=" * 30)
    print(f"Total Ports Scanned : {len(ports_to_scan)}")
    print(f"Open Ports Found    : {open_ports if open_ports else 'None detected'}")
    print(f"Closed/Filtered     : {closed_ports_count}")
    print(f"Time Completed      : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 74)

def parse_port_range(range_str: str) -> list:
    """
    Parses a string input formatting window ranges (e.g., '20-100') safely.
    """
    try:
        parts = range_str.split('-')
        if len(parts) != 2:
            raise ValueError
        start, end = int(parts[0]), int(parts[1])
        if not (1 <= start <= 65535 and 1 <= end <= 65535 and start <= end):
            raise ValueError
        return list(range(start, end + 1))
    except ValueError:
        print("\n[ERROR] Invalid port range format. Correct syntax layout example: '20-80'")
        sys.exit(1)

def main():
    print("=" * 65)
    print("             PRODUCTION TCP PORT SCANNER PIPELINE             ")
    print("=" * 65)
    
    # User Input 1: Target Selection
    target = input("Enter target host (e.g., 127.0.0.1 or scanme.nmap.org): ").strip()
    if not target:
        print("[ERROR] Input violation: Target cannot be left empty.")
        sys.exit(1)
        
    # User Input 2: Scan Modality Selection
    print("\nSelect Scan Target Mode:")
    print("1. Scan standard common ports list")
    print("2. Scan custom numerical port range (e.g., 20-100)")
    mode = input("Enter choice (1 or 2): ").strip()

    if mode == "1":
        ports = COMMON_PORTS
    elif mode == mode == "2":
        range_input = input("Enter range using a hyphen dash (e.g., 22-84): ").strip()
        ports = parse_port_range(range_input)
    else:
        print("[ERROR] Invalid configuration mode choice option selected.")
        sys.exit(1)

    # Fire execution engine sequence
    try:
        execute_port_scan(target, ports)
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Scanning sequence canceled by manual script abort interrupt.")
        sys.exit(0)

if __name__ == "__main__":
    main()
