import socket, threading
from time import sleep

players = dict()


def operate_connection():
    while True:
        con, addr = so.accept()
        data = None
        while not data:
            data = con.recv(1024).decode('utf-8').split(r'\t')
        player_id, params = data[0], r'\t'.join(data[1:])
        players[player_id] = params

        data = players.copy()
        for i in data.keys():
            if i == player_id:
                continue
            info = i + r'\t' + data[i]
            con.send(info.encode('utf-8'))
            sleep(0.002)
        con.send('end'.encode('utf-8'))
        con.close()


host = '127.0.0.1'
port = 9000
so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
so.bind((host, port))
so.listen(50)
print("[OK] server started")

thread_1 = threading.Thread(target=operate_connection)
thread_1.start()

thread_2 = threading.Thread(target=operate_connection)
thread_2.start()

thread_3 = threading.Thread(target=operate_connection)
thread_3.start()

thread_4 = threading.Thread(target=operate_connection)
thread_4.start()
