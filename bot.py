import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction, ParseMode
import requests
import time


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "🌟 *Selamat Datang di Bot Reno!* 🌟\n\n"
        "Saya asisten AI yang siap membantu Anda dengan:\n"
        "• Pertanyaan umum\n• Diskusi teknologi\n• Rekomendasi\n• Dan banyak lagi!\n\n"
        "Gunakan /help untuk melihat petunjuk penggunaan"
    )
    await update.message.reply_text(welcome_msg, parse_mode=ParseMode.MARKDOWN)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_msg = (
        "🆘 *Bantuan dan Petunjuk* 🆘\n\n"
        "Cara menggunakan bot:\n"
        "1. Langsung ketik pertanyaan Anda\n"
        "2. Tunggu beberapa saat\n"
        "3. Dapatkan jawaban terformat rapi\n\n"
        "Contoh pertanyaan:\n"
        "- Jelaskan teori relativitas secara singkat\n"
        "- Bagaimana cara membuat website?\n"
        "- Berikan contoh kode Python untuk loop"
    )
    await update.message.reply_text(help_msg, parse_mode=ParseMode.MARKDOWN)


def format_response(response):
    """Format respons API menjadi struktur Markdown yang lebih baik"""
    response = response.replace("**", "*").replace("\n- ", "\n• ")
    return f"📚 **Jawaban:**\n\n{response}"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action=ChatAction.TYPING
        )
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "Berikan jawaban dalam Markdown dengan struktur jelas menggunakan poin-poin, bold, dan pemformatan tepat."
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ],
            "temperature": 0.7
        }
        
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        raw_reply = result['choices'][0]['message']['content']
        formatted_reply = format_response(raw_reply)
        
        iklan = (
            "\n\n---\n"
            "📢 *ADS:*\n"
            "`Ingin tukar rupiah ke dolar atau sebaliknya?` `[Reno Exchange]` *@PT717TT* `untuk kurs terbaik!`"
        )
        formatted_reply += iklan
        
        max_length = 4096
        for i in range(0, len(formatted_reply), max_length):
            await update.message.reply_text(
                formatted_reply[i:i+max_length],
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )
            time.sleep(1)  
            
    except requests.exceptions.RequestException as e:
        error_msg = "_⚠️ Maaf, sedang ada masalah koneksi. Silakan coba lagi nanti..._"
        await update.message.reply_text(error_msg, parse_mode=ParseMode.MARKDOWN)
        logging.error(f"Request error: {e}")
        
    except Exception as e:
        error_msg = (
            f"_❌ Terjadi kesalahan:_\n\n"
            f"`{str(e)}`\n\n"
            f"Silakan coba pertanyaan lain atau coba lagi nanti."
        )
        await update.message.reply_text(error_msg, parse_mode=ParseMode.MARKDOWN)
        logging.error(f"Unexpected error: {e}")


if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()
    
    
    handlers = [
        CommandHandler("start", start),
        CommandHandler("help", help_command),
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    ]
    
    for handler in handlers:
        application.add_handler(handler)
    
    
    application.run_polling()
