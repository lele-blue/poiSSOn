import socket
import requests

# Set up a TCP/IP server
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
apikey = "bYF3FS3u.0a7wtqoyWT0VRmVQnoMpYOaP1c2pWfHp"
sso_url = "http://localhost:8001"
service_name = "TestServiceExt"

# Bind the socket to server address and port 81
server_address = ('localhost', 8372)
tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_socket.bind(server_address)

# Listen on port 81
tcp_socket.listen(1)

while True:
    print("Waiting for connection")
    connection, client = tcp_socket.accept()

    try:
        print("Connected to client IP: {}".format(client))

        # Receive and print data 32 bytes at a time, as long as the client is sending something
        while True:
            data = connection.recv(32)
            print("Received data: {}".format(data))

            operation, key = str(data, "ascii").strip().split(" ")

            if operation == "get":
                localpart, domain  = key.split("@")
                resp = requests.get(f"{sso_url}/auth/api/configuration/management/{service_name}/by_keys?localpart={localpart}&domain={domain}", headers={"Authorization": f"Api-Key {apikey}"})
                json = resp.json()
                if len(json) == 0:
                    connection.send("500 Not found\n".encode("ascii"))
                elif resp.status_code == 200:
                    connection.send(f"200 {json[0]['_username']}/{json[0]['localpart']}@{json[0]['domain']}/\n".encode("ascii"))
                elif 400 <= resp.status_code <= 499:
                    connection.send("500 Not found\n".encode("ascii"))
                else:
                    connection.send("400 Error\n".encode("ascii"))

            if not data:
                break

    finally:
        connection.close()
