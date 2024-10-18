import socket
import json
import joblib  
import pandas as pd
import threading
import yaml 


with open('Config.yaml', 'r') as file:
    config = yaml.safe_load(file)


class TcpClient(threading.Thread):
    def __init__(self, host=config['tcp']['host'], port=config['tcp']['port'], callback=None):
        super().__init__()
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.callback = callback

    def run(self):
        try:
            self.client_socket.connect((self.host, self.port))
            print(f"Connected to server at {self.host}:{self.port}")
            while True:
                data = self.client_socket.recv(1024)  
                if data:
                    self.process_data(data)
        except Exception as e:
            print(f"Connection error: {e}")

    def process_data(self, data):
        message = data.decode()
        sensor_data = json.loads(message)

        if 'offset' in sensor_data:
            offset_values = sensor_data['offset']
            if self.callback:
                self.callback(offset_values)  
        else:
            print("No offset values received in the message.")


class SensorApp:
    def __init__(self, model, driving_mode=config['driving_mode']): 
        self.model = model
        self.driving_mode = driving_mode

        self.tcp_client = TcpClient(callback=self.predict_position)  
        self.tcp_client.start() 


    def predict_position(self, offset_values):
        sensor_data_dict = {
            'Sensor 1': int(offset_values[0]),
            'Sensor 2': int(offset_values[1]),
            'Sensor 3': int(offset_values[2]),
            'Sensor 4': int(offset_values[3]),
            'Sensor 5': int(offset_values[4]),
            'Sensor 6': int(offset_values[5]),
            'Sensor 7': int(offset_values[6]),
            'Sensor 8': int(offset_values[7]),            
            'Sensor 9': int(offset_values[8]),
            'Sensor 10': int(offset_values[9]),
            'DrivingModeEncoded': self.driving_mode  
        }

        sensor_data_df = pd.DataFrame(sensor_data_dict, index=[0])  
        prediction = self.model.predict(sensor_data_df)
        print(f"Position: {prediction[0]}")


if __name__ == '__main__':
    model_path = config['model']['path']  
    model = joblib.load(model_path)  
    app = SensorApp(model)
