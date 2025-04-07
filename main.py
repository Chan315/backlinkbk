import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# === SETUP GOOGLE SHEETS ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("backlink").sheet1  # Ganti sesuai nama spreadsheet kamu

# === LOGGING ===
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# === USER STATE ===
user_data = {}

# === START COMMAND ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("VIP1", callback_data="VIP1")],
        [InlineKeyboardButton("VIP2", callback_data="VIP2")],
        [InlineKeyboardButton("Traffic", callback_data="Traffic")],
        [InlineKeyboardButton("ID", callback_data="ID")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Silakan pilih menu:", reply_markup=reply_markup)

# === MENU PILIHAN ===
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data[user_id] = {"menu": query.data}
    await query.message.reply_text("Masukkan ID Pemesan:")

# === INPUT DATA SECARA BERTAHAP ===
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_data:
        await update.message.reply_text("Silakan mulai dengan perintah /start.")
        return

    data = user_data[user_id]

    if "id_pemesan" not in data:
        data["id_pemesan"] = update.message.text
        await update.message.reply_text("Masukkan link pesanan:")
    elif "link" not in data:
        data["link"] = update.message.text
        await update.message.reply_text("Masukkan anchor:")
    elif "anchor" not in data:
        data["anchor"] = update.message.text
        data["tanggal"] = datetime.now().strftime("%d-%m-%Y")

        # Simpan ke Google Sheets sesuai urutan kolom
        sheet.append_row([
            data["tanggal"],         # Kolom 1: Tanggal
            data["id_pemesan"],      # Kolom 2: ID Pemesan
            data["menu"],            # Kolom 3: Menu
            data["link"],            # Kolom 4: Link
            data["anchor"]           # Kolom 5: Anchor
        ])

        # Konfirmasi ke user
        await update.message.reply_text(
            f"Data berhasil disimpan:\n"
            f"Menu: {data['menu']}\n"
            f"ID Pemesan: {data['id_pemesan']}\n"
            f"Link: {data['link']}\n"
            f"Anchor: {data['anchor']}\n"
            f"Tanggal: {data['tanggal']}"
        )

        # Bersihkan data user
        user_data.pop(user_id)

# === MAIN FUNCTION ===
def main():
    token = "7042958306:AAHx2zDmIwPRm_XuA1XNYnFZmmw1VCG60l8"  # Ganti dengan token dari BotFather
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    app.run_polling()

if __name__ == '__main__':
    main()
    