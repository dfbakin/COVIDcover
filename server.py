import socket, threading
from time import sleep
from sys import argv

players = dict()


def operate_connection():
    while True:
        try:
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
        except Exception:
            con.close()
            continue


def clean_params():
    while True:
        global players
        players = dict()
        sleep(5)


host = '0.0.0.0'

if len(argv) <= 1:
    port = input('enter the port:    ').strip()
    if not port.isdigit():
        raise ValueError
    port = int(port)
    print(f'starting server on {str(port)} port')
    a = input('confirm, please')
else:
    if not argv[1].isdigit():
        raise ValueError
    port = int(argv[1])

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

clean_thread = threading.Thread(target=clean_params)
clean_thread.start()
