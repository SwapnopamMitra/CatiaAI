import os
import time
import signal
import psutil
import subprocess

def find_process_id(process_name):
    """Finds the PID of a running process by name (Windows-compatible)."""
    pids = []
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if process_name.lower() in proc.info['name'].lower():
            pids.append(proc.info['pid'])
    return pids

def kill_process(pids):
    """Kills all found process IDs."""
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)  # 🔥 SIGTERM is safer than SIGKILL on Windows
            print(f"✅ Successfully killed process with PID: {pid}")
        except ProcessLookupError:
            print(f"⚠ Process {pid} not found. It may have already stopped.")

if __name__ == "__main__":
    print(f"🚨 Auto-kill script running... Watching for `train_loop.py`...")

    while True:
        pids = find_process_id("python")  # ✅ Windows doesn't show full script name, just "python"
        for pid in pids:
            try:
                cmdline = psutil.Process(pid).cmdline()
                if any("train_loop.py" in part for part in cmdline):
                    print(f"🚨 Found `train_loop.py` running! Killing process (PID: {pid})...")
                    kill_process([pid])
                    break  # ✅ Stops script after killing process
            except psutil.NoSuchProcess:
                continue
        
        print("✅ No `train_loop.py` process found. Monitoring...")
        time.sleep(2)  # 🔄 Check every 2 seconds
