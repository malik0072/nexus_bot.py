import os
import sqlite3
import requests
from bs4 import BeautifulSoup
from telegram.ext import ApplicationBuilder, CommandHandler

# --- الإعدادات ---
# ملاحظة: تأكد أن اسم المتغير في Render هو BOT_TOKEN تماماً
TOKEN = os.environ.get("BOT_TOKEN")
DB_NAME = "nexus.db"

# --- قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute('CREATE TABLE IF NOT EXISTS links (url TEXT UNIQUE)')
    conn.commit()
    conn.close()

# --- محرك البحث والتحقق ---
def get_valid_links(query):
    search_url = f"https://www.google.com/search?q=site:t.me+{query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        links = []
        for a in soup.find_all('a', href=True):
            link = a['href']
            # استخراج الرابط الحقيقي من نتائج جوجل
            if "url?q=https://t.me/" in link:
                clean_link = link.split("url?q=")[1].split("&")[0]
                links.append(clean_link)
        
        return list(set(links))[:5]
    except Exception as e:
        print(f"Error searching: {e}")
        return []

# --- أوامر البوت ---
async def start(update, context):
    await update.message.reply_text("مرحباً بك في Nexus TG! اكتب /search [كلمة] للبحث.")

async def search_command(update, context):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("يرجى كتابة كلمة للبحث، مثال: /search programming")
        return
    
    status_msg = await update.message.reply_text("جاري البحث في تيلجرام... 🔍")
    results = get_valid_links(query)
    
    if results:
        await status_msg.edit_text("إليك النتائج:\n\n" + "\n".join(results))
    else:
        await status_msg.edit_text("لم يتم العثور على مجموعات.")

# --- التشغيل ---
if __name__ == '__main__':
    if not TOKEN:
        print("خطأ: يرجى إعداد BOT_TOKEN في إعدادات Render")
    else:
        init_db()
        print("جاري تشغيل البوت...")
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("search", search_command))
        print("Nexus TG يعمل الآن!")
        app.run_polling()
        
