import sys
import socket
from Queue import Queue
import re
import os
import math
from email import message
import re as regex
from threading import  Thread
from threading import Lock

r_lock = Lock()


#threading to handle multiple clients
class ClientThread(Thread):
    def __init__(self, clients):
        print(" client thread has been initialised")
        Thread.__init__(self)
        self.clients = clients

        self.start()

    def run(self):

        while True:
            (connection, address) = self.clients.get()
            # If connection exists process the message otherwise exit
            if connection:
                self.process_client_req(connection, address)

            else:
                break
#function to process client request

    def process_client_req(self, connection,address):


        while connection:
            line = ""
            while "\n\n" not in line:
                stored_value = connection.recv(1024)
                line += stored_value.decode()
                if len(stored_value)<1024:
                    break
#checking if stored_value has some data
            if len(stored_value)>0:
                print("Client's Message", line)
#processing chat request
                if line.startswith("CHAT"):
                    elements = regex.match( r"CHAT: ?(.*)(?:\s|\\n)JOIN_ID: ?(.*)(?:\s|\\n)CLIENT_NAME: ?(.*)(?:\s|\\n)MESSAGE: ?(.*)", line, regex.M)
                    if elements is not None:

                        r = None
                        r_lock.acquire()

                        try:
                            if elements.groups()[0] not in r_array:
                                send_error(error_msg, 5, connection, elements.groups()[0])
                                return
                            r = r_array[elements.groups()[0]]
                        finally:
                            r_lock.release()
                            r.sending_msg(elements.groups()[2], elements.groups()[3])
                    else:
                        send_error(error_msg, 1, connection)
#processing helo request
                if line.startswith("HELO"):

                    elements = regex.match(hello_msg, line, regex.M)
                    if elements is not None:

                        msg_client("HELO " + elements.groups()[0] + "\nIP:" + str(host) + "\nPort:" + str(port) + "\nStudentID:" + "16343086", connection)

                    else:
                        send_error(error_msg, 5, connection)
#processing leave chat_room
                if line.startswith("LEAVE_CHATROOM"):
                    elements = regex.match(r"LEAVE_CHATROOM: ?(.*)(?:\s|\\n)JOIN_ID: ?(.*)(?:\s|\\n)CLIENT_NAME: ?(.*)",
                                           line, regex.M)
                    if elements is not None:


                        r = None

                        # locking so that other threads doesnt interfere
                        r_lock.acquire()
                        try:

                            if elements.groups()[0] not in r_array:
                                send_error(error_msg + elements.groups()[0], 1, connection)
                                return

                            r = r_array[elements.groups()[0]]
                        finally:
                            # release the lock
                            r_lock.release()

                        # process to leave the chat room
                        msg_client("LEFT_CHATROOM: " + str(elements.groups()[0]) + "\nJOIN_ID: " + str(elements.groups()[1]),
                                           connection)
                        #  messaging other users that a particular user has left the chat room
                        r.sending_msg(elements.groups()[2], elements.groups()[2] + " has left this chatroom.")
                        #  deleting user details
                        r.removing_user(elements.groups()[1], elements.groups()[2], connection)

                    else:
                        send_error(error_msg, 5, connection)

                if line.startswith("JOIN_CHATROOM"):
                    elements = regex.match(join_msg, line, regex.M)
                    if elements is not None:

                        r_id = str(hash(elements.groups()[0]))
                        u_id = str(hash(elements.groups()[3]))
                        r_lock.acquire()
                        try:
                            if r_id not in r_array:
                                r_array[r_id] = chat_room(r_name=elements.groups()[0], r_id=r_id)
                            r = r_array[r_id]
                        finally:
                            r_lock.release()
                        print("Client joining the chatroom", elements.groups()[0], "user name", elements.groups()[3])
                        msg_client(r.adding_users(connection, port, host, u_id, elements.groups()[3]), connection)
                        r.sending_msg(elements.groups()[3], elements.groups()[3] + "has joined the chat room")


                    else:
                        send_error(error_msg, 5, connection)
# print Disconnect message if false return error
                if line.startswith("DISCONNECT"):

                    elements = regex.match(r"DISCONNECT: ?(.*)(?:\s|\\n)PORT: ?(.*)(?:\s|\\n)CLIENT_NAME: ?(.*)", line,
                                           regex.M)
                    if elements is not None:

                        r = []
                        u_id = str(hash(elements.groups()[2]))
                        print("Receieved: DISCONNECT from " + elements.groups()[2])
                        r_lock.acquire()
                        try:
                            r = r_array.values()
                        finally:
                            r_lock.release()

                        r = sorted(r, key=lambda x: x.r_name)
                        print(r)
                        for a in r:
                            a.disconnect_user(u_id, elements.groups()[2])

                    else:
                        send_error(error_msg, 5, connection)
                    connection.shutdown(1)
                    connection.close()

                if line == "KILL_SERVICE\n":
                    os._exit(0)


#broadcasting user message

    def broadcast_user(connection, r_id, u_id, u_name, m):
        r = None
        r_lock.acquire()

        try:
            if r_id not in r_array:
                send_error(error_msg, 5, connection, r_id)
                return
            r = r_array[r_id]
        finally:
            r_lock.release()
            r.messaging_client(u_name,m)

#function to create error message
def send_error(details, error_msg, connection):
    print("error code", str(error_msg), details)
    msg = "error message " + str(error_msg) + "\n error details " + details
    msg_client(msg,connection)

def msg_client(msg, connection):
    print(msg)
    if connection:
        connection.sendall((msg + "\n").encode())


class chat_room:


    def __init__(self, r_name, r_id):
        self.r_name = r_name
        self.r_id = r_id
        self.r_users = {}
        self.r_lock = Lock()


    def adding_users(self, connection, port, host, u_id, u_name ):
        self.r_lock.acquire()
        try:
            self.r_users[u_id] =(u_name, connection)
            print (len(self.r_users), self.r_users)

        finally:
            self.r_lock.release()
            print(self.r_name, host, port, self.r_id, u_id)
            return "JOINED_CHATROOM: " + self.r_name + "\nSERVER_IP: " + str(host) + "\nPORT: " + str(port) + "\nROOM_REF: " + str(self.r_id) + "\nJOIN_ID: " + str(u_id)


    def messaging_client(self, message, connection):
        print("Messaging client \n", message)
        if connection:
                connection.sendall((message + "\n").encode())

    def disconnect_user(self, u_id, u_name):
        self.r_lock.acquire()
        try:
            # check if user id is in chat room
            if u_id not in self.r_users:
                return
        finally:
            self.r_lock.release()
        # send disconnect message to all members in chatroom
        self.sending_msg(u_name, u_name + " has left this chatroom.")

        self.r_lock.acquire()
        try:
            # delete from array
            del self.r_users[u_id]
        finally:
            self.r_lock.release()

    def sending_msg(self, src, m):
        uc = []
        self.r_lock.acquire()
        try:
            uc = self.r_users.values()
        finally:
            self.r_lock.release()
        print(uc)
        print(len(self.r_users))
        for i_dest, j_conn in uc:
            print ("\"" + m + "\" to " + i_dest + " in " + self.r_name)
            msg_client("CHAT:" + str(self.r_id) + "\nCLIENT_NAME:" + src + "\nMESSAGE:" + m + "\n", j_conn)

    def removing_user(self, j_id, user , connection):
        print("user leaving" + self.r_name + user)
        self.r_lock.acquire()
        try:
            if j_id in self.r_users:
                if self.r_users[j_id][0]== user:
                    del self.r_users[j_id]
                else:
                    return
        finally:
            self.r_lock.release()




port = 8080
host = 'localhost'
clients = Queue()
r_array = {}

error_msg = "Invalid Message Format"
join_msg = r"JOIN_CHATROOM: ?(.*)\sCLIENT_IP: ?(.*)\sPORT: ?(.*)\sCLIENT_NAME: ?(.*)\s"
hello_msg = r"HELO ?(.*)"

#Main Function
def server_main():
    global  port
    server_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_s.bind((host, port))
    server_s.listen(2)

    while True:
        connection , address = server_s.accept()
        print(address)
        ClientThread(clients)
        clients.put((connection, address))




if __name__ == '__main__':
    server_main()







