
import os
from pathlib import Path


class Helper:

    
    def create_path(directory, filename):
        return os.path.join(directory, filename)
    

    def get_all_files_in_folder(folder_path):
        folder = Path(folder_path)
        files = [file.name for file in folder.iterdir() if file.is_file()]
        return files
