import os
import re
import requests
import instaloader
import telebot
from dotenv import load_dotenv

# Load .env
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
IG_SESSIONID = os.getenv("IG_SESSIONID")

bot = telebot.TeleBot(BOT_TOKEN)

# Instaloader setup
L = instaloader.Instaloader(
    download_video_thumbnails=False,
    download_geotags=False,
    download_comments=False,
    save_metadata=False,
    post_metadata_txt_pattern="",
    filename_pattern="{shortcode}"
)
L.context._session.cookies.set('sessionid', IG_SESSIONID, domain=".instagram.com")

# Extract shortcode
def extract_shortcode(url):
    match = re.search(r"instagram\.com/(?:reel|p|tv)/([^/?#&]+)", url)
    return match.group(1) if match else None

# Fetch post data
def fetch_post(shortcode):
    return instaloader.Post.from_shortcode(L.context, shortcode)

# /start command
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, """
👋 Welcome to the InstaHive Bot!

📥 Send me any public Instagram Reel, Post, or Video:
🔗 https://www.instagram.com/reel/shortcode/

I'll send:
✅ Cover image
✅ Post media (video/photo)
✅ Post details

🔧 Built by @imraj569  
🔗 GitHub: https://github.com/imraj569
""")

# ... (imports and setup remain the same)

# Handle Instagram URLs
@bot.message_handler(func=lambda msg: True)
def handle_instagram_url(message):
    url = message.text.strip()
    shortcode = extract_shortcode(url)

    if not shortcode:
        bot.reply_to(message, "❌ Invalid Instagram URL. Please send a valid /p/, /reel/, or /tv/ link.")
        return

    bot.send_chat_action(message.chat.id, 'typing')

    try:
        post = fetch_post(shortcode)

        # Send cover image
        bot.send_chat_action(message.chat.id, 'upload_photo')
        r = requests.get(post.url)
        if r.status_code == 200:
            bot.send_photo(message.chat.id, r.content, caption="🖼 Cover image")

        # Send post details
        bot.send_chat_action(message.chat.id, 'typing')
        caption = post.caption or "No caption"
        details = f"""📄 <b>Post Details</b>
👤 <b>User:</b> @{post.owner_username}
❤️ <b>Likes:</b> {post.likes}
📝 <b>Caption:</b> {caption[:200]}{'...' if len(caption) > 200 else ''}
🔗 <a href="{url}">View on Instagram</a>"""
        bot.send_message(message.chat.id, details, parse_mode="HTML", disable_web_page_preview=False)

        # Send media
        if post.typename == "GraphSidecar":
            for node in post.get_sidecar_nodes():
                media_url = node.video_url if node.is_video else node.display_url
                send_media(message.chat.id, media_url, node.is_video)
        else:
            media_url = post.video_url if post.is_video else post.url
            send_media(message.chat.id, media_url, post.is_video)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# Helper to send photo/video from URL
def send_media(chat_id, media_url, is_video):
    action = 'upload_video' if is_video else 'upload_photo'
    bot.send_chat_action(chat_id, action)

    r = requests.get(media_url, stream=True)
    if r.status_code == 200:
        media = r.content
        if is_video:
            bot.send_video(chat_id, media)
        else:
            bot.send_photo(chat_id, media)
    else:
        bot.send_message(chat_id, "⚠️ Failed to fetch media.")

# Start polling
print("🤖 Bot is running... by @imraj569")
bot.polling()
