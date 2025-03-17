import socket
from ai_logic import analyze_sos_message
from physics_conversion import convert_physics_data
import json


PHYSICS_DETECTION_PREFIX = "PhysicsDetection:"
MOVEMENT_REQUEST = "request_move"


def send_movement_command(x, y, z):
    movement_data = {"move": {"x": x, "y": y, "z": z}}
    movement_json = json.dumps(movement_data)
    return movement_json


HOST = "0.0.0.0"  # Listen on all available interfaces
PORT = 6000  # Port for communication

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))  # Bind the socket to an address and port
server_socket.listen(5)  # Listen for up to 5 connections

print(f"🟢 AI Agent is running on {HOST}:{PORT}, waiting for Unity...")

while True:
    conn, addr = server_socket.accept()  # Accept connection
    print(f"🔗 Connection from {addr}")

    # Receive data from Unity
    data = conn.recv(1024).decode("utf-8").strip()
    if not data:
        print("⚠️ Received empty message from Unity, ignoring...")
        continue  # Skip processing if empty message
    print(f"📨 Received from Unity: {data}")  # ✅ Log the received message

    if data.startswith("PhysicsDetection:"):
        physics_data = data[len("PhysicsDetection:") :].strip()
        response = convert_physics_data(physics_data)

        print(f"[🧪 Physics Engine Detection] {response}")
    elif data == MOVEMENT_REQUEST:
        response = send_movement_command(1000, 0, 0)  # Example movement command
        print("[🚀 Movement Command] Sending movement command:", response)
    else:
        response = analyze_sos_message(data)

    # Send response back to Unity
    conn.sendall(response.encode("utf-8"))
    print(f"📤 Sent to Unity: {response}")

    conn.close()  # Close connection
