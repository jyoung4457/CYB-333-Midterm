#!/usr/bin/env python3


import socket
import sys

# Define connection constants
HOST = "127.0.0.1"  # Loopback interface for local testing
PORT = 65432        # Non-privileged port (> 1023)

def run_server():
    print(f"[STARTING] Server is initializing on {HOST}:{PORT}...")
    
    # AF_INET specifies IPv4; SOCK_STREAM specifies TCP
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            # Allow immediate reuse of the port after shutdown to prevent "Address already in use" errors
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind the socket to our address configuration
            server_socket.bind((HOST, PORT))
            
            # Enable the server to accept connections
            server_socket.listen()
            print(f"[LISTENING] Server is listening for incoming connections...")
            
            # Block execution until a client connects
            client_socket, client_address = server_socket.accept()
            
            # Manage the active client connection lifecycle safely
            with client_socket:
                print(f"[CONNECTED] Established connection with client at {client_address}")
                
                while True:
                    # Receive data stream up to 1024 bytes
                    data = client_socket.recv(1024)
                    
                    # An empty bytes object (b'') indicates a clean remote disconnection
                    if not data:
                        print("[DISCONNECTED] Client closed the connection cleanly.")
                        break
                        
                    # Decode incoming bytes safely into human-readable text
                    decoded_msg = data.decode("utf-8")
                    print(f"[RECEIVED] From Client: '{decoded_msg}'")
                    
                    # Echo the same message back to verify round-trip delivery
                    response_msg = f"Server Echo: {decoded_msg}"
                    client_socket.sendall(response_msg.encode("utf-8"))
                    print(f"[SENT] Echoed response back to client.")
                    
    except socket.error as err:
        print(f"[SERVER ERROR] A socket exception occurred: {err}", file=sys.stderr)
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Server forced to stop by keyboard interrupt.")
    finally:
        print("[TERMINATED] Server lifecycle ended cleanly.")

if __name__ == "__main__":
    run_server()
