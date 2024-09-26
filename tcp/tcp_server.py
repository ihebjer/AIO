import socket
import json
import time
from threading import Thread

aio_data_template   = "/home/ihebjeridi/Documents/app - OOP/app_acquisation/tcp/aio_data.json"
host                = '127.0.0.1'
port                = 5342
interval            = 0.1  
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data
class TCPServer:
    MSG_DELIMITER = '\n'
    def __init__(self, host, port, data_template_path, interval=0.1):
        self.host = host
        self.port = port
        self.interval = interval
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}")
        self.aio_data = read_json_file(data_template_path)
        self.is_server_active = True
        self.clients = []

        run_thread = Thread(target=self.start)
        run_thread.start()

    def handle_client(self, client_socket):
        try:
            while True:
                data = self.aio_data  
                json_data = json.dumps(data) + TCPServer.MSG_DELIMITER
                client_socket.sendall(json_data.encode('utf-8'))
                time.sleep(self.interval)
        except ConnectionResetError:
            print("Client disconnected")
        except Exception as e:
            print("Error occurred....", e)
        finally:
            client_socket.close()

    def receive_thread(self, client_socket):
        try:
            while True:
                received_data = client_socket.recv(1024).decode('utf-8')
                if received_data:
                    print(f"Received data from client: {received_data}")
                time.sleep(0.1)  
        except ConnectionResetError:
            print("Client disconnected")
        finally:
            client_socket.close()

    def start(self):
        try:
            while self.is_server_active:
                client_socket, addr = self.server_socket.accept()
                self.clients.append(client_socket)
                client_handler = Thread(target=self.handle_client, args=(client_socket,))
                client_handler.start()
                receive_thread = Thread(target=self.receive_thread, args=(client_socket,))
                receive_thread.start()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.is_server_active = False
        self.server_socket.close()
        for client_socket in self.clients:
            client_socket.close()
        print("Server stopped")



if __name__ == "__main__":
    is_main_loop =  True
    server = TCPServer(host, port, aio_data_template, interval)

    try:
        while is_main_loop:
            _input = input('>>')
            if _input == "help":
                for i,k in enumerate(server.aio_data):
                    print(f'{i}: {k} -> {server.aio_data[k]}')
                print("example to update pelvis_alarm  <pelvis_alarm=0>")
            elif _input == "quit" or _input == "q":
                is_main_loop = False
                server.is_server_active = False
                exit(0)
            else:
                try:
                    k,v = _input.split("=")
                    k= k.strip()
                    v = v.strip()
                    if server.aio_data.get(k) is not None:
                        server.aio_data[k] = int(v)
                    else: print('Key does not exist, No update done...')
                except Exception as e:
                    print("Error while parsing key, value ",e)

    except KeyboardInterrupt:
        is_main_loop = False
        server.is_server_active = False





