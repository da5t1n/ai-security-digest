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
        print(f"   📡 Парсим {url}...", flush=True)
        try:
            feed = feedparser.parse(url, request_headers={'User-Agent': 'Mozilla/5.0'})
            for entry in feed.entries[:15]:
                title = entry.get("title", "")
                link = entry.get("link", "")
                summary = entry.get("summary", "")
                text_to_check = (title + " " + summary).lower()
                
                if any(kw in text_to_check for kw in KEYWORDS):
                    items.append(f"• {title}\n  {link}")
        except Exception as e:
            print(f"   ⚠️ Ошибка парсинга {url}: {e}", flush=True)
            continue
    
    if not items:
        return "Явных новостей по ИИ в ИБ за 24 часа не найдено. Сформируй краткий обзор ключевых трендов 2026 года (агентные угрозы, отравление данных, гомоморфное шифрование)."
    
    return "\n\n".join(items[:20])

def generate_digest(news_text: str) -> str:
    """Генерирует дайджест новостей с помощью YandexGPT."""
    
    folder_id = os.getenv("YANDEX_FOLDER_ID")
    api_key = os.getenv("LLM_API_KEY")
    
    if not folder_id or not api_key:
        raise ValueError("❌ ОШИБКА: Не заданы секреты YANDEX_FOLDER_ID или LLM_API_KEY в настройках GitHub Actions!")

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {api_key}",
        "x-folder-id": folder_id
    }

    today = datetime.datetime.now().strftime("%d.%m.%Y")
    
    prompt = f"""Ты эксперт в области информационной безопасности. 
Проанализируй следующие новости и составь структурированный дайджест на русском языке.

ВАЖНО: Используй простую Markdown-разметку:
- Заголовки категорий выделяй **жирным** (например: **🚨 Критические уязвимости**)
- Названия уязвимостей, CVE выделяй `моноширинным шрифтом` (например: `CVE-2024-1234`)
- Используй эмодзи для категорий: 🚨 🛡️ 🤖 📊 🌐
- НЕ используй сложные конструкции Markdown

СТРУКТУРА:
1. Заголовок: **📰 Дайджест новостей ИБ за {today}**
2. Раздели на 3-4 категории с эмодзи
3. В каждой категории 2-3 новости (кратко + ссылка)
4. В конце: **💡 Главный вывод дня** (1 предложение)

НОВОСТИ:
{news_text}
"""

        payload = {
        "modelUri": f"gpt://{folder_id}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": "2000"
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты эксперт по кибербезопасности. Форматируй ответы с Markdown."
            },
            {
                "role": "user",
                "text": prompt
            }
        ]
    }
import feedparser
import datetime
import requests

# Принудительный вывод для отлаimport os
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
        print(f"   📡 Парсим {url}...", flush=True)
        try:
            feed = feedparser.parse(url, request_headers={'User-Agent': 'Mozilla/5.0'})
            for entry in feed.entries[:15]:
                title = entry.get("title", "")
                link = entry.get("link", "")
                summary = entry.get("summary", "")
                text_to_check = (title + " " + summary).lower()
                
                if any(kw in text_to_check for kw in KEYWORDS):
                    items.append(f"• {title}\n  {link}")
        except Exception as e:
            print(f"   ⚠️ Ошибка парсинга {url}: {e}", flush=True)
            continue
    
    if not items:
        return "Явных новостей по ИИ в ИБ за 24 часа не найдено. Сформируй краткий обзор ключевых трендов 2026 года (агентные угрозы, отравление данных, гомоморфное шифрование)."
    
    return "\n\n".join(items[:20])

def generate_digest(news_text: str) -> str:
    """Генерирует дайджест новостей с помощью YandexGPT."""
    
    folder_id = os.getenv("YANDEX_FOLDER_ID")
    api_key = os.getenv("LLM_API_KEY")
    
    if not folder_id or not api_key:
        raise ValueError("❌ ОШИБКА: Не заданы секреты YANDEX_FOLDER_ID или LLM_API_KEY в настройках GitHub Actions!")

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {api_key}",
        "x-folder-id": folder_id
    }

    today = datetime.datetime.now().strftime("%d.%m.%Y")
    
    prompt = f"""Ты эксперт в области информационной безопасности. 
Проанализируй следующие новости и составь структурированный дайджест на русском языке.

ВАЖНО: Используй простую Markdown-разметку:
- Заголовки категорий выделяй **жирным** (например: **🚨 Критические уязвимости**)
- Названия уязвимостей, CVE выделяй `моноширинным шрифтом` (например: `CVE-2024-1234`)
- Используй эмодзи для категорий: 🚨 🛡️ 🤖 📊 🌐
- НЕ используй сложные конструкции Markdown

СТРУКТУРА:
1. Заголовок: **📰 Дайджест новостей ИБ за {today}**
2. Раздели на 3-4 категории с эмодзи
3. В каждой категории 2-3 новости (кратко + ссылка)
4. В конце: **💡 Главный вывод дня** (1 предложение)

НОВОСТИ:
{news_text}
"""

    payload = {
        "modelUri": f"gpt://{дки
print("🚀 СКРИПТ ЗАПУЩЕН УСПЕШНО!", flush=True)
print(f"🚀 TG_CHAT_ID из окружения: {os.getenv('TG_CHAT_ID')}", flush=True)

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

import datetime

def generate_digest(news_text: str) -> str:
    # Получаем текущую дату
    today = datetime.datetime.now().strftime("%d.%m.%Y")
    
    # ... остальной код ...
    
    # В промпте замени [дата] на {today}
    prompt = f"""...
СТРУКТУРА ДАЙДЖЕСТА:
1. Начни с заголовка: **📰 Дайджест новостей ИБ за {today}**
...
"""
    
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
            "temperature": 0.6,
            "maxTokens": "2000"
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты эксперт по кибербезопасности. Форматируй ответы с Markdown."
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
    """Отправляет сообщение в Telegram с обработкой ошибок форматирования."""
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    
    # Пробуем отправить с Markdown
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",  # Обычный Markdown (более совместимый)
        "disable_web_page_preview": False  # Разрешаем превью ссылок
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("✅ Сообщение отправлено с Markdown-форматированием")
        
    except requests.exceptions.HTTPError as e:
        # Если Markdown сломался (например, неправильная разметка), отправляем как обычный текст
        print(f"⚠️ Ошибка Markdown, отправляю как обычный текст: {e}")
        
        payload_fallback = {
            "chat_id": TG_CHAT_ID,
            "text": text,
            "disable_web_page_preview": False
        }
        response = requests.post(url, json=payload_fallback)
        response.raise_for_status()
        print("✅ Сообщение отправлено без форматирования")   
   
