import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading
import os
import sys
import signal

# Get the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Global variable to track the current process
current_process = None

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

def run_script():
    global current_process
    
    # Get inputs from Entry widgets
    device_ids = [entry.get() for entry in entries]
    if not all(id_.isdigit() for id_ in device_ids):
        output_box.insert(tk.END, "Please enter only numeric device IDs.\n")
        return
    
    # Use absolute paths with os.path
    python_path = os.path.join(project_root, "myenv", "Scripts", "python.exe")
    script_path = os.path.join(project_root, "src", "heart_rate_mqtt_broker.py")
    
    command = [python_path, script_path] + device_ids
    
    output_box.insert(tk.END, f"Running command: {' '.join(command)}\n")
    output_box.insert(tk.END, f"Working directory: {project_root}\n")

    def target():
        global current_process
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Redirect stderr to stdout
            text=True,
            bufsize=0,  # No buffering for immediate output
            cwd=project_root,  # Set working directory explicitly
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0  # For Windows CTRL+C handling
        )
        
        current_process = process
        
        # Function to read from stdout and write to output_box
        for line in iter(process.stdout.readline, ''):
            if line:
                output_box.insert(tk.END, line)
                output_box.see(tk.END)
                root.update()  # Full GUI update
        
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
    # Add default values (can be removed if not needed)
    entry.insert(0, str(i+1))
    entries.append(entry)

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
root.geometry("800x600")
root.minsize(600, 400)

root.mainloop()