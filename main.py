from rubika import Bot
from shazamio import Shazam
import asyncio
import os

# تنظیمات اصلی روبیکا
TOKEN = "BIFBDD0UZWINMELTHUCHDXQURFUQVHJAORIHHOTFUWGAUXGMHZDALBYSLGTCNQZE"
# لیست کانال‌هایی که کاربر باید عضو شود
CHANNELS = ["@FUNK_FUNKMUSIC_EDIT", "@alfafunk_muzekfunk7edet"]

bot = Bot(TOKEN)

@bot.on_message()
async def handle_message(msg):
    if msg.is_private:
        user_id = msg.author_id
        
        if msg.text == "/start":
            await bot.send_message(msg.chat_id, "سلام! خوش آمدید.\nبرای استفاده از ربات لطفا در کانال‌های ما عضو شوید و سپس آهنگ یا وویس خود را ارسال کنید. 🎵")
            return

        # بررسی وجود فایل (آهنگ یا وویس)
        if msg.file:
            try:
                await bot.send_message(msg.chat_id, "درحال پردازش و شناسایی آهنگ... لطفاً کمی صبر کنید 🚀")
                
                # دانلود فایل در پوشه موقت
                file_path = await bot.download_file(msg.file)
                
                shazam = Shazam()
                out = await shazam.recognize_song(file_path)
                
                if 'track' in out:
                    track = out['track']
                    title = track.get('title', 'نامشخص')
                    artist = track.get('subtitle', 'نامشخص')
                    await bot.send_message(msg.chat_id, f"✅ آهنگ پیدا شد!\n\n🎵 نام آهنگ: {title}\n👤 هنرمند: {artist}")
                else:
                    await bot.send_message(msg.chat_id, "متاسفانه شزم نتوانست این آهنگ را شناسایی کند. ❌")
                
                # حذف فایل برای پر نشدن حافظه سرور
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
            except Exception as e:
                print(f"Error: {e}")
                await bot.send_message(msg.chat_id, "خطایی در شناسایی رخ داد. لطفاً دوباره تلاش کنید.")

# اجرای ربات
if __name__ == "__main__":
    print("Bot is running...")
    bot.run()
