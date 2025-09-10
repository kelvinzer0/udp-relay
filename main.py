import socket
import threading
import asyncio
import asyncore
from collections import defaultdict

class UDPRelayServer:
    def __init__(self, host='0.0.0.0', port=7300):
        self.host = host
        self.port = port
        self.clients = {}
        self.udp_sockets = {}
        
    def start(self):
        # TCP server to receive connections from workers
        tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcp_server.bind((self.host, self.port))
        tcp_server.listen(5)
        
        print(f"UDP Relay Server listening on {self.host}:{self.port}")
        
        while True:
            client_socket, client_address = tcp_server.accept()
            print(f"New connection from {client_address}")
            client_thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket,)
            )
            client_thread.daemon = True
            client_thread.start()
    
    def handle_client(self, client_socket):
        try:
            while True:
                # Receive data from the worker
                data = client_socket.recv(4096)
                if not data:
                    break
                
                # Parse header: "target_ip:target_port|actual_data"
                header_end = data.find(b'|')
                if header_end == -1:
                    continue
                
                header = data[:header_end].decode()
                udp_data = data[header_end + 1:]
                
                target_ip, target_port = header.split(':')
                target_port = int(target_port)
                
                # Create or reuse UDP socket for this target
                key = (target_ip, target_port)
                if key not in self.udp_sockets:
                    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    udp_sock.settimeout(5)
                    self.udp_sockets[key] = udp_sock
                    
                    # Start a thread to listen for responses from the target
                    response_thread = threading.Thread(
                        target=self.listen_udp_responses,
                        args=(udp_sock, client_socket, key)
                    )
                    response_thread.daemon = True
                    response_thread.start()
                
                # Send UDP data to the target
                udp_sock = self.udp_sockets[key]
                udp_sock.sendto(udp_data, (target_ip, target_port))
                
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()
    
    def listen_udp_responses(self, udp_sock, client_socket, key):
        try:
            while True:
                # Listen for responses from the UDP target
                response, addr = udp_sock.recvfrom(4096)
                
                # Send response back to the worker via TCP
                client_socket.send(response)
                
        except socket.timeout:
            print(f"UDP socket timeout for {key}")
        except Exception as e:
            print(f"Error in UDP listener for {key}: {e}")
        finally:
            udp_sock.close()
            if key in self.udp_sockets:
                del self.udp_sockets[key]

if __name__ == "__main__":
    server = UDPRelayServer()
    server.start()
