import socket
import threading

class RelayServer:
    def __init__(self, host='0.0.0.0', port=7300):
        self.host = host
        self.port = port
        self.udp_sockets = {}
        self.tcp_sockets = {}

    def start(self):
        # TCP server to receive connections from workers
        tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcp_server.bind((self.host, self.port))
        tcp_server.listen(5)
        
        print(f"Relay Server listening on {self.host}:{self.port}")
        
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
                data = client_socket.recv(4096)
                if not data:
                    break
                
                header_end = data.find(b'|')
                if header_end == -1:
                    continue
                
                header = data[:header_end].decode()
                actual_data = data[header_end + 1:]
                
                parts = header.split(':')
                protocol = parts[0]
                target_ip = parts[1]
                target_port = int(parts[2])
                
                if protocol.lower() == 'udp':
                    self.handle_udp(client_socket, target_ip, target_port, actual_data)
                elif protocol.lower() == 'tcp':
                    self.handle_tcp(client_socket, target_ip, target_port, actual_data)

        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def handle_udp(self, client_socket, target_ip, target_port, udp_data):
        key = (target_ip, target_port)
        if key not in self.udp_sockets:
            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_sock.settimeout(5)
            self.udp_sockets[key] = udp_sock
            
            response_thread = threading.Thread(
                target=self.listen_udp_responses,
                args=(udp_sock, client_socket, key)
            )
            response_thread.daemon = True
            response_thread.start()
        
        udp_sock = self.udp_sockets[key]
        udp_sock.sendto(udp_data, (target_ip, target_port))

    def listen_udp_responses(self, udp_sock, client_socket, key):
        try:
            while True:
                response, addr = udp_sock.recvfrom(4096)
                client_socket.send(response)
        except socket.timeout:
            print(f"UDP socket timeout for {key}")
        except Exception as e:
            print(f"Error in UDP listener for {key}: {e}")
        finally:
            udp_sock.close()
            if key in self.udp_sockets:
                del self.udp_sockets[key]

    def handle_tcp(self, client_socket, target_ip, target_port, tcp_data):
        key = (target_ip, target_port)
        if key not in self.tcp_sockets:
            try:
                tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcp_sock.connect((target_ip, target_port))
                self.tcp_sockets[key] = tcp_sock

                response_thread = threading.Thread(
                    target=self.listen_tcp_responses,
                    args=(tcp_sock, client_socket, key)
                )
                response_thread.daemon = True
                response_thread.start()
            except Exception as e:
                print(f"Failed to connect to TCP target {key}: {e}")
                return

        tcp_sock = self.tcp_sockets[key]
        try:
            tcp_sock.sendall(tcp_data)
        except Exception as e:
            print(f"Error sending to TCP target {key}: {e}")
            self.cleanup_tcp_socket(key)

    def listen_tcp_responses(self, tcp_sock, client_socket, key):
        try:
            while True:
                response = tcp_sock.recv(4096)
                if not response:
                    break
                client_socket.send(response)
        except Exception as e:
            print(f"Error in TCP listener for {key}: {e}")
        finally:
            self.cleanup_tcp_socket(key)

    def cleanup_tcp_socket(self, key):
        if key in self.tcp_sockets:
            self.tcp_sockets[key].close()
            del self.tcp_sockets[key]

if __name__ == "__main__":
    server = RelayServer()
    server.start()
