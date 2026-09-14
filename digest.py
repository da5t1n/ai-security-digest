import os
import feedparser
import datetime
import requests

# --- НАСТРОЙКИ TELEGRAM ---
TG_TOKEN = os.environ.get("TG_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")

# --- НАСТРОЙКИ AI (Pollinations.ai - бесплатно, без ключей) ---
LLM_URL = "https://text.pollinations.ai/openai"

FEEDS = [
    "https://habr.com/ru/flows/security/rss/",
    "https://www.tadviser.ru/rss/",
    "https://www.anti-malware.ru/rss",
    "https://thehackernews.com/feeds/posts/default",
]

KEYWORDS = ["иИ", "ai ", "llm", "нейросет", "machine learning", "prompt", "агентн", "gpt", "llama", "кибербезопасность"]

def get_news():
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
    items = []
    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:
                title = entry.get("title", "")
                link = entry.get("link", "")
                summary = entry.get("summary", "")
                text_to_check = (title + " " + summary).lower()
                
                if any(kw in text_to_check for kw in KEYWORDS):
                    items.append(f"• {title}\n  {link}")
        except Exception:
            continue
    
    if not items:
        return "Явных новостей по ИИ в ИБ за 24 часа не найдено. Сформируй краткий обзор ключевых трендов 2026 года (агентные угрозы, отравление данных, гомоморфное шифрование)."
    
    return "\n\n".join(items[:20])

def generate_digest(news_text):
    prompt = f"""Ты — эксперт по информационной безопасности. Сделай ежедневный дайджест по ИБ в сфере ИИ.
Формат строго:
1. 🚨 Угрозы и риски (3–4 пункта, кратко, с контекстом).
2. 💡 Прорывные решения и факты (3–4 пункта).
3. 🔗 Источники (2–3 ссылки из текста).
Тон: для специалиста по ИБ, без воды, максимум 400 слов. Используй Markdown.

Новости для анализа:
{news_text}"""

    headers = {"Content-Type": "application/json"}
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "model": "llama", # Нативная модель, без OpenAI-обертки и её лимитов
        "private": True
    }
    
    # ВАЖНО: обращаемся к корневому адресу, а не к /openai
    response = requests.post("https://text.pollinations.ai/", headers=headers, json=payload, timeout=60)
    
    if response.status_code != 200:
        print(f"❌ Ошибка API: {response.status_code}")
        print(f"Ответ сервера: {response.text}")
        response.raise_for_status()
    
    # Pollinations может вернуть JSON или чистый текст, обрабатываем оба варианта
    try:
        data = response.json()
        if "response" in data:
            return data["response"]
        elif "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            return str(data)
    except:
        return response.text
    
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
    
    print("Генерация дайджеста...")
    digest = generate_digest(news)
    
    print("Отправка в Telegram...")
    send_to_telegram(digest)
    print("Готово!")
