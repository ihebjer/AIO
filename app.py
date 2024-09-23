import tkinter as tk
from tkinter import ttk, messagebox
import json
import serial
import csv
import socket
import time
from threading import Thread
import yaml

class App:
    def __init__(self, root):
        self.load_config('config.yaml')
        self.root = root
        self.root.title("FORVIA DATA ACQUISITION")
        self.root.geometry("800x600")
        self.root.resizable(True, False)
        self.data = {
            "occupants": {},
            "seat_details": {},
            "seat_positioning": {} ,
            "sensors": {},
            "environment": {},
            # Initialize for seat positioning data
        }
        self.sensor_data = []
        self.tabControl = ttk.Notebook(root)

        # Create Tabs
        self.occupant_tab = ttk.Frame(self.tabControl)
        self.seat_tab = ttk.Frame(self.tabControl)
        self.positioning_tab = ttk.Frame(self.tabControl)  # New tab for seat positioning
        self.sensor_tab = ttk.Frame(self.tabControl)
        self.environment_tab = ttk.Frame(self.tabControl)
        self.send_tab = ttk.Frame(self.tabControl)

        # Add Tabs to Notebook
        self.tabControl.add(self.occupant_tab, text="Occupant")
        self.tabControl.add(self.seat_tab, text="Seat details")
        self.tabControl.add(self.positioning_tab, text="Seat Positioning")  # Added tab
        self.tabControl.add(self.sensor_tab, text="Sensors")
        self.tabControl.add(self.environment_tab, text="Environment")
        self.tabControl.add(self.send_tab, text="Send")

        self.tabControl.pack(expand=1, fill="both")
        self.create_occupant_tab()
        self.create_seat_tab()
        self.create_positioning_tab()  # Create the positioning tab
        self.create_sensor_tab()
        self.create_environment_tab()
        self.create_send_tab()

        self.tcp_client = Client(host=self.host, port=self.port, reader=self.tcp_reader)
        self.offset_data = None
        self.current_position = 0
        self.logging = False
        self.log_thread = None 

    def load_config(self, file_path):
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
            self.host = config['host']
            self.port = config['port']
            global seat_data
            seat_data = config['seat_data']

    def configure_grid(self, tab, rows, columns):
        for i in range(rows):
            tab.grid_rowconfigure(i, weight=1)
        for j in range(columns):
            tab.grid_columnconfigure(j, weight=1)

    def create_occupant_tab(self):
        labels = ["ID_Occupant", "Age", "Weight", "Height", "Gender", "Ocuppant Classification"]
        self.configure_grid(self.occupant_tab, len(labels) + 1, 2)
        self.occupant_entries = {}
        for i, label in enumerate(labels):
            tk.Label(self.occupant_tab, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            if label == "Gender":
                entry = ttk.Combobox(self.occupant_tab, values=["H", "F"], state="readonly")
            else:
                entry = tk.Entry(self.occupant_tab)
                
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            self.occupant_entries[label] = entry

        self.occupant_entries["Weight"].bind("<KeyRelease>", self.update_weight_class)
        self.occupant_entries["Height"].bind("<KeyRelease>", self.update_weight_class)

        style = ttk.Style()
        style.configure("TButton", foreground="black", background="blue")

        ttk.Button(self.occupant_tab, text="Save", command=self.save_occupant, style="TButton").grid(row=len(labels), column=0, columnspan=2, pady=10)
        
    def update_weight_class(self, event):
        try:
            weight = float(self.occupant_entries["Weight"].get())
            age = float(self.occupant_entries["Age"].get())
            height = float(self.occupant_entries["Height"].get())
            if 13.3 <= weight <= 25.7 and 88.9 <= height <= 124.5 and 3 <= age <= 6:
                self.occupant_entries["Ocuppant Classification"].delete(0, tk.END)
                self.occupant_entries["Ocuppant Classification"].insert(0, "CHILD")
            elif 35 <= weight <= 42 and 128 <= height <= 136:
                self.occupant_entries["Ocuppant Classification"].delete(0, tk.END)
                self.occupant_entries["Ocuppant Classification"].insert(0, "GREY ZONE 1")
            elif 46.8 <= weight <= 51.3 and 139.7 <= height <= 160:
                self.occupant_entries["Ocuppant Classification"].delete(0, tk.END)
                self.occupant_entries["Ocuppant Classification"].insert(0, "5-TH Percentile")
            elif 51.3 <= weight <= 76.3 and 161 <= height <= 172:
                self.occupant_entries["Ocuppant Classification"].delete(0, tk.END)
                self.occupant_entries["Ocuppant Classification"].insert(0, "GREY ZONE 2")
            elif 76.3 <= weight <= 80.8 and 173 <= height <= 182:
                self.occupant_entries["Ocuppant Classification"].delete(0, tk.END)
                self.occupant_entries["Ocuppant Classification"].insert(0, "50-TH Percentile")
            else:
                self.occupant_entries["Ocuppant Classification"].delete(0, tk.END)
                self.occupant_entries["Ocuppant Classification"].insert(0, "Not Classified") 
        except ValueError:
            self.occupant_entries["Ocuppant Classification"].delete(0, tk.END)  

    def save_occupant(self):
        try:
            age = int(self.occupant_entries["Age"].get())
            if age < 0:
                raise ValueError("Age must be a positive integer.")
            
            weight = float(self.occupant_entries["Weight"].get())
            height = float(self.occupant_entries["Height"].get())
            gender = self.occupant_entries["Gender"].get()

            if gender not in ["H", "F"]:
                raise ValueError("Gender must be 'H' or 'F'.")

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return
        
        self.data["occupants"] = {label: entry.get() for label, entry in self.occupant_entries.items()}
        print("Occupant data saved:", self.data["occupants"])

    def create_seat_tab(self):
        self.seat_entries = {
            "SeatID": tk.Entry(self.seat_tab),
            "SeatName": tk.Entry(self.seat_tab),
            "sensor_numbers_backrest": tk.Entry(self.seat_tab),
            "SensorNumbersCushion": tk.Entry(self.seat_tab),
            "CushionWidth": tk.Entry(self.seat_tab),
            "FoamMaterial": tk.Entry(self.seat_tab),
            "CushionFoamThickness": tk.Entry(self.seat_tab),
            "BackrestFoamThickness": tk.Entry(self.seat_tab),
            "BolsterCoverMaterial": tk.Entry(self.seat_tab),
            "CushionCoverMaterial": tk.Entry(self.seat_tab),
            "BackrestCoverMaterial": tk.Entry(self.seat_tab)
        }

        self.configure_grid(self.seat_tab, len(self.seat_entries) + 1, 2)
        row = 0
        for label, entry in self.seat_entries.items():
            tk.Label(self.seat_tab, text=label).grid(row=row, column=0, padx=10, pady=5, sticky="ew")
            entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
            row += 1
        self.seat_entries["SeatID"].bind("<FocusOut>", self.update_seat_details)
        ttk.Button(self.seat_tab, text="Save", command=self.save_seat, style="TButton").grid(row=row, column=0, columnspan=2, pady=10)

    def update_seat_details(self, event):
        seat_id = self.seat_entries["SeatID"].get()
        seat_info = seat_data.get(seat_id)  
        if seat_info:  
            self.seat_entries["SeatName"].delete(0, tk.END)
            self.seat_entries["SeatName"].insert(0, seat_info["SeatName"])
            for field in ["sensor_numbers_backrest", "SensorNumbersCushion", "CushionWidth", 
                          "FoamMaterial", "CushionFoamThickness", "BackrestFoamThickness", 
                          "BolsterCoverMaterial", "CushionCoverMaterial", "BackrestCoverMaterial"]:
                self.seat_entries[field].delete(0, tk.END)
                self.seat_entries[field].insert(0, seat_info[field])
        else:
            for field in self.seat_entries:
                self.seat_entries[field].delete(0, tk.END)

    def save_seat(self):
        self.data["seat_details"] = {label: entry.get() for label, entry in self.seat_entries.items()}
        print("Seat data saved:", self.data["seat_details"])

    def create_sensor_tab(self):
        self.sensor_labels = [f"Sensor {i + 1}" for i in range(10)]
        self.sensor_entries = {label: tk.Label(self.sensor_tab, text="0.0") for label in self.sensor_labels}
        
        tk.Label(self.sensor_tab, text="Out of Position").grid(row=len(self.sensor_labels), column=0, padx=10, pady=5, sticky="ew")
        self.out_of_position_entry = ttk.Combobox(self.sensor_tab, values=[
            "Nominal position", "Foot underneath", "Pretzel", 
            "Hold the knees", "Pelvis drift", "Feet on the dashboard"
        ])
        self.out_of_position_entry.grid(row=len(self.sensor_labels), column=1, padx=10, pady=5, sticky="ew")
        
        tk.Label(self.sensor_tab, text="Timer:").grid(row=len(self.sensor_labels) + 1, column=0, padx=10, pady=5, sticky="ew")
        self.timer_label = tk.Label(self.sensor_tab, text="00:00:00")
        self.timer_label.grid(row=len(self.sensor_labels) + 1, column=1, padx=10, pady=5, sticky="ew")
        
        self.configure_grid(self.sensor_tab, len(self.sensor_labels) + 4, 2)

        for i, label in enumerate(self.sensor_labels):
            tk.Label(self.sensor_tab, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            self.sensor_entries[label].grid(row=i, column=1, padx=10, pady=5, sticky="ew")

        self.status_label = tk.Label(self.sensor_tab, text="Status: Not Started")
        self.status_label.grid(row=len(self.sensor_labels) + 2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        button_frame = ttk.Frame(self.sensor_tab)
        button_frame.grid(row=len(self.sensor_labels) + 3, column=0, columnspan=2, pady=10)

        self.start_button = ttk.Button(button_frame, text="Start Test", command=self.start_test, style="TButton")
        self.start_button.grid(row=0, column=0, padx=10)

        self.stop_button = ttk.Button(button_frame, text="Stop Test", command=self.stop_test, state=tk.DISABLED, style="TButton")
        self.stop_button.grid(row=0, column=1, padx=10)

        self.save_button = ttk.Button(button_frame, text="Save", command=self.save_sensor_data, style="TButton")
        self.save_button.grid(row=0, column=2, padx=10)

        ttk.Button(button_frame, text="Read from Serial", command=self.read_from_serial, style="TButton").grid(row=0, column=3, padx=10)
        ttk.Button(button_frame, text="Import from CSV", command=self.import_from_csv, style="TButton").grid(row=0, column=4, padx=10)

    def create_environment_tab(self):
        self.environment_entries = {
            "Temperature": tk.Entry(self.environment_tab),
            "Humidity": tk.Entry(self.environment_tab)
        }
        self.configure_grid(self.environment_tab, len(self.environment_entries) + 1, 2)
        row = 0
        for label, entry in self.environment_entries.items():
            tk.Label(self.environment_tab, text=label).grid(row=row, column=0, padx=10, pady=2, sticky="ew")  
            entry.grid(row=row, column=1, padx=10, pady=2, sticky="ew")  
            row += 1
        ttk.Button(self.environment_tab, text="Save", command=self.save_environment, style="TButton").grid(row=row, column=0, columnspan=2, pady=10)

    def create_send_tab(self):
        button_frame = ttk.Frame(self.send_tab)
        button_frame.pack(expand=True)
        ttk.Button(button_frame, text="Submit", command=self.submit_all, style="TButton").pack(side=tk.LEFT, padx=20, pady=10)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_all, style="TButton").pack(side=tk.LEFT, padx=20, pady=10)
        self.image = tk.PhotoImage(file="C:\\Users\\ijeridi\\Documents\\gui\\images\\faurecia_logo-removebg-preview.png")  
        image_label = tk.Label(self.send_tab, image=self.image)
        image_label.pack(side=tk.BOTTOM, pady=40)

    def create_positioning_tab(self):
        # Create entries for each seat positioning attribute
        self.positioning_entries = {
            "Backrest": tk.Entry(self.positioning_tab),
            "CushionTilt": tk.Entry(self.positioning_tab),
            "Track": tk.Entry(self.positioning_tab),
            "Height": tk.Entry(self.positioning_tab),
            "Uba": tk.Entry(self.positioning_tab),
        }

        # Configure the grid and populate the positioning tab
        self.configure_grid(self.positioning_tab, len(self.positioning_entries) + 1, 2)
        row = 0
        for label, entry in self.positioning_entries.items():
            tk.Label(self.positioning_tab, text=label).grid(row=row, column=0, padx=10, pady=5, sticky="ew")
            entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
            row += 1

        # Add a Save button
        ttk.Button(self.positioning_tab, text="Save", command=self.save_positioning_data, style="TButton").grid(row=row, column=0, columnspan=2, pady=10)

    def save_positioning_data(self):
        try:
            # Validate numeric input for Backrest, CushionTilt, Track, Height, Uba
            for field in ["Backrest", "CushionTilt", "Track", "Height", "Uba"]:
                value = float(self.positioning_entries[field].get())
                if value < 0:
                    raise ValueError(f"{field} must be a positive float.")
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return
        
        # Save the seat positioning data into the main data structure
        self.data["seat_positioning"] = {label: entry.get() for label, entry in self.positioning_entries.items()}
        print("Seat positioning data saved:", self.data["seat_positioning"])

    def read_from_serial(self):
        try:
            ser = serial.Serial('COM3', 9600)
            line = ser.readline().decode('utf-8').strip()
            ser.close()
            sensor_data = line.split(',')
            if len(sensor_data) == 10:  
                for i, label in enumerate(self.sensor_labels):
                    self.sensor_entries[label].config(text=sensor_data[i])
        except Exception as e:
            print(f"Error ::::::: reading from serial port: {e}")

    def import_from_csv(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, 'r') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) == 10: 
                        for i, label in enumerate(self.sensor_labels):
                            self.sensor_entries[label].config(text=row[i]) 

    def start_test(self):
        
        if not self.out_of_position_entry.get():
            messagebox.showwarning("Input Error", "Please enter position.")
            return  
        
        if self.offset_data is not None:
            for i, label in enumerate(self.sensor_labels):
                self.sensor_entries[label].config(text=self.offset_data[i])
                
            self.logging = True  
            self.start_time = time.time()  

            self.status_label.config(text="Status: Testing position {}".format(self.current_position + 1))
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.DISABLED)  
            
            self.log_thread = Thread(target=self.log_sensor_data, daemon=True)
            self.log_thread.start()
            self.timer_thread = Thread(target=self.update_timer, daemon=True)
            self.timer_thread.start()

    def stop_test(self):
        self.logging = False 
        self.start_button.config(state=tk.NORMAL)  
        self.stop_button.config(state=tk.DISABLED)  
        self.save_button.config(state=tk.NORMAL)  
        self.status_label.config(text="Status: Test stopped. Ready for next position.")
        self.timer_label.config(text="00:00:00") 
        self.start_time = None  
        
    def log_sensor_data(self):
        while self.logging:
            timestamp = time.strftime("%H:%M:%S")  
            current_out_of_position = self.out_of_position_entry.get()  
            sensor_values = {label: self.offset_data[i] for i, label in enumerate(self.sensor_labels)}

            self.sensor_data.append({
                "timestamp": timestamp,
                "position": self.current_position + 1,
                "status": "Empty",
                "out_of_position": current_out_of_position,
                **sensor_values
            })

            print("Logged data:", self.sensor_data[-1])  
            time.sleep(0.2)  
            
    def update_timer(self):
        while self.logging:
            if self.start_time is not None:
                self.elapsed_time = time.time() - self.start_time
                formatted_time = time.strftime("%H:%M:%S", time.gmtime(self.elapsed_time))
                self.timer_label.config(text=formatted_time)  
                time.sleep(1)  
        self.logging = False  
        self.start_button.config(state=tk.NORMAL)  
        self.stop_button.config(state=tk.DISABLED)  
        self.save_button.config(state=tk.NORMAL)  
        self.status_label.config(text="Status: Test stopped. Ready for next position.")
        self.timer_label.config(text="00:00:00")  
        self.start_time = None  

    def save_sensor_data(self):
        if not self.sensor_data:
            print("No sensor data to save.")
            return

        with open('sensor_data.json', 'w') as f:
            json.dump(self.sensor_data, f, indent=4)
        print("Sensor data saved successfully!")

    def save_environment(self):
        try:
            temperature = float(self.environment_entries["Temperature"].get())
            if temperature < 0:
                raise ValueError("Temperature must be a positive float.")
            humidity = float(self.environment_entries["Humidity"].get())
            if humidity < 0:
                raise ValueError("Humidity must be a positive float.")
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return
        
        self.data["environment"] = {label: entry.get() for label, entry in self.environment_entries.items()}
        print("Environment data saved:", self.data["environment"])

    def submit_all(self):
        self.data["sensors"] = self.sensor_data
        with open('database_schema.json', 'w') as f:
            json.dump(self.data, f, indent=4)
        print("All data saved to the file 'database_schema.json'.")

    def cancel_all(self):
        self.data = {
            "occupants": {},
            "seat_details": {},
            "sensors": {},
            "environment": {},
            "seat_positioning": {}  # Clear seat positioning data too
        }
        self.sensor_data.clear() 
        print("Data has been cleared.")

    def tcp_reader(self, data):
        try:
            data = json.loads(data)
            if 'offset' in data and isinstance(data['offset'], list):
                self.offset_data = data['offset']  # 
            else:
                print("Received TCP data does not contain valid offset values.")
        except json.JSONDecodeError as e:
            print("Received invalid JSON:", data)
            print("Error:", e)

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

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Application terminated.")
        app.tcp_client.stop()