import os
import feedparser
import datetime
import requests

# --- НАСТРОЙКИ ---
TG_TOKEN = os.environ.get("TG_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")
LLM_KEY = os.environ.get("LLM_API_KEY")

# Бесплатная модель на OpenRouter (Qwen 2.5 72B отлично работает с русским)
LLM_MODEL = "qwen/qwen-2.5-72b-instruct:free" 
# Альтернатива на Groq (если OpenRouter тормозит): модель "llama3-70b-8192", URL "https://api.groq.com/openai/v1/chat/completions"

FEEDS = [
    "https://habr.com/ru/flows/security/rss/",
    "https://www.tadviser.ru/rss/",
    "https://www.anti-malware.ru/rss",
    "https://thehackernews.com/feeds/posts/default",
    "https://feeds.feedburner.com/TechCrunch/ArtificialIntelligence"
]

KEYWORDS = ["иИ", "ai ", "llm", "нейросет", "machine learning", "prompt", "агентн", "gpt", "llama"]

def get_news():
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
    items = []
    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]: # Берем последние 15 записей из каждого
                title = entry.get("title", "")
                link = entry.get("link", "")
                summary = entry.get("summary", "")
                text_to_check = (title + " " + summary).lower()
                
                # Фильтр по ключевым словам ИИ
                if any(kw in text_to_check for kw in KEYWORDS):
                    items.append(f"• {title}\n  {link}")
        except Exception:
            continue
    
    return "\n\n".join(items[:20]) # Ограничиваем 20 новостями, чтобы не превысить лимит токенов

def generate_digest(news_text):
    prompt = f"""Ты — эксперт по информационной безопасности. Сделай ежедневный дайджест по ИБ в сфере ИИ на основе этих новостей.
Формат строго:
1. Раздел "🚨 Угрозы и риски" (3–4 пункта, кратко, с указанием источника/контекста).
2. Раздел "💡 Прорывные решения и факты" (3–4 пункта).
3. Раздел "🔗 Источники" (2–3 ссылки из текста).
Тон: для специалиста по ИБ, без воды, максимум 400 слов. Если новостей мало, сделай выводы на основе общих трендов 2026 года.

Новости для анализа:
{news_text}"""

    headers = {
        "Authorization": f"Bearer {LLM_KEY}",
        "HTTP-Referer": "https://github.com", # Требуется OpenRouter
        "X-Title": "AI Security Digest"
    }
    payload = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    })

if __name__ == "__main__":
    print("Сбор новостей...")
    news = get_news()
    if not news:
        news = "За последние 24 часа явных новостей по ИИ в ИБ не найдено. Сформируй дайджест на основе ключевых трендов 2026 года (агентные угрозы, отравление данных, гомоморфное шифрование)."
    
    print("Генерация дайджеста...")
    digest = generate_digest(news)
    
    print("Отправка в Telegram...")
    send_to_telegram(digest)
    print("Готово!")
