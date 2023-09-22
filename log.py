import logging
import os
import json
from datetime import datetime

with open("/root/Nkss_AppcbUploading/config.json", "r") as file:
        config = json.load(file)


StorePath=config["ConfigSettings"]["StorePath"]        
# Define the maximum size of the log file in bytes
MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Define the logger and set the logging level
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Define the log file handler and set the logging format
log_filename = StorePath+"ProcessLog.txt"
if not os.path.exists(log_filename):
    open(log_filename, 'w').close()
file_handler = logging.FileHandler(log_filename)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Define a function to check the log file size and create a new file if necessary
def check_log_file_size():
    if os.path.isfile(log_filename) and os.path.getsize(log_filename) > MAX_LOG_FILE_SIZE:
        # Get the current date and time
        current_time = datetime.now().strftime("%m-%d")
        # Rename the current log file with the date and time appended to the name
        new_log_filename = os.path.join(StorePath, f"ProcessLog_{current_time}.txt")    
        logging.shutdown()    
        os.rename(log_filename, new_log_filename)
        file_handler = logging.FileHandler(log_filename)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)