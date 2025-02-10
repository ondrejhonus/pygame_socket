import socket
import threading
import pickle

# Server settings
host = '127.0.0.1'
port = 12345
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(5)

# List to store all connected clients
clients = []
player_positions = {}

def handle_client(client_socket, client_address):
    global player_positions
    print(f"New connection from {client_address}")
    
    try:
        while True:
            # Receive the length of data to read
            data_length = client_socket.recv(4)
            if not data_length:
                break
            data_length = int.from_bytes(data_length, byteorder='big')
            
            # Receive the actual data (player position)
            data = b""
            while len(data) < data_length:
                chunk = client_socket.recv(data_length - len(data))
                if not chunk:
                    break
                data += chunk

            # Unpickle the player position and update the positions dictionary
            player_pos = pickle.loads(data)
            player_positions[client_address] = player_pos

            # Send all player positions to all clients
            players_data = pickle.dumps(player_positions)
            for client in clients:
                client.sendall(len(players_data).to_bytes(4, byteorder='big'))
                client.sendall(players_data)
            
    except Exception as e:
        print(f"Error with client {client_address}: {e}")
    finally:
        client_socket.close()
        clients.remove(client_socket)
        del player_positions[client_address]
        print(f"Connection closed with {client_address}")

def accept_connections():
    print("Server started, waiting for clients...")
    while True:
        client_socket, client_address = server_socket.accept()
        clients.append(client_socket)
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

# Start accepting connections
accept_connections()
