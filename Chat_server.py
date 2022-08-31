import socket
import threading

host = socket.gethostbyname(socket.gethostname())
port = 65534
serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv_sock.bind((host, port))
serv_sock.listen()

clients = []
nicknames = []


def broadcast(msg):
    for client in clients:
        client.send(msg)


def handle_clients(client):
    while True:
        try:
            msg = client.recv(1024)
            if msg.decode("ascii").startswith("KICK"):
                if nicknames[clients.index(client)] == "admin":
                    name = msg.decode('ascii')[5:]
                    if name == "admin":
                        name_index = nicknames.index(name)
                        client_to_kick = clients[name_index]
                        client_to_kick.send("You cannot Ban or Kick admin".encode("ascii"))
                    else:
                        kick_user(name)
                else:
                    client.send("Command was refused".encode("ascii"))

            elif msg.decode("ascii").startswith("BAN"):
                if nicknames[clients.index(client)] == "admin":
                    name_to_ban = msg.decode("ascii")[4:]
                    if name_to_ban == "admin":
                        name_index = nicknames.index(name_to_ban)
                        client_to_kick = clients[name_index]
                        client_to_kick.send("You cannot Ban or Kick admin".encode("ascii"))
                    else:
                        kick_user(name_to_ban)
                        with open("bans.txt", 'a') as f:
                            f.write(f"{name_to_ban}\n")
                        print(f'{name_to_ban} was Banned')
                else:
                    client.send("Command was refused".encode("ascii"))
            else:
                broadcast(msg)

        except:
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast(f"{nickname} left the chat".encode('ascii'))
                nicknames.remove(nickname)
                break


def recv():
    while True:
        client, addr = serv_sock.accept()
        print(f"Client {addr[0]}:{addr[1]} connected with", end=" ")
        client.send("NICK".encode('ascii'))
        nickname = client.recv(1024).decode('ascii')

        with open("bans.txt", "r") as f:
            ban_list = f.readlines()

        if nickname + '\n' in ban_list:
            client.send("BAN".encode("ascii"))
            client.close()
            continue

        if nickname == "admin":
            client.send("PSD".encode("ascii"))
            password = client.recv(1024)

            if password.decode("ascii") != "admin":
                print(f'pass recv:{password}')
                client.send("REFUSE".encode("ascii"))
                client.close()
                continue

        nicknames.append(nickname)
        clients.append(client)
        print("name {}".format(nickname))
        client.send('Connected to server!'.encode('ascii'))
        broadcast("{} joined the chat!".format(nickname).encode('ascii'))

        thread = threading.Thread(target=handle_clients, args=(client,))
        thread.start()


def kick_user(name):

    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send("You were kicked by admin".encode("ascii"))
        client_to_kick.close()
        nicknames.remove(name)
        broadcast(f"{name} was kicked by admin".encode("ascii"))


print(f"Server is running on {host}:{port}")
recv()
