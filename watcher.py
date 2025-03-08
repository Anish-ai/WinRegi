import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, process):
        self.process = process

    def on_any_event(self, event):
        if event.src_path.endswith(".py"):
            print(f"Detected change in {event.src_path}. Restarting...")
            self.process.kill()
            time.sleep(1)
            self.process = subprocess.Popen([sys.executable, "main.py"])

def start():
    process = subprocess.Popen([sys.executable, "main.py"])
    event_handler = ReloadHandler(process)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        process.kill()

    observer.join()

if __name__ == "__main__":
    start()
