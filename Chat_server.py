import sys
import socket
import queue
import re
import os
import math
from email import message
import re as regex


from threading import  Thread

port = 8080
host = 'localhost'


error_5 = "Invalid Message Format"
join_msg = r"JOIN_CHATROOM: ?(.*)\sCLIENT_IP: ?(.*)\sPORT: ?(.*)\sCLIENT_NAME: ?(.*)\s"
hello_msg = r"HELO ?(.*)"







#threading to handle multiple clients
class ClientThread(Thread):
    def __init__(self, clients):
        print(" Initialization of clients thread")
        self.clients = clients
        self.daemon = True
        self.start()

    def run(self):
        while True:
            (connection, address) = self.clients.get()
            # If connection object exists process message otherwise exit
            if connection:
                self.process_client_req(connection, address)
            else:
                break

def process_client_req(connection,address):

    while connection:
        msg = ""
        while "\n\n" not in msg:
            stored_value = connection.recv(1024)
            msg += stored_value.decode()
            if len(stored_value)<1024:
                break

        if len(stored_value)>0:
            #there is somedata
            print("MESSAGE FROM CLIENT->"), regex.escape(msg)
            if msg.startswith("HELO"):
                hello(connection, msg, address)
            if msg.startswith("JOIN_CHATROOM"):
                join(connection, msg)

def chat_room(connection, rname , user_name):
    r_id = str(int(hashlib.md5(chat_room).hexdigest(), 16))
    user_id = str(int(hashlib.md5(user_name).hexdigest(), 16))


def hello():
    elements = regex.match(hello_msg, msg, regex.M)
    if elements is not None:
        msg_client("HELO " + elements.groups()[0] + "\nIP:" + str(address[0]) + "\nPort:" + str(
            address[1]) + "\nStudentID:" + "16343086", connection)

    else:
        error_client(error_5, 5, connection)



def join(connection, msg):
    elements = regex.match(join_msg, msg, regex.M)
    if elements is not None:
        msg_client("HELO " + elements.groups()[0] + "\nIP:" + str(address[0]) + "\nPort:" + str(
            address[1]) + "\nStudentID:" + "16343086", connection)

    else:
        error_client(error_5, 5, connection)




#Main Function
def server_main():
    global  port
    server_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(host, socket.gethostname())
    server_s.bind((host, port))
    server_s.listen(2)

    while True:
        connection , address = server_s.accept()
        print(address)
        ClientThread(clients)




if __name__ == '__main__':
    server_main()







