# client
import socket
import time

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 11111))

while True:
    cRequest = input("send: ")
    client.send(cRequest.encode())
    if cRequest == "quit":
        print("[+] Down line......")
        time.sleep(2)
        client.close()
        break