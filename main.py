import telebot
from telebot import types
import asyncio
from shazamio import Shazam
import os

# توکن ربات شما (از قبل تنظیم شده)
TOKEN = '7892120008:AAG7iK-5W0kZ6_8h9eWvXp_Qf7_e7o0I'
# آیدی کانال‌ها با @
CHANNELS = ['@alfafunk_muzekfunk7edet', '@FUNK_FUNKMUSIC_EDIT']

bot = telebot.TeleBot(TOKEN)

def check_membership(user_id):
    for channel in CHANNELS:
        try:
            status = bot.get_chat_member(channel, user_id).status
            if status in ['left', 'kicked']:
                return False
        except Exception as e:
            print(f"Error checking channel {channel}: {e}")
            return False
    return True

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if check_membership(user_id):
        bot.send_message(message.chat.id, "✅ عضویت شما تایید شد!\nحالا ویدیویی که می‌خواهید آهنگش را پیدا کنم بفرستید.")
    else:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("کانال اول 📢", url=f"https://t.me/{CHANNELS[0][1:]}")
        btn2 = types.InlineKeyboardButton("کانال دوم 📢", url=f"https://t.me/{CHANNELS[1][1:]}")
        check_btn = types.InlineKeyboardButton("✅ عضو شدم (بررسی)", callback_data="check_sub")
        markup.add(btn1, btn2)
        markup.add(check_btn)
        bot.send_message(message.chat.id, "🛑 برای استفاده از ربات باید در کانال‌های ما عضو شوید:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def check_callback(call):
    if check_membership(call.from_user.id):
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        bot.send_message(call.message.chat.id, "✨ خوش آمدید! حالا ویدیوی خود را بفرستید.")
    else:
        bot.answer_callback_query(call.id, "⚠️ شما هنوز در تمام کانال‌ها عضو نشده‌اید!", show_alert=True)

async def find_song(file_path):
    shazam = Shazam()
    try:
        out = await shazam.recognize(file_path)
        return out
    except Exception as e:
        print(f"Shazam error: {e}")
        return None

@bot.message_handler(content_types=['video', 'video_note', 'document'])
def handle_video(message):
    if not check_membership(message.from_user.id):
        start(message)
        return

    file_id = None
    if message.content_type == 'video':
        file_id = message.video.file_id
    elif message.content_type == 'video_note':
        file_id = message.video_note.file_id
    elif message.content_type == 'document':
        if message.document.mime_type and 'video' in message.document.mime_type:
            file_id = message.document.file_id

    if not file_id:
        bot.reply_to(message, "❌ لطفا یک فایل ویدیویی بفرستید.")
        return

    status_msg = bot.reply_to(message, "🔍 در حال دریافت ویدیو و استخراج آهنگ... لطفا صبر کنید.")

    try:
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # ذخیره موقت فایل
        temp_filename = f"temp_{message.chat.id}_{file_id}.mp4"
        with open(temp_filename, 'wb') as new_file:
            new_file.write(downloaded_file)

        # تغییر متن پیام برای کاربر
        bot.edit_message_text("🎵 در حال آنالیز صدا با هوش مصنوعی Shazam...", chat_id=message.chat.id, message_id=status_msg.message_id)

        # اجرای Shazam به صورت async
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(find_song(temp_filename))
        loop.close()

        # پاک کردن فایل موقت بعد از اتمام کار
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

        if result and 'track' in result:
            track = result['track']
            title = track.get('title', 'نامشخص')
            subtitle = track.get('subtitle', 'نامشخص')
            
            response_text = f"✅ آهنگ پیدا شد!\n\n🎵 نام آهنگ: {title}\n👤 خواننده: {subtitle}"
share_url = track.get('share', {}).get('href')
            if share_url:
                response_text += f"\n\n🔗 لینک شنیدن: {share_url}"
            
            bot.edit_message_text(response_text, chat_id=message.chat.id, message_id=status_msg.message_id)
        else:
            bot.edit_message_text("❌ متاسفانه نتوانستم آهنگی در این ویدیو پیدا کنم. مطمئن شوید صدا واضح است.", chat_id=message.chat.id, message_id=status_msg.message_id)

    except Exception as e:
        print(f"Error: {e}")
        bot.edit_message_text("اوه ببخشید! دارم دوباره با دقت بیشتر بررسی می‌کنم...", chat_id=message.chat.id, message_id=status_msg.message_id)

bot.infinity_polling()
