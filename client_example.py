import socket

def send_udp_via_relay(relay_host, relay_port, target_ip, target_port, data):
    """
    Connects to the TCP relay server and sends a UDP packet to the target.
    """
    try:
        # Create a TCP socket to connect to the relay
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
            tcp_sock.connect((relay_host, relay_port))
            print(f"Connected to relay server at {relay_host}:{relay_port}")

            # Prepare the header and the payload
            header = f"{target_ip}:{target_port}".encode('utf-8')
            payload = data.encode('utf-8') if isinstance(data, str) else data
            
            # Format: "target_ip:target_port|actual_data"
            message = header + b'|' + payload

            # Send the formatted message
            tcp_sock.sendall(message)
            print(f"Sent data to target {target_ip}:{target_port} via relay.")

            # Listen for a response from the target (relayed back by the server)
            print("Waiting for response from target...")
            response = tcp_sock.recv(4096)
            if response:
                print(f"Received response from target: {response.decode('utf-8', 'ignore')}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Relay server details (running in Docker)
    RELAY_HOST = '127.0.0.1'
    RELAY_PORT = 7300

    # --- IMPORTANT ---
    # Change these values to your actual target UDP server
    TARGET_IP = '123.45.67.89' 
    TARGET_PORT = 12345        
    # -----------------

    # Data to send
    udp_message = "Hello from the other side!"

    send_udp_via_relay(RELAY_HOST, RELAY_PORT, TARGET_IP, TARGET_PORT, udp_message)
