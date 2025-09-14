import socket
import argparse

def send_via_relay(relay_host, relay_port, protocol, target_ip, target_port, data):
    """
    Connects to the TCP relay server and sends a packet to the target.
    """
    try:
        # Create a TCP socket to connect to the relay
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
            tcp_sock.connect((relay_host, relay_port))
            print(f"Connected to relay server at {relay_host}:{relay_port}")

            # Prepare the header and the payload
            header = f"{protocol}:{target_ip}:{target_port}".encode('utf-8')
            payload = data.encode('utf-8') if isinstance(data, str) else data
            
            # Format: "protocol:target_ip:target_port|actual_data"
            message = header + b'|' + payload

            # Send the formatted message
            tcp_sock.sendall(message)
            print(f"Sent {protocol.upper()} data to target {target_ip}:{target_port} via relay.")

            # Listen for a response from the target (relayed back by the server)
            print("Waiting for response from target...")
            response = tcp_sock.recv(4096)
            if response:
                print(f"Received response from target: {response.decode('utf-8', 'ignore')}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TCP/UDP Relay Client Example")
    parser.add_argument('--relay-host', type=str, default='127.0.0.1', help='Relay server host')
    parser.add_argument('--relay-port', type=int, default=7300, help='Relay server port')
    args = parser.parse_args()

    # --- UDP Example ---
    print("--- Sending UDP Packet ---")
    UDP_TARGET_IP = '1.1.1.1'  # Example public DNS
    UDP_TARGET_PORT = 53
    udp_message = b'\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01' # DNS query for example.com
    send_via_relay(args.relay_host, args.relay_port, 'udp', UDP_TARGET_IP, UDP_TARGET_PORT, udp_message)
    print("\n" + "-"*26 + "\n")

    # --- TCP Example ---
    print("--- Sending TCP Packet ---")
    TCP_TARGET_IP = '93.184.216.34'  # Example IP for example.com
    TCP_TARGET_PORT = 80
    tcp_message = "GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n"
    send_via_relay(args.relay_host, args.relay_port, 'tcp', TCP_TARGET_IP, TCP_TARGET_PORT, tcp_message)
