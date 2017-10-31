import sys
from socket import *
import queue

from threading import  Thread

port = 9009
host = ''

def server_main():
    server_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_s.bind((host, port))
    server_s.listen(1)

    while True:
        connection , address = server_s.accept()
        print(address)
        data = connection.recv(1024)
        print  ("recieved", repr(data))
        reply = raw_input("Reply : ")
        connection.sendall(reply)
    connection.close()







