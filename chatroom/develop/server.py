import configparser
import socket
import sys
import os
import threading
import queue
import json
from until.logger import Logger

# 读取配置文件
config = configparser.ConfigParser()
config.read('config/config.ini')
# 输出日志
log = Logger(level='info').logger

que = queue.Queue()  # 用于存放客户端发送的信息的队列
users = []  # 用于存放在线用户的信息  [conn, user, addr]
lock = threading.Lock()  # 创建锁, 防止多个线程写入数据的顺序打乱


# 将在线用户存入online列表并返回
def onlines():
    online = []
    for i in range(len(users)):
        online.append(users[i][1])
    return online


class ChatServer(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.ADDR = (config.get('server', 'host'), port)
        os.chdir(sys.path[0])
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 用于接收所有客户端发送信息的函数
    def tcp_connect(self, conn, addr):
        # 连接后将用户信息添加到users列表
        user = conn.recv(1024)  # 接收用户名
        user = user.decode()

        for i in range(len(users)):
            if user == users[i][1]:
                log.info('User already exist')
                user = '' + user + '_2'

        if user == 'no':
            user = addr[0] + ':' + str(addr[1])
        users.append((conn, user, addr))
        log.info('新用户加入了聊天' + str(addr) + ':' + str(user))  # 打印用户名
        d = onlines()  # 有新连接则刷新客户端的在线用户显示
        self.recv(d, addr)
        try:
            while True:
                data = conn.recv(1024)
                data = data.decode()
                # print(data)
                log.info(user + '->' + data.split(':;')[2] + ':' + data.split(':;')[0])
                self.recv(data, addr)  # 保存信息到队列
            conn.close()
        except:
            log.info(user + '退出了聊天室')
            self.delUsers(conn, addr)  # 将断开用户移出users
            conn.close()

    # 判断断开用户在users中是第几位并移出列表, 刷新客户端的在线用户显示
    def delUsers(self, conn, addr):
        a = 0
        for i in users:
            if i[0] == conn:
                users.pop(a)
                d = onlines()
                self.recv(d, addr)
                log.info('剩下的人员' + str(d))  # 打印剩余在线用户(conn)
                break
            a += 1

    # 将接收到的信息(ip,端口以及发送的信息)存入que队列
    def recv(self, data, addr):
        lock.acquire()
        try:
            que.put((addr, data))
        finally:
            lock.release()

    # 将队列que中的消息发送给所有连接到的用户
    def sendData(self):
        while True:
            if not que.empty():
                data = ''
                message = que.get()  # 取出队列第一个元素
                if isinstance(message[1], str):  # 如果data是str则返回Ture
                    for i in range(len(users)):
                        # user[i][1]是用户名, users[i][2]是addr, 将message[0]改为用户名
                        for j in range(len(users)):
                            if message[0] == users[j][2]:
                                # log.info(str(message[1]).split(':;')[1] + ':' + str(message[1]).split(':;')[0])
                                data = ' ' + users[j][1] + '：' + message[1]
                        users[i][0].send(data.encode())
                # data = data.split(':;')[0]
                if isinstance(message[1], list):  # 同上
                    # 如果是list则打包后直接发送
                    data = json.dumps(message[1])
                    for i in range(len(users)):
                        try:
                            users[i][0].send(data.encode())
                        except:
                            pass

    def run(self):
        self.s.bind(self.ADDR)
        self.s.listen(5)
        log.info('聊天服务器开启 '+str(self.ADDR))
        # 这里开启一个新的线程 将数据发送给所有用户
        q = threading.Thread(target=self.sendData)
        q.start()
        while True:
            conn, addr = self.s.accept()
            # 接收服务端数据
            t = threading.Thread(target=self.tcp_connect, args=(conn, addr))
            t.start()
        self.s.close()

    ################################################################


if __name__ == '__main__':
    cserver = ChatServer(int(config.get('server', 'port')))
    cserver.start()
