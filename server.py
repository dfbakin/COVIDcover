import socket
from time import sleep, time

players = dict()


def operate_connection(con: socket.socket):
    #print(players)
    data = None
    while not data:
        data = con.recv(1024).decode('utf-8').split(r'\t')
    player_id, params = data[0], r'\t'.join(data[1:])
    players[player_id] = params

    for i in players.keys():
        if i == player_id:
            continue
        info = i + r'\t' + players[i]
        #print(player_id, params)
        #print(players)
        #print(info)
        con.send(info.encode('utf-8'))
        sleep(0.005)
    con.send('end'.encode('utf-8'))

    con.close()


def main():
    host = '127.0.0.1'
    port = 9000
    so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    so.bind((host, port))
    so.listen(10)
    print("server started.")
    while True:
        conn, addr = so.accept()
        #print("client connected IP:<" + str(addr) + ">")
        operate_connection(conn)


if __name__ == '__main__':
    main()
