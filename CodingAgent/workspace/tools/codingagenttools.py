import os
import psycopg2
import subprocess
from dotenv import load_dotenv
load_dotenv()
class codingagenttools:
    def __init__(self):
        # Get the absolute path of the directory where main.py is located
        main_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the path to the workingspace folder
        self.working_dir = os.path.join(main_dir, 'workingspace')
    def create_py_file(self, filename, content):
        filepath = os.path.join(self.working_dir, filename)
        try:
            with open(filepath, 'w') as file:
                file.write(content)
            return f"File '{filename}' created successfully."
        except Exception as e:
            return f"An error occurred while creating the file: {e}"
    def read_file(self, filename):
        filepath = os.path.join(self.working_dir, filename)
        try:
            with open(filepath, 'r') as file:
                content = file.read()
            return f"Content of '{filename}':\n{content}"
        except Exception as e:
            return f"An error occurred while reading the file: {e}"
    def run_file(self, filename):
        filepath = os.path.join(self.working_dir, filename)
        try:
            output = subprocess.check_output(['python', filepath])
            return f"Execution Output:\n{output.decode('utf-8')}"
        except Exception as e:
            return f"An error occurred while executing the file: {e}"
    def view_workspace(self):
        print("Files in workspace:")
        for filename in os.listdir(self.working_dir):
            print(filename)
    def edit_file(self, filename, new_content):
        filepath = os.path.join(self.working_dir, filename)
        try:
            with open(filepath, 'w') as file:
                file.write(new_content)
            print(f"File '{filename}' edited successfully.")
        except Exception as e:
            print(f"An error occurred while editing the file: {e}")

    