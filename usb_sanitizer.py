import os
import shutil
import logging
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
log_file = "USB-Sanitization/usb_sanitizer.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Define the path to the USB drive
USB_PATH = r"D:\\Abad Khan\\CyberSecurity_Projects\\Projects\\USB-Sanitization\\usb"  # Use raw string

# Define suspicious file extensions and filenames
SUSPICIOUS_EXTENSIONS = ['.exe', '.bat', '.vbs', '.cmd', '.scr', '.pif']
SUSPICIOUS_FILES = ['autorun.inf']

# Create a folder to quarantine suspicious files
QUARANTINE_FOLDER = os.path.join(USB_PATH, 'quarantine')
if not os.path.exists(QUARANTINE_FOLDER):
    os.makedirs(QUARANTINE_FOLDER)

def scan_and_clean(directory):
    for root, dirs, files in os.walk(directory):
        if QUARANTINE_FOLDER in root:
            continue
        for file in files:
            file_path = os.path.join(root, file)
            if file.lower().endswith(tuple(SUSPICIOUS_EXTENSIONS)) or file.lower() in SUSPICIOUS_FILES:
                logging.info(f"Suspicious file detected: {file_path}")
                quarantine_file(file_path)

def quarantine_file(file_path):
    try:
        base_name = os.path.basename(file_path)
        quarantine_path = os.path.join(QUARANTINE_FOLDER, base_name)
        # If file with the same name already exists, append timestamp
        if os.path.exists(quarantine_path):
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            base_name, ext = os.path.splitext(base_name)
            quarantine_path = os.path.join(QUARANTINE_FOLDER, f"{base_name}_{timestamp}{ext}")

        shutil.move(file_path, quarantine_path)
        logging.info(f"Quarantined file: {file_path} to {quarantine_path}")
    except Exception as e:
        logging.error(f"Error quarantining file: {file_path}. Error: {str(e)}")

class USBEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            scan_and_clean(USB_PATH)

if __name__ == "__main__":
    # Initial scan
    scan_and_clean(USB_PATH)

    # Set up a watchdog to monitor the USB drive for new files
    event_handler = USBEventHandler()
    observer = Observer()
    observer.schedule(event_handler, USB_PATH, recursive=True)
    observer.start()

    logging.info("Monitoring USB drive for new files...")

    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    logging.info("Stopped monitoring USB drive.")
