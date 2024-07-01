import socket
import pickle

def authenticate(username, password):
    credentials = {'username': username, 'password': password}

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 8081))

    # Send authentication credentials to the server
    client_socket.send(pickle.dumps(credentials))

    # Receive the authentication result from the server
    data = client_socket.recv(1024)
    response = pickle.loads(data)

    print(f"Server response: {response['message']} for {username}")

    # If authentication is successful, interact with GPT-3.5
    if response['status'] == 'success':
        while True:
            prompt = input("Enter a prompt for GPT-3.5 (type 'exit' to end): ")
            
            # Send the prompt to the server
            client_socket.send(pickle.dumps({'prompt': prompt}))

            # Receive the GPT-3.5 response from the server
            gpt_response = client_socket.recv(1024).decode()
            print(f"GPT-3.5 Response: {gpt_response}")

            if prompt.lower() == 'exit':
                break

    # Close the client socket
    client_socket.close()

def main():
    username = input("Enter username: ")
    password = input("Enter password: ")

    authenticate(username, password)

if __name__ == "__main__":
    main()