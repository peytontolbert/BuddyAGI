import subprocess
import tkinter as tk
from tkinter import scrolledtext
import os


# Define your list of application folders to target
target_folders = ['Buddy', 'CodingAgent', 'DBAgent', 'ManagerAgent', 'WebBrowserAgent']


# Path to the main directory where target folders are located
current_script_path = os.path.abspath(__file__)  # Absolute path of the current script
parent_dir = os.path.dirname(os.path.dirname(current_script_path))  # Navigate up twice to reach the main directory

# List to keep track of subprocesses
processes = {}

def start_app(app_name):
    app_folder_path = os.path.join(parent_dir, app_name)
    main_py_path = os.path.join(app_folder_path, 'main.py')
    if os.path.exists(main_py_path) and app_name not in processes:
        process = subprocess.Popen(['python', main_py_path],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   text=True,
                                   bufsize=1,
                                   universal_newlines=True)
        processes[app_name] = process
        update_console(app_name)

def stop_app(app_name):
    if app_name in processes:
        processes[app_name].terminate()
        del processes[app_name]

def restart_app(app_name):
    stop_app(app_name)
    start_app(app_name)

def update_console(app_name):
    console.configure(state='normal')
    if app_name in processes:
        process = processes[app_name]
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                console.insert(tk.END, output)
                console.yview(tk.END)
    console.configure(state='disabled')

processes = {}

root = tk.Tk()
root.title("Python Applications Manager")

# Assuming you have an application called 'DrawSD'
console = scrolledtext.ScrolledText(root, state='disabled', height=10)
console.pack(padx=10, pady=10)

# Create buttons for each application
for app_name in target_folders:
    tk.Button(root, text=f"Start {app_name}", command=lambda name=app_name: start_app(name)).pack()
    tk.Button(root, text=f"Stop {app_name}", command=lambda name=app_name: stop_app(name)).pack()
    tk.Button(root, text=f"Restart {app_name}", command=lambda name=app_name: restart_app(name)).pack()

root.mainloop()