import json
import os
from datetime import datetime
from libraries.dataholder import dataholder
import pickle

class FileHandler:
    def __init__(self, file_path="./logs/data.json", log_path="./logs/logs.txt"):
        self.file_path = file_path
        self.log_path = log_path

        # Ensure all required files exist or are properly formatted
        self._ensure_file(self.file_path, is_list=True)  
        self._ensure_log_file()

        # Load updates from the updates file into memory
        self.data = self.load_data()

    def _ensure_file(self, path, is_list=True):
        """Ensures the file exists and contains valid JSON. Resets if invalid."""
        if not os.path.exists(path):
            # Create the file with an empty list or dict
            with open(path, 'w+') as f:
                json.dump([] if is_list else {}, f)
        else:
            # Try to load the file and reset if invalid
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    if is_list and not isinstance(data, list):
                        raise ValueError(f"Invalid JSON format in {path}, resetting to empty list.")
                    if not is_list and not isinstance(data, dict):
                        raise ValueError(f"Invalid JSON format in {path}, resetting to empty dictionary.")
            except (json.JSONDecodeError, ValueError):
                # Reset the file content
                with open(path, 'w') as f:
                    json.dump([] if is_list else {}, f)

    def _ensure_log_file(self):
        """Ensures the log file exists."""
        log_dir = os.path.dirname(self.log_path)
        # Create log directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        # Create log file if it doesn't exist
        if not os.path.exists(self.log_path):
            with open(self.log_path, 'w') as f:
                f.write("")  # Create an empty log file

    def load_data(self):
        """Loads and returns the JSON data from the main file."""
        with open(self.file_path, 'r') as f:
            return json.load(f)
        
    def _save_data(self, data):
        """Saves the given data back to the main JSON file."""
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def append_data(self, value):
        """Appends a value to the JSON data and saves it to the file."""
        data = self.load_data()
        for i in data:
            if(data['id']==value['id']):
                return    #error
        data.append(value)
        self._save_data(data)

    def load_sync_data(self,collection):
        data = self.load_data()
        for iter in data:
            collection[iter["id"]] = dataholder(iter)


    def write_log(self, text):
        """Writes a log entry in the format '[time] text'."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{current_time}] {text}\n"
        with open(self.log_path, 'a') as f:
            f.write(log_entry)

    def save_updates_on_exit(self):
        """Saves the updates dictionary back to the updates file when the program stops."""
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f, indent=4)

