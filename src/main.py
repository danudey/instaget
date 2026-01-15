#!/usr/bin/env python3
import os
import re
import sys
import shutil
import getpass
import pathlib
import logging
import instaloader

logging.basicConfig(level=logging.WARN)

match_pat = re.compile(r"instagram\.com/(?:reel|p|tv)/([^/?#&]+)")

downloads_folder = pathlib.Path("~/Downloads").expanduser()
temp_dir = downloads_folder.joinpath("temp_download")
download_path = downloads_folder.joinpath("ig_downloads")

# Extract shortcode from URL
def extract_shortcode(url):
    if match := match_pat.search(url):
        return match.group(1)


# Download a single post (photo/video/album)
def download_post(loader, shortcode):
    post = instaloader.Post.from_shortcode(loader.context, shortcode)
    temp_dir.mkdir(parents=True, exist_ok=True)
    loader.dirname_pattern = temp_dir.as_posix()
    loader.download_post(post, target="")

    files = [
        file
        for file in os.listdir(temp_dir)
        if (file.endswith((".mp4", ".jpg", ".jpeg", ".png")) and shortcode in file)
    ]
    if not files:
        print("[X] Media file not found.")
        shutil.rmtree(temp_dir)
        return

    # Show progress bar during download
    for file in files:
        old_path = temp_dir.joinpath(file)
        new_filename = f"{post.owner_username}_{file}"
        download_path.mkdir(exist_ok=True)
        new_path = download_path.joinpath(new_filename)
        shutil.move(old_path, new_path)

    print(f"[✓] Saved {len(files)} file(s) to {download_path} successfully.")
    shutil.rmtree(temp_dir)

def main():
    # Setup Instaloader
    loader = instaloader.Instaloader(
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        post_metadata_txt_pattern="",
        filename_pattern="{shortcode}",
    )
    session_dir = pathlib.Path("ig_session")
    session_dir.mkdir(parents=True, exist_ok=True)

    profile_files = list(session_dir.glob("*"))
    print(f"Found {len(profile_files)} profiles")
    if len(profile_files) == 0:
        # We need to log in
            username = input("Username: ")
            password = getpass.getpass()
            session_file = session_dir.joinpath(username)
            try:
                loader.login(username, password)
                loader.save_session_to_file(session_file)
                print("[✓] Login successful. Session saved.")

            except Exception as e:
                print(f"[X] Login failed: {e}")
                exit(-1)
    elif len(profile_files) == 1:
        session_file = profile_files[0]
        print(f"Loading session from {session_file}")
        username = session_file.name
        loader.load_session_from_file(username, session_file.as_posix())
    else:
        raise RuntimeError("Can't cope with multiple profiles yet")

    # Main loop for downloading posts
    for url in sys.argv[1:]:
        shortcode = extract_shortcode(url)
        if not shortcode:
            print("[X] Unsupported or invalid URL.")
            continue
        try:
            download_post(loader, shortcode)
        except Exception as e:
            print(f"[X] Download failed: {e}")
            raise

if __name__ == '__main__':
    main()