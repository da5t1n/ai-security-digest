import os
import feedparser
import datetime
import requests
import time

# --- НАСТРОЙКИ TELEGRAM ---
TG_TOKEN = os.environ.get("TG_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")

# --- ТОЛЬКО РУССКОЯЗЫЧНЫЕ ИСТОЧНИКИ ---
FEEDS = [
    "https://habr.com/ru/flows/security/rss/",
    "https://www.tadviser.ru/rss/",
    "https://www.anti-malware.ru/rss",
    "https://tg.i-c-a.su/rss/kiber_boloid",
    "https://www.securitylab.ru/news/rss.php",
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
                    # Форматируем так, чтобы нейросеть НЕ могла потерять ссылку
                    items.append(f"ЗАГОЛОВОК: {title}\nССЫЛКА: {link}")
        except Exception as e:
            print(f"   ⚠️ Ошибка парсинга {url}: {e}", flush=True)
            continue
    
    if not items:
        return "Явных новостей по ИИ в ИБ за 24 часа не найдено. Сформируй краткий обзор ключевых трендов 2026 года (агентные угрозы, отравление данных, гомоморфное шифрование)."
    
    return "\n\n---\n\n".join(items[:20])

def generate_digest(news_text: str) -> str:
    """Генерирует дайджест новостей с помощью YandexGPT."""
    
    folder_id = os.getenv("YANDEX_FOLDER_ID")
    api_key = os.getenv("LLM_API_KEY")
    
    if not folder_id or not api_key:
        raise ValueError("❌ ОШИБКА: Не заданы секреты YANDEX_FOLDER_ID или LLM_API_KEY!")

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {api_key}",
        "x-folder-id": folder_id
    }

    today = datetime.datetime.now().strftime("%d.%m.%Y")
    
    # УСИЛЕННЫЙ ПРОМПТ С ЖЕСТКИМ ТРЕБОВАНИЕМ СОХРАНЯТЬ ССЫЛКИ
    prompt = f"""Ты эксперт в области информационной безопасности. 
Проанализируй следующие новости и составь структурированный дайджест на русском языке.

КРИТИЧЕСКИ ВАЖНО: Ты обязан сохранить гиперссылки на первоисточники для каждой новости!
Используй формат гиперссылок Telegram Markdown: [Текст ссылки](URL)

СТРУКТУРА ДАЙДЖЕСТА:
1. Заголовок: **📰 Дайджест новостей ИБ за {today}**
2. Раздели новости на 3-4 тематические категории с эмодзи (🚨 🛡️ 🤖 📊 🌐).
3. В каждой категории опиши 2-4 новости. 
   Формат каждой новости должен быть СТРОГО таким:
   📌 **Краткая суть новости (1-2 предложения)**
   🔗 [Читать первоисточник](точная_ссылка_из_входных_данных)
4. В конце добавь раздел: **💡 Главный вывод дня** (1 предложение).

НЕ ВЫДУМЫВАЙ ссылки. Используй только те URL, которые предоставлены во входных данных.

ВХОДНЫЕ ДАННЫЕ (НОВОСТИ):
{news_text}
"""

    payload = {
        "modelUri": f"gpt://{folder_id}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.5, # Чуть ниже температура для большей точности следования инструкциям
            "maxTokens": "1500" # Чуть увеличили лимит, чтобы хватило места на ссылки
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты эксперт по кибербезопасности. Строго следуй инструкциям по форматированию, особенно в части сохранения URL-адресов."
            },
            {
                "role": "user",
                "text": prompt
            }
        ]
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"🧠 Отправка запроса к YandexGPT (попытка {attempt + 1}/{max_retries})...", flush=True)
            
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            digest_text = result["result"]["alternatives"][0]["message"]["text"]
            
            print(f"✅ Дайджест сгенерирован. Длина: {len(digest_text)} символов", flush=True)
            return digest_text
            
        except requests.exceptions.ReadTimeout:
            print(f"⏳ Превышено время ожидания. Повторная попытка через 5 секунд...", flush=True)
            time.sleep(5)
        except Exception as e:
            print(f"❌ Ошибка API (не таймаут): {e}", flush=True)
            raise
            
    raise Exception("Не удалось получить ответ от YandexGPT после нескольких попыток.")

def send_to_telegram(text):
    """Отправляет сообщение в Telegram."""
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    
    print(f"📤 Отправка в Telegram (chat_id: {TG_CHAT_ID})...", flush=True)
    print(f"📏 Длина сообщения: {len(text)} символов", flush=True)
    
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True # True, чтобы не спамить превью картинок для каждой ссылки
    }
    
    response = requests.post(url, json=payload, timeout=30)
    print(f"📥 Ответ Telegram: {response.status_code}", flush=True)
    
    if response.status_code == 200:
        print("✅ Сообщение отправлено с Markdown!", flush=True)
        return
    
    print(f"⚠️ Markdown не сработал: {response.text}", flush=True)
    print("📤 Пробую без форматирования...", flush=True)
    
    payload_simple = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "disable_web_page_preview": True
    }
    
    response = requests.post(url, json=payload_simple, timeout=30)
    print(f"📥 Ответ Telegram (без Markdown): {response.status_code}", flush=True)
    
    if response.status_code == 200:
        print("✅ Сообщение отправлено без форматирования!", flush=True)
    else:
        print(f"❌ Ошибка отправки: {response.text}", flush=True)
        response.raise_for_status()

if __name__ == "__main__":
    print("=" * 60, flush=True)
    print("🚀 НАЧАЛО ВЫПОЛНЕНИЯ СКРИПТА", flush=True)
    print("=" * 60, flush=True)
    
    try:
        print("\n1️⃣ СБОР НОВОСТЕЙ", flush=True)
        news = get_news()
        print(f"✅ Новости собраны. Длина: {len(news)} символов\n", flush=True)
        
        print("2️⃣ ГЕНЕРАЦИЯ ДАЙДЖЕСТА", flush=True)
        digest = generate_digest(news)
        print(f"✅ Дайджест готов\n", flush=True)
        
        print("3️⃣ ОТПРАВКА В TELEGRAM", flush=True)
        send_to_telegram(digest)
        
        print("\n" + "=" * 60, flush=True)
        print("🎉 ВСЕ ШАГИ УСПЕШНО ЗАВЕРШЕНЫ!", flush=True)
        print("=" * 60, flush=True)
        
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {type(e).__name__}: {e}", flush=True)
        import traceback
        traceback.print_exc()
        raise
