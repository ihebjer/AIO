import socket
from threading import Thread
import time

class Client:
    def __init__(self, host, port, reader: callable = None):
        self.sock = socket.socket()
        self.sock.connect((host, port))
        self.receive_flag = True
        self.reader = reader
        self.receive_thread = Thread(target=self.receive)
        self.receive_thread.start()

    def receive(self):
        while self.receive_flag:
            try:
                data = self.sock.recv(2048).decode()
                if self.reader and data:
                    self.reader(data)
                time.sleep(0.01)
            except Exception as e:
                print(f"Error receiving data: {e}")

    def stop(self):
        self.receive_flag = False
        self.sock.close()