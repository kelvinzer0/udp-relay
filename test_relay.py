import socket
import threading
import time
import sys

def mock_udp_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((host, port))
        # Set a timeout to stop the server thread after the test
        sock.settimeout(10)
        try:
            while True:
                data, addr = sock.recvfrom(1024)
                if data:
                    sock.sendto(data, addr)
        except socket.timeout:
            pass # Server times out as expected

def send_udp_via_relay_for_test(relay_host, relay_port, target_ip, target_port, data):
    """
    Connects to the TCP relay server, sends a UDP packet, and returns the response.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        tcp_sock.connect((relay_host, relay_port))
        header = f"{target_ip}:{target_port}".encode('utf-8')
        payload = data.encode('utf-8') if isinstance(data, str) else data
        message = header + b'|' + payload
        tcp_sock.sendall(message)
        response = tcp_sock.recv(4096)
        return response

def test_relay():
    # --- Mock UDP Server Setup ---
    mock_server_host = '127.0.0.1'
    mock_server_port = 12345
    server_thread = threading.Thread(target=mock_udp_server, args=(mock_server_host, mock_server_port))
    server_thread.daemon = True
    server_thread.start()
    time.sleep(1) # Give the server a moment to start

    # --- Relay and Test Details ---
    relay_host = '127.0.0.1'
    relay_port = 7300
    test_message = "Hello, relay!"

    # --- Run the Test ---
    try:
        print("Running test...")
        response = send_udp_via_relay_for_test(relay_host, relay_port, mock_server_host, mock_server_port, test_message)

        # --- Assert and Cleanup ---
        if response.decode('utf-8') == test_message:
            print("Test passed!")
        else:
            print(f"Test failed: Expected '{test_message}', but got '{response.decode('utf-8')}'")
            sys.exit(1)

    except Exception as e:
        print(f"Test failed with exception: {e}")
        sys.exit(1)
    finally:
        # The server thread will exit due to the timeout
        server_thread.join()


if __name__ == "__main__":
    test_relay()
