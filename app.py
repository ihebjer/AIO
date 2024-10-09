import tkinter as tk
from tkinter import ttk, messagebox
import json
import time
import uuid
from threading import Thread
import yaml
import sys
sys.path.append('/home/ihebjeridi/Documents/cbliteFinal/couchbase-lite-python')
from CouchbaseLite.Document import MutableDocument,Document
from database_manager import DatabaseManager
from client import Client


class App:
    def __init__(self, root):
        self.db_manager = DatabaseManager()  
        self.load_config('config.yaml')
        self.root = root
        self.root.title("FORVIA DATA ACQUISITION")
        self.root.geometry("1000x700")
        self.root.resizable(True, False)
        self.data = {
            "occupants": {},
            "seat_details": {},
            "seat_positioning": {} ,
            "sensors": {},
            "environment": {},
        }
        self.sensor_data = []
        self.create_tabs()
        self.tcp_client = Client(host=self.host, port=self.port, reader=self.tcp_reader)
        self.offset_data = None
        self.current_position = 0
        self.logging = False
        self.log_thread = None 
        self.test_counts = {}

    def create_tabs(self):
        self.tabControl = ttk.Notebook(self.root)
        self.occupant_tab = ttk.Frame(self.tabControl)
        self.seat_tab = ttk.Frame(self.tabControl)
        self.positioning_tab = ttk.Frame(self.tabControl)  
        self.sensor_tab = ttk.Frame(self.tabControl)
        self.environment_tab = ttk.Frame(self.tabControl)
        self.send_tab = ttk.Frame(self.tabControl)

        self.tabControl.add(self.occupant_tab, text="Occupant")
        self.tabControl.add(self.seat_tab, text="Seat details")
        self.tabControl.add(self.positioning_tab, text="Seat Positioning") 
        self.tabControl.add(self.sensor_tab, text="Sensors")
        self.tabControl.add(self.environment_tab, text="Environment")
        self.tabControl.add(self.send_tab, text="Send")

        self.tabControl.pack(expand=1, fill="both")
        self.create_occupant_tab()
        self.create_seat_tab()
        self.create_positioning_tab()  
        self.create_sensor_tab()
        self.create_environment_tab()
        self.create_send_tab()

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
        labels = ["ID_Occupant","Name", "Age", "Weight", "Height", "Gender", "Ocuppant Classification"]
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
        style.configure("TButton", foreground="white", background="black")

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

# def save_occupant(self):
#     try:
#         age = int(self.occupant_entries["Age"].get())
#         if age < 0:
#             raise ValueError("Age must be a positive integer.")
        
#         weight = float(self.occupant_entries["Weight"].get())
#         height = float(self.occupant_entries["Height"].get())
#         gender = self.occupant_entries["Gender"].get()

#         if gender not in ["H", "F"]:
#             raise ValueError("Gender must be 'H' or 'F'.")

#     except ValueError as e:
#         messagebox.showerror("Input Error", str(e))
#         return

#     occupant_data = {label: entry.get() for label, entry in self.occupant_entries.items()}

#     document_id = f"{occupant_data['Name']}_{occupant_data['ID_Occupant']}"
#     doc = Document.createDocWithId(document_id)
#     try:
#         occupant_json = occupant_data  
#         Document.setJSON(doc, occupant_json)  
#     except Exception as e:
#         messagebox.showerror("Document Error", f"Failed to create or set JSON on document: {str(e)}")
#         return

#     occupants_collection = self.db_manager.occupants_collection
#     if occupants_collection is None:
#         messagebox.showerror("Collection Error", "The 'Occupants' collection could not be initialized.")
#         return

#     try:
#         self.db_manager.save_document(occupants_collection, doc)  
#         print(f"Occupant document saved with ID: {document_id} in occupants_collection")
#     except Exception as e:
#         messagebox.showerror("Save Error", f"Failed to save occupant data: {str(e)}")
#     for entry in self.occupant_entries.values():
#         entry.delete(0, tk.END)

#     messagebox.showinfo("Success", f"Occupant data for '{document_id}' has been saved and cleared.")
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
        
        occupant_data = {label: entry.get() for label, entry in self.occupant_entries.items()}
        document_id = f"Occupant_{occupant_data['ID_Occupant']}"
        occupant_doc = MutableDocument(document_id)
        for key, value in occupant_data.items():
            occupant_doc[key] = value
        
        try:
            self.db_manager.db.saveDocument(occupant_doc)
            print(f"Occupant document saved with ID: {document_id}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save occupant data: {str(e)}")

        for entry in self.occupant_entries.values():
            entry.delete(0, tk.END)  

        messagebox.showinfo("Success", f"Occupant data for '{document_id}' has been saved and cleared.")

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
        seat_id = self.seat_entries["SeatID"].get()
        
        if not seat_id:
            raise ValueError("Seat ID is required.")
        
        try:
            if self.db_manager.db.getDocument(seat_id) is not None:
                raise ValueError(f"Seat with ID '{seat_id}' already exists in the database.")
            
            doc = MutableDocument(seat_id)
            
            fields = [
                "SeatName", "sensor_numbers_backrest", "SensorNumbersCushion", 
                "CushionWidth", "FoamMaterial", "CushionFoamThickness", 
                "BackrestFoamThickness", "BolsterCoverMaterial", 
                "CushionCoverMaterial", "BackrestCoverMaterial"
            ]
            
            for field in fields:
                doc[field] = self.seat_entries[field].get()

            self.db_manager.db.saveDocument(doc)
            print(f"Seat data with ID '{seat_id}' saved to database:", doc)

            for entry in self.seat_entries.values():
                entry.delete(0, tk.END)
            
            messagebox.showinfo("Success", f"Seat data for '{seat_id}' has been saved and cleared.")

        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
            print(str(ve))
        except Exception as e:
            messagebox.showerror("Database Error", f"Error saving seat data: {str(e)}")
            print("Error saving seat data:", e)

    def create_sensor_tab(self):
        self.sensor_labels = [f"Sensor {i + 1}" for i in range(10)]
        self.sensor_entries = {label: tk.Label(self.sensor_tab, text="0.0") for label in self.sensor_labels}
        
        tk.Label(self.sensor_tab, text="Out of Position").grid(row=len(self.sensor_labels), column=0, padx=10, pady=5, sticky="ew")
        self.out_of_position_entry = ttk.Combobox(self.sensor_tab, values=[
            "Nominal position","Leaning forward", "Dissymetry", 
            "Pelvis drift", "Feet on the dashboard"
        ])
        self.out_of_position_entry.grid(row=len(self.sensor_labels), column=1, padx=10, pady=5, sticky="ew")
        
        tk.Label(self.sensor_tab, text="Timer:").grid(row=len(self.sensor_labels) + 1, column=0, padx=10, pady=5, sticky="ew")
        self.timer_label = tk.Label(self.sensor_tab, text="00:00:00")
        self.timer_label.grid(row=len(self.sensor_labels) + 1, column=1, padx=10, pady=5, sticky="ew")
        
        self.configure_grid(self.sensor_tab, len(self.sensor_labels) + 4, 2)

        for i, label in enumerate(self.sensor_labels):
            tk.Label(self.sensor_tab, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            self.sensor_entries[label].grid(row=i, column=1, padx=10, pady=5, sticky="ew")

        button_frame = ttk.Frame(self.sensor_tab)
        button_frame.grid(row=len(self.sensor_labels) + 3, column=0, columnspan=2, pady=10)

        self.start_button = ttk.Button(button_frame, text="Start Test", command=self.start_test, style="TButton")
        self.start_button.grid(row=0, column=0, padx=10)

        self.stop_button = ttk.Button(button_frame, text="Stop Test", command=self.stop_test, state=tk.DISABLED, style="TButton")
        self.stop_button.grid(row=0, column=1, padx=10)

        self.save_button = ttk.Button(button_frame, text="Save", command=self.save_sensor_data, style="TButton")
        self.save_button.grid(row=0, column=2, padx=10)

        

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
        ttk.Button(button_frame, text="Clear Data", command=self.clear_all, style="TButton").pack(side=tk.LEFT, padx=20, pady=10)
        self.image = tk.PhotoImage(file="/home/ihebjeridi/Documents/app - OOP/app_acquisation/images/faurecia_logo-removebg-preview.png")  
        image_label = tk.Label(self.send_tab, image=self.image)
        image_label.pack(side=tk.BOTTOM, pady=40)

    def create_positioning_tab(self):
        self.positioning_entries = {
            "SeatID": tk.Entry(self.positioning_tab),  
            "OccupantID": tk.Entry(self.positioning_tab),  
            "Backrest": tk.Entry(self.positioning_tab),
            "CushionTilt": tk.Entry(self.positioning_tab),
            "Track": tk.Entry(self.positioning_tab),
            "Height": tk.Entry(self.positioning_tab),
            "Uba": tk.Entry(self.positioning_tab),
        }

        self.configure_grid(self.positioning_tab, len(self.positioning_entries) + 1, 2)
        row = 0
        for label, entry in self.positioning_entries.items():
            tk.Label(self.positioning_tab, text=label).grid(row=row, column=0, padx=10, pady=5, sticky="ew")
            entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
            row += 1

        ttk.Button(self.positioning_tab, text="Save", command=self.save_positioning_data, style="TButton").grid(row=row, column=0, columnspan=2, pady=10)


    def save_positioning_data(self):
        try:
            occupant_id = self.positioning_entries["OccupantID"].get()  
            seat_id = self.positioning_entries["SeatID"].get()  

            if not occupant_id or not seat_id:
                raise ValueError("Occupant ID and Seat ID are required.")

            occupant_doc_id = f"Occupant_{occupant_id}"  
            occupant_doc = self.db_manager.db.getDocument(occupant_doc_id)
            if not occupant_doc:
                raise ValueError(f"No occupant found with ID: {occupant_id}")

            seat_doc = self.db_manager.db.getDocument(seat_id)
            if not seat_doc:
                raise ValueError(f"No seat found with ID: {seat_id}")

            for field in ["Backrest", "CushionTilt", "Track", "Height", "Uba"]:
                value = float(self.positioning_entries[field].get())
                if value < 0:
                    raise ValueError(f"{field} must be a positive float.")

            self.data["seat_positioning"] = {
                **{label: entry.get() for label, entry in self.positioning_entries.items() if label not in ["SeatID", "OccupantID"]}
            }
            print("Seat positioning data saved:", self.data["seat_positioning"])

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except Exception as e:
            messagebox.showerror("Database Error", f"Error accessing database: {str(e)}")

    def start_test(self):
        
        if not self.out_of_position_entry.get():
            messagebox.showwarning("Input Error", "Please enter position.")
            return  
        
        if self.offset_data is not None:
            for i, label in enumerate(self.sensor_labels):
                self.sensor_entries[label].config(text=self.offset_data[i])
                
            self.logging = True  
            self.start_time = time.time()  

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
        self.timer_label.config(text="00:00:00") 
        self.start_time = None  
        
    def log_sensor_data(self):
        while self.logging:
            timestamp = time.strftime("%H:%M:%S")  
            current_out_of_position = self.out_of_position_entry.get()  
            
            sensor_values = {label: round((self.offset_data[i]), 2)for i, label in enumerate(self.sensor_labels)}
            
            self.sensor_data.append({
                "timestamp": timestamp,
                "position": self.current_position + 1,
                "out_of_position": current_out_of_position,
                **sensor_values
            })

            for label in self.sensor_labels:
                self.sensor_entries[label].config(text=str(sensor_values[label]))  

                
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
        try:
            occupant_id = self.positioning_entries["OccupantID"].get()  
            seat_id = self.positioning_entries["SeatID"].get()  
            
            if not occupant_id or not seat_id:
                raise ValueError("Occupant ID and Seat ID are required for submission.")

            occupant_doc_id = f"Occupant_{occupant_id}"  

            occupant_doc = self.db_manager.db.getDocument(occupant_doc_id)             
            if not occupant_doc:
                raise ValueError(f"No occupant found with ID: {occupant_id}")

            props = occupant_doc.properties
            occupant_name = props.get("Name", "Unknown")  
            
            short_uuid = str(uuid.uuid4())[:8]  

            document_id = f"{occupant_name}_{occupant_id}_{short_uuid}"

            seat_positioning_data = {label: entry.get() for label, entry in self.positioning_entries.items() if label not in ["SeatID", "OccupantID"]}
            
            self.data["seat_positioning"] = seat_positioning_data
            self.data["sensors"] = self.sensor_data
            self.data["environment"] = {label: entry.get() for label, entry in self.environment_entries.items()}

            doc = MutableDocument(document_id)
            doc["seat_positioning"] = self.data["seat_positioning"]
            doc["sensors"] = self.data["sensors"]
            doc["environment"] = self.data["environment"]
            doc["SeatID"] = seat_id  
            doc["OccupantID"] = occupant_id  

            self.db_manager.db.saveDocument(doc)
            print(f"Test data saved successfully with ID: {document_id}")

        except ValueError as e:
            messagebox.showerror("Submission Error", str(e))
            return
        except Exception as e:
            messagebox.showerror("Database Error", f"Error saving document: {str(e)}")
            return

        messagebox.showinfo("Success", "All test data has been successfully submitted and saved.")

            
    def clear_all(self):
        self.data.clear()
        self.sensor_data = []

        for entry in self.positioning_entries.values():
            entry.delete(0, tk.END)

        for entry in self.environment_entries.values():
            entry.delete(0, tk.END)

        # Clear sensor values
        for label in self.sensor_labels:
            self.sensor_entries[label].config(text="0.0")

        messagebox.showinfo("Success", "All data and entry fields have been cleared")


    def tcp_reader(self, data):
        try:
            data = json.loads(data)
            if 'offset' in data and isinstance(data['offset'], list):
                self.offset_data = data['offset']  
                #print(f"Received asana_offset: {self.offset_data}")  # Print the received offsets
            else:
                print("Received TCP data does not contain valid offset values.")
        except json.JSONDecodeError as e:
            print("Received invalid JSON:", data)
            print("Error:", e)


