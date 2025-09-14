# TCP/UDP Relay Docker

This project runs a TCP/UDP relay server inside a Docker container. The server listens for TCP connections on port 7300, reads a target address and protocol, and relays TCP or UDP packets to that target.

## How to Run from Docker Hub

Once published, you or anyone else can run the image directly from Docker Hub.

1.  **Pull the image from Docker Hub:**

    ```bash
    docker pull kelvinzer0/udp-relay
    ```

2.  **Run the Docker container:**

    ```bash
    docker run -p 7300:7300 --name udp-relay-server kelvinzer0/udp-relay
    ```

The server will be listening on TCP port 7300 on your local machine.

## Example Usage

This server expects data in a specific format over a TCP connection: `protocol:target_ip:target_port|actual_data`.

Here is a simple Python client example that sends a message to a target server through the relay. You can save this code as `client_example.py`.

```python
import socket

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
    # Relay server details
    RELAY_HOST = '127.0.0.1'
    RELAY_PORT = 7300

    # --- UDP Example ---
    print("--- Sending UDP Packet ---")
    UDP_TARGET_IP = '1.1.1.1'  # Example public DNS
    UDP_TARGET_PORT = 53
    udp_message = b'\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01' # DNS query for example.com
    send_via_relay(RELAY_HOST, RELAY_PORT, 'udp', UDP_TARGET_IP, UDP_TARGET_PORT, udp_message)
    print("\n" + "-"*26 + "\n")

    # --- TCP Example ---
    print("--- Sending TCP Packet ---")
    TCP_TARGET_IP = '93.184.216.34'  # Example IP for example.com
    TCP_TARGET_PORT = 80
    tcp_message = "GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n"
    send_via_relay(RELAY_HOST, RELAY_PORT, 'tcp', TCP_TARGET_IP, TCP_TARGET_PORT, tcp_message)
```

### How to run the example:

1.  Make sure the `udp-relay` Docker container is running.
2.  Save the code above as `client_example.py`.
3.  Run the client:
    ```bash
    python client_example.py
    ```

### Public Relay List

If you are running a **TCP/UDP Relay Docker** instance and would like to share your relay with the community, please **fork this repository**, edit the table below by adding your relay information, and submit a **pull request**. I’ll be happy to review and approve it.

| No | Relay IP / Host         | Port TCP | Date Start Active |
| -- | ----------------------- | -------- | ----------------- |
| 1  | `udp-relay.hobihaus.space` | 7300     | 2025-09-12        |
---

