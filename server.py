import socket
import pickle
import openai  # Make sure to import the openai library
import multizain
import binascii
import json
import hashlib

# Set your OpenAI API key
openai.api_key = '{privately owned key }'

# Connection details for MultiChain
rpcuser = "multichainrpc"
rpcpassword = "password"
rpchost = "127.0.0.1"
rpcport = "port"
chainname = "sehersidd"

# Create a MultiChain client instance
mc = multizain.MultiChainClient(rpchost, rpcport, rpcuser, rpcpassword)

def retrieve_password(username):
    try:
        # Retrieve data from MultiChain based on username (key)
        result = mc.liststreamitems('users')
        for item in result:
            item_data = binascii.unhexlify(item['data']).decode()
            parsed_data = json.loads(item_data)

            # Check if the current item's key matches the input username
            if parsed_data.get('username') == username:
                retrieved_password = parsed_data.get('hashed_password')
                print(f"Retrieved password for {username}: {retrieved_password}")
                
                # Print both the retrieved password and the hashed password in lowercase
                # print(f"Retrieved password (lowercase): {retrieved_password.lower()}")
                return retrieved_password.lower()

    except multizain.exceptions.RPCError as e:
        print(f"MultiChain RPC Error: {e}")
    return None

def authenticate_user(username, password):
    # Retrieve hashed password from MultiChain based on username
    stored_password = retrieve_password(username)

    # Check if the provided password matches the stored hashed password
    if stored_password:
        # Hash the received password using the same algorithm (e.g., SHA-256)
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        # print(f"Hash of password received from client: {hashed_password}")
        # print(f"Retrieved password from MultiChain (lowercase): {stored_password}")

        if hashed_password.lower() == stored_password.lower():
            print("Authentication successful")
            return True
        else:
            print("Authentication failed: Hashed passwords do not match")
    else:
        print("Authentication failed: Username not found in MultiChain")

    return False

def interact_with_gpt(prompt):
    # Interact with GPT-3.5 based on the received prompt
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.7,
        max_tokens=150
    )
    gpt_response = response.choices[0].text.strip()

    return gpt_response

def handle_client(client_socket):
    try:
        # Receive authentication credentials from the client
        data = client_socket.recv(1024)
        credentials = pickle.loads(data)

        # Check authentication
        username = credentials['username']
        password = credentials['password']
        if authenticate_user(username, password):
            response = {'status': 'success', 'message': 'Authentication successful'}
        else:
            response = {'status': 'failure', 'message': 'Authentication failed'}

        # Send the authentication result back to the client
        client_socket.send(pickle.dumps(response))

        # If authentication is successful, receive and process GPT-3.5 prompts
        if response['status'] == 'success':
            while True:
                prompt_data = client_socket.recv(1024)
                prompt = pickle.loads(prompt_data)['prompt']

                if prompt.lower() == 'exit':
                    break

                # Interact with GPT-3.5 based on the received prompt
                gpt_response = interact_with_gpt(prompt)

                # Send the GPT-3.5 response back to the client
                client_socket.send(gpt_response.encode())

    except Exception as e:
        print(f"Error handling client: {str(e)}")
    finally:
        # Close the client socket
        client_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('172.16.7.67', 12345))
    server_socket.listen(5)

    print("Server listening on port 12345")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")
        handle_client(client_socket)

if __name__ == "__main__":
    main()