import socket
import threading
import time
import sys

def mock_udp_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((host, port))
        sock.settimeout(10)
        try:
            data, addr = sock.recvfrom(1024)
            if data:
                sock.sendto(data, addr)
        except socket.timeout:
            pass

def mock_tcp_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, port))
        sock.listen(1)
        sock.settimeout(10)
        try:
            conn, addr = sock.accept()
            with conn:
                data = conn.recv(1024)
                if data:
                    conn.sendall(data)
        except socket.timeout:
            pass

def send_via_relay_for_test(relay_host, relay_port, protocol, target_ip, target_port, data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        tcp_sock.connect((relay_host, relay_port))
        header = f"{protocol}:{target_ip}:{target_port}".encode('utf-8')
        payload = data.encode('utf-8') if isinstance(data, str) else data
        message = header + b'|' + payload
        tcp_sock.sendall(message)
        response = tcp_sock.recv(4096)
        return response

def test_udp_relay():
    mock_server_host = '127.0.0.1'
    mock_server_port = 12345
    server_thread = threading.Thread(target=mock_udp_server, args=(mock_server_host, mock_server_port))
    server_thread.daemon = True
    server_thread.start()
    time.sleep(1)

    relay_host = '127.0.0.1'
    relay_port = 7300
    test_message = "Hello, UDP relay!"

    try:
        print("Running UDP relay test...")
        response = send_via_relay_for_test(relay_host, relay_port, 'udp', mock_server_host, mock_server_port, test_message)
        assert response.decode('utf-8') == test_message
        print("UDP relay test passed!")
    except Exception as e:
        print(f"UDP relay test failed: {e}")
        sys.exit(1)
    finally:
        server_thread.join()

def test_tcp_relay():
    mock_server_host = '127.0.0.1'
    mock_server_port = 12346
    server_thread = threading.Thread(target=mock_tcp_server, args=(mock_server_host, mock_server_port))
    server_thread.daemon = True
    server_thread.start()
    time.sleep(1)

    relay_host = '127.0.0.1'
    relay_port = 7300
    test_message = "Hello, TCP relay!"

    try:
        print("Running TCP relay test...")
        response = send_via_relay_for_test(relay_host, relay_port, 'tcp', mock_server_host, mock_server_port, test_message)
        assert response.decode('utf-8') == test_message
        print("TCP relay test passed!")
    except Exception as e:
        print(f"TCP relay test failed: {e}")
        sys.exit(1)
    finally:
        server_thread.join()

if __name__ == "__main__":
    test_udp_relay()
    test_tcp_relay()
