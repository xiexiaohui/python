#!/usr/bin/python3

import socket
import select

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('', 9981))
server_socket.listen(5)
#server_socket.setblocking(0)
poll = select.poll()
poll.register(server_socket.fileno(), select.POLLIN)

connections = {}
while True:
    events = poll.poll(10000)
    for fileno, event in events:
        if fileno == server_socket.fileno():
            (client_socket, client_address) = server_socket.accept()
            print ("got connection from", client_address)
            #client_socket.setblocking(0)
            poll.register(client_socket.fileno(), select.POLLIN)
            connections[client_socket.fileno()] = client_socket
        elif event & select.POLLIN:
            client_socket = connections[fileno]
            data = client_socket.recv(4096)
            if data:
                client_socket.send(data)
                for fd, other_socket in connections.items():
                    if other_socket != client_socket:
                        other_socket.send(data)
            else:
                poll.unregister(fileno)
                client_socket.close()
                del connections[fileno]
