import socket
import threading

host = socket.gethostbyname(socket.gethostname())
port = 65534

nickname = input("Choose your nickname: ")
if nickname == "admin":
    password = input("Enter the password : ")

client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_sock.connect((host, port))

stop_thread = False


def receive():
    while True:
        global stop_thread
        if stop_thread:
            break
        try:
            message = client_sock.recv(1024).decode('ascii')
            if message == 'NICK':
                client_sock.send(nickname.encode('ascii'))
                nxt_msg = client_sock.recv(1024).decode("ascii")
                if nxt_msg == "PSD":
                    client_sock.send(password.encode("ascii"))
                    if client_sock.recv(1024).decode("ascii") == "REFUSE":
                        print("Connection refused wrong password")
                        stop_thread = True

                elif nxt_msg == "BAN":
                    print("Connection refused because of Ban")
                    client_sock.close()
                    stop_thread = True

            else:
                print(message)

        except:
            # Close Connection When Error
            print("An error occurred!")
            client_sock.close()
            break


def write():
    while True:
        if stop_thread:
            break
        message = '{}: {}'.format(nickname, input(''))
        if message[len(nickname)+2:].startswith("/"):
            if nickname == "admin":
                if message[len(nickname)+2:].startswith("/kick"):
                    client_sock.send(f"KICK {message[len(nickname)+2+6:]}".encode("ascii"))
                elif message[len(nickname)+2:].startswith("/ban"):
                    client_sock.send(f"BAN {message[len(nickname)+2+5:]}".encode("ascii"))
            else:
                print("Command can only be executed by Admin")
        else:
            client_sock.send(message.encode('ascii'))


receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
