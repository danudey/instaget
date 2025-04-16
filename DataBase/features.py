import random,shutil,os,sys,requests,zipfile
from time import sleep
from colorama import Fore,init,Style
init(autoreset=True)

def show_banner():
    banners = [
        f"""{Fore.MAGENTA}
╔══════════════════════════════════════════════╗
║     📸 InstaHive - Instagram Downloader     ║
╠══════════════════════════════════════════════╣
║ GitHub: https://github.com/imraj569          ║
╚══════════════════════════════════════════════╝
""",

        f"""{Fore.CYAN}
╔══════════════════════════════════════════════╗
║     📲 InstaHive - Grab Instagram Content   ║
╠══════════════════════════════════════════════╣
║ GitHub: https://github.com/imraj569          ║
╚══════════════════════════════════════════════╝
""",

        f"""{Fore.GREEN}
╔══════════════════════════════════════════════╗
║     🚀 InstaHive - Download Instagram Media  ║
╠══════════════════════════════════════════════╣
║ GitHub: https://github.com/imraj569          ║
╚══════════════════════════════════════════════╝
"""
    ]
    print(random.choice(banners))

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
    repo_url = "https://github.com/imraj569/InstaHive/archive/refs/heads/main.zip"
    download_path = "InstaHive-main.zip"

    # Download the entire repository as a zip
    try:
        print(Fore.YELLOW + "[*] Downloading the latest version of the repository...")
        response = requests.get(repo_url, stream=True)
        if response.status_code == 200:
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print(Fore.GREEN + "[✓] Repository downloaded successfully.")
        else:
            print(Fore.RED + "[X] Failed to download the repository.")
            return
    except Exception as e:
        print(Fore.RED + f"[X] Error downloading repository: {e}")
        return

    # Extract the downloaded ZIP file
    try:
        print(Fore.YELLOW + "[*] Extracting the repository...")
        with zipfile.ZipFile(download_path, 'r') as zip_ref:
            zip_ref.extractall()
        print(Fore.GREEN + "[✓] Repository extracted successfully.")
    except Exception as e:
        print(Fore.RED + f"[X] Error extracting repository: {e}")
        return

    # Replace the old files with the new ones
    extracted_folder = "InstaHive-main"
    for root, dirs, files in os.walk(extracted_folder):
        for file in files:
            # Skip the downloaded ZIP file itself
            if file == download_path:
                continue
            src_file = os.path.join(root, file)
            dst_file = os.path.join(os.getcwd(), file)

            try:
                # Replace old files with new ones
                if os.path.exists(dst_file):
                    os.remove(dst_file)
                shutil.copy(src_file, dst_file)
                print(Fore.GREEN + f"[✓] Replaced: {file}")
            except Exception as e:
                print(Fore.RED + f"[X] Error replacing {file}: {e}")

    # Clean up: Delete the downloaded ZIP and extracted folder
    os.remove(download_path)
    shutil.rmtree(extracted_folder)
    print(Fore.GREEN + "[✓] Update complete. Restarting...")
    sleep(2)
    os.execv(sys.executable, ['python'] + sys.argv)  # Restart the script to apply updates

# Function to get the current version of the script (use version.txt as the source)
def get_current_version():
    try:
        with open("version.txt", "r") as file:
            return file.read().strip()  # Get current version from the version.txt file
    except FileNotFoundError:
        print(Fore.RED + "[X] version.txt not found.")
    return "unknown"  # Default fallback version if version.txt isn't found
