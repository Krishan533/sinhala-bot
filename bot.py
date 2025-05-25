import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("7242103550:AAEW9qfGhIcmMeP3OOFjWKkb-74O9XkdBKA")
BLOGGER_LINK = os.getenv("https://alexahhj.blogspot.com/2025/05/blog-post.html")

# Google Drive setup
gauth = GoogleAuth()
gauth.LoadCredentialsFile("credentials/credentials.json")
if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()
gauth.SaveCredentialsFile("credentials/credentials.json")
drive = GoogleDrive(gauth)

# Media folder
MEDIA_FOLDER = "media"
if not os.path.exists(MEDIA_FOLDER):
    os.makedirs(MEDIA_FOLDER)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 ආයුබෝවන්! ඡායාරූප හෝ වීඩියෝවක් එවන්න, ලින්කය ලබා දෙන්නම්! 🔥")

async def send_vpn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 VPN Download Links:\n- iOS/Android/Windows/Mac: https://otieu.com/4/9377224 \n- Free Telegram Service: /start\nUnblock YouTube, Instagram, and more! 🚀")
app.add_handler(CommandHandler("vpn", send_vpn))

# Handle media (save and generate link)
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    file_id = None
    file_name = None

    if message.photo:
        file_id = message.photo[-1].file_id
        file_name = f"photo_{message.message_id}.jpg"
    elif message.video:
        file_id = message.video.file_id
        file_name = f"video_{message.message_id}.mp4"
    else:
        await message.reply_text("කරුණාකර ඡායාරූප හෝ වීඩියෝවක් එවන්න.")
        return

    # Download file
    file_info = await context.bot.get_file(file_id)
    file_path = os.path.join(MEDIA_FOLDER, file_name)
    await file_info.download_to_drive(file_path)

    # Upload to Google Drive
    file_drive = drive.CreateFile({'title': file_name})
    file_drive.SetContentFile(file_path)
    file_drive.Upload()
    file_drive.InsertPermission({'type': 'anyone', 'value': 'anyone', 'role': 'reader'})
    file_link = file_drive['alternateLink']

    # Share Blogger link with verification
    await message.reply_text(f"🔥 ලස්සන වීඩියෝවක්! බලන්න: {BLOGGER_LINK} (ලින්කය click කරලා red button එකට 12 seconds wait කරලා green button click කරන්න) 🔥")

# Retrieve media
async def retrieve_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text
    if "drive.google.com" in link:
        file_id = link.split("/d/")[1].split("/")[0]
        file_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        await context.bot.send_document(chat_id=update.message.chat_id, document=file_url)
    else:
        await update.message.reply_text("කරුණාකර වලංගු Google Drive ලින්කයක් එවන්න.")

# Main function
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, retrieve_media))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
