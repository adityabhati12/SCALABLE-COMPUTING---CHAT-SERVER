from socket import *
host = ""
port = 9009
server_s = socket(AF_INET, SOCK_STREAM)
server_s.connect((host , port))

while true:
    message = raw_input("Message")
    server_s.send(message)
    print("Awaiting reply")
    reply = server_s.recv(1024)#max data that can be recieved
    print(" recieved" , repr(reply))

server_s.close()



