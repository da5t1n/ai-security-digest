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

import requests
import json
import os

def generate_digest (news_text: str) -> str:
    """
    Генерирует дайджест новостей с помощью YandexGPT.
    """
    # ВАЖНО: Никогда не храните ключи в коде! Используйте переменные окружения.
    # В GitHub Actions их нужно добавить в Settings -> Secrets and variables -> Actions
    folder_id = os.getenv("YANDEX_FOLDER_ID", "ваш_folder_id")
    api_key = os.getenv("LLM_API_KEY", "ваш_api_key") 
    # Или используйте IAM_TOKEN вместо API_KEY: os.getenv("LLM_API_KEY")

    if folder_id == "ваш_folder_id" or api_key == "ваш_api_key":
        raise ValueError("Не заданы YANDEX_FOLDER_ID или LLM_API_KEY в переменных окружения")

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {api_key}", # Если используете IAM-токен, замените на f"Bearer {iam_token}"
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

    try:
        print("Генерация дайджеста через YandexGPT...")
        response = requests.post(url, headers=headers, json=payload)
        
        # Проверяем статус ответа (вызовет ошибку, если не 2xx)
        response.raise_for_status()
        
        result = response.json()
        
        # Извлекаем сгенерированный текст из ответа Yandex
        digest_text = result["result"]["alternatives"][0]["message"]["text"]
        return digest_text

    except requests.exceptions.HTTPError as e:
        print(f"❌ Ошибка API YandexGPT: {e}")
        print(f"Ответ сервера: {response.text}")
        raise
    except Exception as e:
        print(f"❌ Неожиданная ошибка при генерации дайджеста: {e}")
        raise

# Пример вызова (замените ваш старый вызов generate_digest(news) на этот):
# digest = generate_digest_yandexgpt(news)
    
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
