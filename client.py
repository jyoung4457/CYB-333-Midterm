#!/usr/bin/env python3
"""
Robust TCP Client with Error Handling and Connection Failure Safety.
"""

import socket
import sys
import time

HOST = "127.0.0.1"
PORT = 65432

def run_client():
    print(f"[STARTING] Client attempting connection to server at {HOST}:{PORT}...")
    
    try:
        # Create an IPv4, TCP socket using a context manager
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            # Attempt to connect to the active server listener
            client_socket.connect((HOST, PORT))
            print(f"[SUCCESS] Connected successfully to server at {HOST}:{PORT}")
            
            # Define an array of test scenarios to feed through our connection pipeline
            test_messages = [
                "Hello, Server!",
                "Testing socket connection validation protocol.",
                "Final standard payload."
            ]
            
            for msg in test_messages:
                print(f"\n[SENDING] Dispatching payload: '{msg}'")
                # Convert string to byte payload for transport
                client_socket.sendall(msg.encode("utf-8"))
                
                # Await matching server reflection payload
                response_bytes = client_socket.recv(1024)
                if not response_bytes:
                    print("[WARN] Server terminated communication channel unexpectedly.")
                    break
                    
                print(f"[RECEIVED] From Server: '{response_bytes.decode('utf-8')}'")
                time.sleep(1)  # Simulate intentional processing intervals
                
            print("\n[DISCONNECTING] Commencing graceful cleanup sequence...")
            
    except ConnectionRefusedError:
        print(
            f"[CONNECTION ERROR] Failed to connect to {HOST}:{PORT}.\n"
            "-> Reason: Target server is either offline or actively rejecting connection.", 
            file=sys.stderr
        )
    except socket.error as err:
        print(f"[CLIENT ERROR] Network system error: {err}", file=sys.stderr)
    finally:
        print("[TERMINATED] Client channel closed cleanly.")

if __name__ == "__main__":
    run_client()  
    
