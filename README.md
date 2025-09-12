# UDP Relay Docker

This project runs a UDP relay server inside a Docker container. The server listens for TCP connections on port 7300, reads a target address, and relays UDP packets to that target.



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

This server expects data in a specific format over a TCP connection: `target_ip:target_port|actual_udp_payload`.

Here is a simple Python client example that sends a UDP message to a target server through the relay. You can save this code as `client_example.py`.

```python
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
```

### How to run the example:

1.  Make sure the `udp-relay` Docker container is running.
2.  Save the code above as `client_example.py`.
3.  **Important:** Change `TARGET_IP` and `TARGET_PORT` to the actual address of your target UDP server.
4.  Run the client:
    ```bash
    python client_example.py
    ```

Got it, here’s the **English version** you can drop directly into your `README.md`:

---

### Public Relay List

If you are running a **UDP Relay Docker** instance and would like to share your relay with the community, please **fork this repository**, edit the table below by adding your relay information, and submit a **pull request**. I’ll be happy to review and approve it.

| No | Relay IP / Host         | Port TCP | Date Start Active |
| -- | ----------------------- | -------- | ----------------- |
| 1  | `udp-relay.hobihaus.space` | 7300     | 2025-09-12        |
---

Do you also want me to prepare a **CONTRIBUTING.md template** in English with clear steps (fork → edit → PR)? That way contributors won’t have to guess the process.

