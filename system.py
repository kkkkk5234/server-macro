import os
import sys
import time
import subprocess
import platform
import ctypes
import getpass
import signal

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
AUTO_STARTUP = True
PASSWORD_FILE = "sl_password"   # will be stored in user's home directory
# ------------------------------------------------------------

def get_os():
    return platform.system().lower()

def get_password_path():
    # Store password in user's home directory, not current working dir
    home = os.path.expanduser("~")
    return os.path.join(home, PASSWORD_FILE)

# ---------------------- PERSISTENCE ----------------------
def install_persistence():
    script_path = os.path.abspath(sys.argv[0])
    try:
        if get_os() == "windows":
            startup_dir = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
            dest = os.path.join(startup_dir, "second_layer.bat")
            with open(dest, "w") as f:
                f.write(f'@echo off\npython "{script_path}"\n')
            subprocess.run(["reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "/v", "SecondLayer", "/t", "REG_SZ", "/d", f'python "{script_path}"', "/f"], capture_output=True)
            print("[Persistence] Installed")
        elif get_os() == "linux":
            cron_line = f"@reboot python3 {script_path} &"
            subprocess.run(["crontab", "-l"], stdout=open("/tmp/cron_temp","w"), stderr=subprocess.DEVNULL, text=True)
            with open("/tmp/cron_temp", "a") as f:
                f.write(cron_line + "\n")
            subprocess.run(["crontab", "/tmp/cron_temp"], capture_output=True)
            os.remove("/tmp/cron_temp")
            print("[Persistence] Installed")
        elif get_os() == "darwin":
            plist_path = os.path.expanduser("~/Library/LaunchAgents/com.secondlayer.plist")
            with open(plist_path, "w") as f:
                f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.secondlayer</string>
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
            print("[Persistence] Installed")
    except Exception as e:
        print(f"[Persistence] Error: {e}")

# ---------------------- REMOVE PERSISTENCE ----------------------
def remove_persistence():
    try:
        if get_os() == "windows":
            startup_dir = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
            dest = os.path.join(startup_dir, "second_layer.bat")
            if os.path.exists(dest): os.remove(dest)
            subprocess.run(["reg", "delete", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "/v", "SecondLayer", "/f"], capture_output=True)
        elif get_os() == "linux":
            subprocess.run(["crontab", "-l"], stdout=open("/tmp/cron_temp","w"), stderr=subprocess.DEVNULL, text=True)
            lines = open("/tmp/cron_temp").readlines()
            lines = [l for l in lines if "second_layer" not in l]
            with open("/tmp/cron_temp", "w") as f: f.writelines(lines)
            subprocess.run(["crontab", "/tmp/cron_temp"], capture_output=True)
            os.remove("/tmp/cron_temp")
        elif get_os() == "darwin":
            plist_path = os.path.expanduser("~/Library/LaunchAgents/com.secondlayer.plist")
            if os.path.exists(plist_path):
                subprocess.run(["launchctl", "unload", plist_path], capture_output=True)
                os.remove(plist_path)
        print("[*] Persistence removed")
    except Exception as e:
        print(f"[Remove] Error: {e}")

# ---------------------- LOCK FUNCTIONS (NO SHUTDOWN BLOCK) ----------------------
def lock_windows():
    try:
        user32 = ctypes.WinDLL("user32")
        user32.LockWorkStation()
        # Only disable task manager, NOT shutdown
        subprocess.run(["reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System", "/v", "DisableTaskMgr", "/t", "REG_DWORD", "/d", "1", "/f"], capture_output=True)
        print("[Windows] Locked (task manager disabled)")
    except Exception as e:
        print(f"[Lock] Error: {e}")

def lock_linux():
    try:
        subprocess.run(["gnome-screensaver-command", "-l"], capture_output=True, timeout=5)
        subprocess.run(["loginctl", "lock-session"], capture_output=True)
        print("[Linux] Locked")
    except Exception as e:
        print(f"[Lock] Error: {e}")

def lock_macos():
    try:
        subprocess.run(["pmset", "displaysleepnow"], capture_output=True)
        subprocess.run(["osascript", "-e", 'tell application "System Events" to key code 12 using {command down, control down}'], capture_output=True)
        print("[macOS] Locked")
    except Exception as e:
        print(f"[Lock] Error: {e}")

def lock_system():
    os_name = get_os()
    if os_name == "windows": lock_windows()
    elif os_name == "linux": lock_linux()
    elif os_name == "darwin": lock_macos()
    else: print(f"[!] Unsupported OS: {os_name}")

def unlock_system(password, stored_password):
    return password == stored_password

# ---------------------- UNLOCK CLEANUP ----------------------
def cleanup_after_unlock():
    if get_os() != "windows":
        return
    # Restore task manager
    subprocess.run(["reg", "delete", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System", "/v", "DisableTaskMgr", "/f"], capture_output=True)

# ---------------------- INTERRUPT BLOCK ----------------------
def ignore_signal(sig, frame):
    print("[!] Exit blocked")

# ---------------------- MAIN MODE ----------------------
def setup_mode():
    print("\n=== SECOND LAYER SECURITY - SETUP ===")
    pwd = getpass.getpass("Enter your desired unlock password: ")
    confirm = getpass.getpass("Confirm password: ")
    if pwd != confirm:
        print("Passwords do not match. Exiting.")
        sys.exit(1)
    # Save password to user home directory
    password_path = get_password_path()
    with open(password_path, "w") as f:
        f.write(pwd)
    print(f"[*] Password saved to {password_path}")
    if AUTO_STARTUP:
        install_persistence()
    print("[*] Tool will activate on next boot.")
    time.sleep(2)
    sys.exit(0)

def lock_mode():
    password_path = get_password_path()
    if not os.path.exists(password_path):
        print("[!] Password file missing. Re-run setup.")
        sys.exit(1)
    with open(password_path, "r") as f:
        stored_pwd = f.read().strip()
    print("[*] Second Layer active. Locking screen...")
    time.sleep(2)
    lock_system()
    while True:
        try:
            pwd = getpass.getpass("[LOCKED] Enter password to unlock: ")
            if unlock_system(pwd, stored_pwd):
                print("[*] Unlocked successfully.")
                cleanup_after_unlock()
                break
            else:
                print("[!] Wrong password.")
                lock_system()
        except KeyboardInterrupt:
            print("[!] Interrupt blocked.")
            lock_system()
        except Exception as e:
            print(f"[!] Error: {e}")
            lock_system()

def uninstall_mode():
    print("\n=== UNINSTALL SECOND LAYER ===")
    print("Press ENTER to confirm removal. Any other key to cancel.")
    choice = input("> ")
    if choice != "":
        print("Cancelled.")
        sys.exit(0)
    remove_persistence()
    password_path = get_password_path()
    if os.path.exists(password_path):
        os.remove(password_path)
    cleanup_after_unlock()
    print("[*] Second Layer removed. Machine back to normal.")
    time.sleep(2)
    sys.exit(0)

# ---------------------- MAIN ----------------------
def main():
    if get_os() == "windows":
        ctypes.windll.kernel32.SetConsoleCtrlHandler(None, True)
    signal.signal(signal.SIGINT, ignore_signal)
    signal.signal(signal.SIGTERM, ignore_signal)

    password_path = get_password_path()
    if not os.path.exists(password_path):
        # First run -> setup mode
        setup_mode()
    else:
        # Check if user wants to uninstall
        print("Second Layer Security is active.")
        print("Press ENTER within 5 seconds to UNINSTALL, or wait to enter lock mode.")
        try:
            if os.name == 'nt':
                import msvcrt
                start = time.time()
                while time.time() - start < 5:
                    if msvcrt.kbhit():
                        msvcrt.getch()
                        uninstall_mode()
                        return
                    time.sleep(0.5) 
            else:
                import select
                rlist, _, _ = select.select([sys.stdin], [], [], 5)
                if rlist:
                    sys.stdin.readline()
                    uninstall_mode()
                    return
        except Exception:
            pass
        lock_mode()

if __name__ == "__main__":
    main()