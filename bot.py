import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("8077603292:AAGBw6NrqhqsNbdZ-YCI2F96TbrdupwKgHA")
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

# Start command (VPN ads removed)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 ආයුබෝවන්! ඡායාරූප හෝ වීඩියෝවක් එවන්න, Full Video Download link ලබා දෙන්නම්! 💋")

# Handle media upload (Kamadenuwa BOT style)
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
        await message.reply_text("කරුණාකර ඡායාරූප හෝ වීඩියෝවක් එවන්න!")
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

    # Send response like Kamadenuwa BOT
    caption = f"🔥 මෙම එකතුව ඇතුලම චිකි! 💋\nකාමදෙනුව 15 ක් ඇතුලත ගිහින් Full Video Download කරන්න:\n{file_link}"
    keyboard = [
        [InlineKeyboardButton("Full Video", url=file_link)],
        [InlineKeyboardButton("Download", url=file_link)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_photo(photo=open(file_path, 'rb'), caption=caption, reply_markup=reply_markup)

# Handle download request
async def handle_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    last_message = await update.message.chat.get_messages(offset=-1, limit=1)
    if last_message[0].photo or last_message[0].video:
        file_link = [btn.url for row in last_message[0].reply_markup.inline_keyboard for btn in row if btn.text in ["Full Video", "Download"]][0]
        await update.message.reply_text(f"🔥 Full Video Download: {file_link}")
    else:
        await update.message.reply_text("මුලින් ඡායාරූප/වීඩියෝවක් එවන්න!")

# Main function
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.regex(r'(?i)(download|full video)'), handle_download))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
