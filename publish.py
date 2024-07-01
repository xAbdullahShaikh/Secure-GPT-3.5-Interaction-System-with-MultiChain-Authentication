import multizain
import getpass
import hashlib
import json
import binascii
import subprocess


# Connection details
rpcuser = "multichainrpc"
rpcpassword = "password"
rpchost = "127.0.0.1"
rpcport = "port"
chainname = "sehersidd"

# Create a MultiChain client instance
mc = multizain.MultiChainClient(rpchost, rpcport, rpcuser, rpcpassword)

def hash_password(password):
    # Use a secure hashing algorithm (e.g., SHA-256) to hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

def upload_data(stream_name, data):
    # Iterate through the data and publish to the stream
    for item in data:
        # Use the username as the key
        key = item['username']
        # Hash the password before storing it
        hashed_password = hash_password(item['password'])
        # Construct the data to publish as a JSON string
        data_to_publish = json.dumps({'username': item['username'], 'hashed_password': hashed_password})

        # Convert the data to hexadecimal
        hex_data = binascii.hexlify(data_to_publish.encode()).decode()

        # Build the command to publish
        command = f"d:\Multichain\multichain-cli.exe {chainname} publish {stream_name} {key} {hex_data}"

        # Execute the command
        try:
            result = subprocess.check_output(command, shell=True)
            print(result.decode())
        except subprocess.CalledProcessError as e:
            print(f"Error code: {e.returncode}")
            print(f"Error message: {e.output.decode()}")

    print(f"Data uploaded to the {stream_name} stream.")

# Ask the user for username and password
username = input("Enter username: ")
password = getpass.getpass("Enter password: ")

# Prepare the data to upload
data_to_upload = [{'username': username, 'password': password}]

# Upload the data to the 'users' stream
upload_data('userr', data_to_upload)