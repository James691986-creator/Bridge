import socket
import json
import os
import sys

# Core Lambert Protocol Constants
PORT = 5757
BUFFER = 4096
KEY_PATH = "sovereign-key.json"
IDENTITY_HASH = "ed971a0"

class SovereignNode:
    def __init__(self):
        self.node_id = self._load_identity()

    def _load_identity(self):
        if os.path.exists(KEY_PATH):
            with open(KEY_PATH, 'r') as f:
                return json.load(f)
        return {"id": "UNVERIFIED", "hash": IDENTITY_HASH}

    def broadcast_handshake(self, target_ip):
        print(f"[*] Dispatching Signal to {target_ip} (Hash: {IDENTITY_HASH})")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((target_ip, PORT))
                packet = json.dumps(self.node_id).encode('utf-8')
                s.sendall(packet)
                response = s.recv(BUFFER).decode('utf-8')
                print(f"[+] LINK ESTABLISHED: {response}")
        except Exception as e:
            print(f"[!] Link Failed: {e}")

    def listen_active(self):
        print(f"[*] Sovereign Root Listening on port {PORT}...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', PORT))
            s.listen(12)
            while True:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(BUFFER).decode('utf-8')
                    if IDENTITY_HASH in data:
                        print(f"[+] AUTHENTICATED ACCESS: {addr}")
                        conn.sendall(b"IDENTITY VERIFIED - LAMBERT PROTOCOL ACTIVE")
                    else:
                        print(f"[!] UNAUTHORIZED SIGNAL ATTEMPT: {addr}")
                        conn.sendall(b"CONNECTION REFUSED - ARCHITECT ONLY")

if __name__ == "__main__":
    node = SovereignNode()
    if len(sys.argv) > 1:
        if sys.argv[1] == "listen":
            node.listen_active()
        elif sys.argv[1] == "sync" and len(sys.argv) > 2:
            node.broadcast_handshake(sys.argv[2])
    else:
        print("Usage: python REMOTE_CONTROLLER.py [listen|sync] [Target_IP]")
