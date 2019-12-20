import configparser
import datetime
import os
import select
import socket as s
import sys
from until.logger import Logger
from until.mysql_until import Dao
# 读取配置文件
config = configparser.ConfigParser()
config.read('config/config.ini')
# 日志
base_dir = os.path.dirname(__file__)
path = os.path.join(base_dir, (config.get('log', 'path') + datetime.datetime.now().strftime('%Y-%m-%d') + '.log'))
if not os.path.exists(path):
    fd = open(path, mode="w", encoding="utf-8")
    fd.close()
log = Logger(path, level='info').logger


if __name__ == '__main__':
    # 建立服务器端socket
    server_socket = s.socket(s.AF_INET, s.SOCK_STREAM)
    server_socket.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
    server_socket.bind((config.get('server', 'host'), int(config.get('server', 'port'))))
    server_socket.listen(5)
    connection_list = [server_socket]
    online = {}
    online_name = {}
    connection_list.append(server_socket)
    log.info("Chat server started on port " + config.get('server', 'port'))
    running = True
    while running:
        # select函数阻塞程序运行，监控connection_list中的套接字，当其中有套接字满足可读的条件
        # （第一个参数为可读，如果是第二个参数则为可写），则把这个套接字返回给read_sockets，然后程序继续运行。
        read_sockets, write_sockets, error_sockets = select.select(connection_list, [], [])
        for sock in read_sockets:
            if sock == server_socket:
                connection, addr = server_socket.accept()
                connection_list.append(connection)
                message = "Client (%s) connected\t" % addr
                log.info(message)
                tc = Dao("record")
                tc.write_db(message)
            # elif sock == sys.stdin:
            #     junk = sys.stdin.readline()
            #     if junk == "exit":
            #         running = False
            #     else:
            #         broadcast_data(sock, "testing\n")
            # else:
            #     try:
            #         data = sock.recv(config.get('server', 'recv_buffer'))
            #         logout_flag = False
            #         if data:
            #             redata = parse_data(sock, data.decode().rstrip()) + "\n"
            #             sock.send(redata.encode())
            #             if logout_flag:
            #                 offline(sock)
            #         else:
            #             offline(sock)
            #     except Exception as e:
            #         offline(sock)
