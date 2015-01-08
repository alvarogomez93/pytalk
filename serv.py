import sys
import termios
import tty

__author__ = 'alvarogomez93'

import ssh
import threading
import socket
import os

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Server(ssh.ServerInterface):
    def check_auth_password(self, username, password):
        if (username == "test") and (password == "test"):
            return ssh.AUTH_SUCCESSFUL
        else:
            return ssh.AUTH_FAILED
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return ssh.OPEN_SUCCEEDED

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth,
                                  pixelheight, modes):
        return True

    def __init__(self):
        self.event = threading.Event()







def windows_shell(chan):
    import threading

    chan.send("---Escribe escribe---.\r\n")

    def writeall(sock):
        while True:
            data = sock.recv(256)
            sys.stdout.write(data)
            if data == '\r' or '\n' == data:
                chan.send("\r\n")
                print '\r\n',
            chan.send(bcolors.OKGREEN+data+bcolors.ENDC)

    writer = threading.Thread(target=writeall, args=(chan,))
    writer.start()

#Inicializacion, binding al puerto 3000
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', 3000))

if os.path.exists("id_rsa"):
    rsallave = ssh.RSAKey(filename="id_rsa")
else:
    print "Generando llave del servidor "+bcolors.FAIL+"NO LA PIERDAS"+bcolors.ENDC
    nuevallave = ssh.RSAKey.generate(1024)
    nuevallave.write_private_key(open("id_rsa", 'w'), password=None)
    rsallave = ssh.RSAKey(filename="id_rsa")


while True:
    try:
        sock.listen(100)
        client, addr = sock.accept()
    except Exception as e:
        sys.exit(1)


    print "Conexion establecida"
    t = ssh.Transport(client)
    servidor = Server()
    t.add_server_key(rsallave)
    t.start_server(server=servidor)

    conexion = t.accept(20)
    if conexion is None:
        print "No conexion"
        sys.exit(1)
    print "Autenticacion completa "+ t.get_username()

    servidor.event.wait(10)

    windows_shell(conexion)


