import os
import feedparser
import datetime
import requests

# --- НАСТРОЙКИ TELEGRAM ---
TG_TOKEN = os.environ.get("TG_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")

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

def generate_digest(news_text: str) -> str:
    """Генерирует дайджест новостей с помощью YandexGPT."""
    
    # Получаем переменные окружения
    folder_id = os.getenv("YANDEX_FOLDER_ID")
    api_key = os.getenv("LLM_API_KEY")
    
    # Надежная проверка на пустоту
    if not folder_id or not api_key:
        raise ValueError("❌ ОШИБКА: Не заданы секреты YANDEX_FOLDER_ID или LLM_API_KEY в настройках GitHub Actions!")

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {api_key}",
        "x-folder-id": folder_id
    }

    prompt = f"""Ты эксперт в области информационной безопасности. 
    Проанализируй следующие новости и составь краткий, структурированный дайджест на русском языке. 
    Выдели главные угрозы, уязвимости или события. Используй маркированные списки.
    
    Новости:
    {news_text}
    """

    payload = {
        "modelUri": f"gpt://{folder_id}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.5,
            "maxTokens": "1500"
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты полезный ассистент, эксперт по кибербезопасности. Отвечай четко и по делу."
            },
            {
                "role": "user",
                "text": prompt
            }
        ]
    }

    print("Отправка запроса к YandexGPT...")
    response = requests.post(url, headers=headers, json=payload)
    
    # Если ключ неверный, здесь будет ошибка 401
    response.raise_for_status()
    
    result = response.json()
    
    # Извлекаем текст из ответа Yandex
    digest_text = result["result"]["alternatives"][0]["message"]["text"]
    return digest_text

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    response = requests.post(url, json={
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    })
    response.raise_for_status()

if __name__ == "__main__":
    print("Сбор новостей...")
    news = get_news()
    
    print("Генерация дайджеста...")
    digest = generate_digest(news)
    
    print("Отправка в Telegram...")
    send_to_telegram(digest)
    print("Готово! ✅")
