from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import time
import os

class RestartHandler(FileSystemEventHandler):
    def __init__(self, script_path):
        self.script_path = script_path
        self.process = None
        self.start_script()

    def start_script(self):
        if self.process:
            self.process.terminate()
        self.process = subprocess.Popen(['python', self.script_path])

    def on_modified(self, event):
        if event.src_path == self.script_path:
            print(f"{self.script_path} has been modified. Restarting...")
            self.start_script()

if __name__ == "__main__":
    script_to_watch = "internship.py"  # Update with your script path
    event_handler = RestartHandler(script_to_watch)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(script_to_watch), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
