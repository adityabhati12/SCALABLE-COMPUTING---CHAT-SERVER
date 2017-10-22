import sys
import socket
import queue

from threading import  Thread

port = 9009
host = ''

def server_main():
    server_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_s.bind((host, port))
    server_s.listen(10)

    while True:
        connection , address = server_s.accept()


if __name__ == "__main__":
    server_main()

