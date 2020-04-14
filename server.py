import socket, threading
from time import sleep

players = dict()


def operate_connection(con: socket.socket):
    data = None
    while not data:
        data = con.recv(1024).decode('utf-8').split(r'\t')
    player_id, params = data[0], r'\t'.join(data[1:])
    players[player_id] = params

    for i in players.keys():
        if i == player_id:
            continue
        info = i + r'\t' + players[i]
        con.send(info.encode('utf-8'))
        sleep(0.002)
    con.send('end'.encode('utf-8'))

    con.close()


def run_server():
    host = '127.0.0.1'
    port = 9000
    so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    so.bind((host, port))
    so.listen(50)
    print("[OK] server started")
    while True:
        client, addr = so.accept()
        thread = threading.Thread(target=operate_connection, args=(client,))
        thread.start()
        thread.join(1)


run_server()
