import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading
import os
import sys
import signal
import re

# Get the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Global variable to track the current process
current_process = None
# Dictionary to store heart rate labels
heart_rate_labels = {}
# Lists to store UI references
device_frames = []
device_title_labels = []
hr_labels = []

def kill_script():
    global current_process
    if current_process and current_process.poll() is None:
        output_box.insert(tk.END, "Stopping monitoring (sending CTRL+C)...\n")
        
        # On Windows, use CTRL_BREAK_EVENT (CTRL+C is CTRL_C_EVENT)
        if os.name == 'nt':  # Windows
            try:
                current_process.send_signal(signal.CTRL_BREAK_EVENT)
            except Exception:
                current_process.terminate()
        else:  # Unix/Linux/Mac
            current_process.send_signal(signal.SIGINT)  # SIGINT is the signal sent by CTRL+C
            
        output_box.insert(tk.END, "Stop signal sent.\n")
        output_box.see(tk.END)

def update_heart_rate(device_id, heart_rate):
    """Update the heart rate display for a specific device"""
    if device_id in heart_rate_labels:
        heart_rate_labels[device_id].config(text=f"Heart Rate: {heart_rate} BPM")
        # Change color based on heart rate value
        if heart_rate > 160:
            heart_rate_labels[device_id].config(fg="red")
        elif heart_rate > 120:
            heart_rate_labels[device_id].config(fg="orange")
        else:
            heart_rate_labels[device_id].config(fg="green")

def parse_output_line(line):
    """Parse heart rate updates from output lines"""
    # Pattern: "Device ID X: Heart rate update Y"
    pattern = r"Device ID (\d+): Heart rate update (\d+)"
    match = re.search(pattern, line)
    if match:
        device_id = match.group(1)
        heart_rate = int(match.group(2))
        return device_id, heart_rate
    return None, None

def update_device_labels(active_devices):
    """Update the device labels to reflect the actual device IDs entered"""
    global heart_rate_labels
    
    # Clear previous heart_rate_labels
    heart_rate_labels = {}
    
    # Show only frames with entered device IDs
    for i in range(9):
        if i < len(active_devices) and active_devices[i]:
            # Update title to show actual device ID
            device_title_labels[i].config(text=f"Device ID: {active_devices[i]}")
            # Map this device ID to its heart rate label
            heart_rate_labels[active_devices[i]] = hr_labels[i]
            # Make sure the frame is visible
            device_frames[i].grid(row=(i // 3), column=(i % 3), padx=10, pady=5, sticky="ew")
        else:
            # Hide unused frames
            device_frames[i].grid_forget()

def run_script():
    global current_process
    
    # Get inputs from Entry widgets and filter out empty entries
    device_ids = [entry.get().strip() for entry in entries]
    active_devices = [id_ for id_ in device_ids if id_]
    
    if not all(id_.isdigit() for id_ in active_devices):
        output_box.insert(tk.END, "Please enter only numeric device IDs.\n")
        return
    
    # Update the device labels
    update_device_labels(active_devices)
    
    # Use absolute paths with os.path
    python_path = os.path.join(project_root, "myenv", "Scripts", "python.exe")
    script_path = os.path.join(project_root, "src", "heart_rate_mqtt_broker.py")
    
    command = [python_path, script_path] + active_devices
    
    output_box.insert(tk.END, f"Running command: {' '.join(command)}\n")
    output_box.insert(tk.END, f"Working directory: {project_root}\n")

    def target():
        global current_process
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=0,
            cwd=project_root,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        
        current_process = process
        
        # Function to read from stdout and write to output_box
        for line in iter(process.stdout.readline, ''):
            if line:
                # Update heart rate display if this is a heart rate update
                device_id, heart_rate = parse_output_line(line)
                if device_id and heart_rate:
                    # Update the corresponding heart rate display
                    root.after(0, update_heart_rate, device_id, heart_rate)
                
                # Still log everything to the output box
                output_box.insert(tk.END, line)
                output_box.see(tk.END)
                root.update()
        
        # Wait for process to complete
        exit_code = process.wait()
        output_box.insert(tk.END, f"\nProcess exited with code: {exit_code}\n")
        output_box.see(tk.END)
        current_process = None

    threading.Thread(target=target, daemon=True).start()

# Create GUI
root = tk.Tk()
root.title("ANT+ Heart Rate Monitor")

# Create a frame for labels and entries
frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Enter Device IDs:").grid(row=0, column=0, columnspan=3)

entries = []
# Create a grid of entry widgets (3x3)
for i in range(9):
    row = (i // 3) + 1
    col = i % 3
    frame_entry = tk.Frame(frame)
    frame_entry.grid(row=row, column=col, padx=5, pady=5)
    
    tk.Label(frame_entry, text=f"Device {i+1}:").pack(anchor='w')
    entry = tk.Entry(frame_entry, width=10)
    entry.pack()
    # Add default values
    entry.insert(0, str(i+1))
    entries.append(entry)

# Heart rate display frame
hr_frame = tk.Frame(root)
hr_frame.pack(pady=10, fill=tk.X)

# Create heart rate display widgets (3x3 grid)
for i in range(9):
    row = (i // 3)
    col = i % 3
    device_frame = tk.Frame(hr_frame, bd=2, relief=tk.GROOVE, padx=5, pady=5)
    device_frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
    device_frames.append(device_frame)
    
    # Create and store title label
    title_label = tk.Label(device_frame, text=f"Device {i+1}")
    title_label.pack()
    device_title_labels.append(title_label)
    
    # Create and store heart rate label
    hr_label = tk.Label(device_frame, text="Heart Rate: -- BPM", font=("Arial", 10, "bold"))
    hr_label.pack(pady=3)
    hr_labels.append(hr_label)
    
    # Initially map using default IDs (will be updated when Start is clicked)
    device_id = str(i+1)
    heart_rate_labels[device_id] = hr_label

# Button frame
button_frame = tk.Frame(root)
button_frame.pack(pady=5)
tk.Button(button_frame, text="Start Monitoring", command=run_script).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Stop Monitoring", command=kill_script, 
          bg="red", fg="white").pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Clear Output", 
         command=lambda: output_box.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=5)

# Output box with scrollbar
output_box = scrolledtext.ScrolledText(root, height=20, width=80)
output_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Initial instructions
output_box.insert(tk.END, "Enter device IDs and click 'Start Monitoring'.\n")
output_box.insert(tk.END, "Default IDs are pre-filled (1-9).\n\n")

# Make window resizable
root.geometry("800x700")
root.minsize(600, 500)

root.mainloop()