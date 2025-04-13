import os
import re
import shutil
import platform
import requests
import sys
import logging
from time import sleep
from tqdm import tqdm
import instaloader
from DataBase.features import *
from colorama import Fore

# Suppress instaloader noisy logs
instaloader.logger.setLevel(logging.CRITICAL)

# Function to get the latest version from version.txt
def get_latest_version():
    version_url = "https://raw.githubusercontent.com/imraj569/InstaHive/main/version.txt"
    try:
        response = requests.get(version_url, timeout=5)
        if response.status_code == 200:
            return response.text.strip()
        else:
            print(Fore.RED + "[X] Failed to fetch version from GitHub.")
    except Exception as e:
        print(Fore.RED + f"[X] Error fetching version: {e}")
    return None

# Check and update the script if a new version is found
def check_and_update():
    # Fetch the latest version from GitHub
    remote_version = get_latest_version()
    
    # Check if the remote version exists and is different from the current version
    if remote_version:
        if remote_version != get_current_version():  # Compare with current version in the script
            print(Fore.MAGENTA + f"[!] New version available: {remote_version}. Updating...")
            update_script(remote_version)  # If update is needed, update the script
        else:
            print(Fore.GREEN + "[✓] You’re already using the latest version.")

# Update the script with the new code from GitHub
def update_script(remote_version):
    script_url = "https://raw.githubusercontent.com/imraj569/InstaHive/main/instagram_downloader.py"
    local_file = sys.argv[0]

    try:
        new_code = requests.get(script_url).text
        with open(local_file, "w", encoding="utf-8") as f:
            f.write(new_code)

        print(Fore.GREEN + "[✓] Update complete. Restarting...")
        sleep(2)
        os.execv(sys.executable, ['python'] + sys.argv)  # Restart the script to apply updates
    except Exception as e:
        print(Fore.RED + f"[X] Update failed: {e}")

# Function to get the current version of the script (use version.txt as the source)
def get_current_version():
    try:
        with open("version.txt", "r") as file:
            return file.read().strip()  # Get current version from the version.txt file
    except FileNotFoundError:
        print(Fore.RED + "[X] version.txt not found.")
    return "unknown"  # Default fallback version if version.txt isn't found

# Determine platform-specific download path
if platform.system() == "Windows":
    user = os.getlogin()
    download_path = f"C://Users//{user}//Downloads"
else:
    download_path = "/data/data/com.termux/files/home/storage/downloads"

session_file = "ig_session"
temp_dir = os.path.join(download_path, "temp_download")

# Clear screen function
def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

# Extract shortcode from URL
def extract_shortcode(url):
    match = re.search(r"instagram\.com/(?:reel|p|tv)/([^/?#&]+)", url)
    return match.group(1) if match else None

# Setup Instaloader
L = instaloader.Instaloader(
    download_video_thumbnails=False,
    download_geotags=False,
    download_comments=False,
    save_metadata=False,
    post_metadata_txt_pattern="",
    filename_pattern="{shortcode}"
)

# Download a single post (photo/video/album)
def download_post(shortcode):
    post = instaloader.Post.from_shortcode(L.context, shortcode)
    os.makedirs(temp_dir, exist_ok=True)
    L.dirname_pattern = temp_dir
    L.download_post(post, target="")

    files = [file for file in os.listdir(temp_dir) if (file.endswith((".mp4", ".jpg", ".jpeg", ".png")) and shortcode in file)]
    if not files:
        print(Fore.RED + "[X] Media file not found.")
        shutil.rmtree(temp_dir)
        return

    # Show progress bar during download
    for file in tqdm(files, desc="Downloading", colour="green"):
        old_path = os.path.join(temp_dir, file)
        new_filename = f"{post.owner_username}_{file}"
        new_path = os.path.join(download_path, new_filename)
        shutil.move(old_path, new_path)
        sleep(0.2)  # for progress bar effect

    print(Fore.GREEN + f"[✓] Saved {len(files)} file(s) successfully.")
    shutil.rmtree(temp_dir)
    sleep(2)
    clear_screen()
    show_banner()

# Start the script
clear_screen()
show_banner()

# Check for updates at the beginning
check_and_update()

# Login to Instagram
username = input(Fore.YELLOW + "Enter your Instagram username: ")
try:
    L.load_session_from_file(username, session_file)
    print(Fore.GREEN + "[✓] Logged in with saved session.")
    sleep(1)
    clear_screen()
    show_banner()
except FileNotFoundError:
    print(Fore.MAGENTA + "[!] No session found. Logging in...")
    password = input("Enter your Instagram password: ")
    try:
        L.login(username, password)
        L.save_session_to_file(session_file)
        print(Fore.GREEN + "[✓] Login successful. Session saved.")
        sleep(1)
        clear_screen()
        show_banner()
    except Exception as e:
        print(Fore.RED + f"[X] Login failed: {e}")
        exit()

# Main loop for downloading posts
while True:
    print()
    url = input(Fore.CYAN + "Paste Instagram URL (or type 'exit' to quit): ").strip()
    
    if url.lower() == "exit":
        print(Fore.YELLOW + "Goodbye! 👋")
        break

    shortcode = extract_shortcode(url)
    if not shortcode:
        print(Fore.RED + "[X] Unsupported or invalid URL.")
        continue
    try:
        download_post(shortcode)
    except Exception as e:
        print(Fore.RED + f"[X] Download failed: {e}")
