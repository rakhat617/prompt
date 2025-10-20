import re
import json
import os
import requests

import google.generativeai as genai

from dotenv import load_dotenv

from json_to_txt import get_examples_text

load_dotenv()


# with open("examples.txt", "r", encoding="utf-8") as f:
#     examples_text = f.read()

examples_text = get_examples_text()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

ID_INSTANCE = os.getenv("ID_INSTANCE")
API_TOKEN_INSTANCE = os.getenv("API_TOKEN_INSTANCE")
API_URL = os.getenv("API_URL")
CLIENT_PHONE_NUMBER = os.getenv("CLIENT_PHONE_NUMBER")

url = f"{API_URL}/waInstance{ID_INSTANCE}/getChatHistory/{API_TOKEN_INSTANCE}"

payload = {
    "chatId": f"{CLIENT_PHONE_NUMBER}@c.us", 
    "count": 10
}
headers = {
  'Content-Type': 'application/json'
}

response = requests.post(url, json=payload)
messages = response.json()
messages = list(reversed(messages))

chat_history = """"""
deal_start_time = 0 # ПЕРЕМЕННАЯ ДЛЯ ВРЕМЕНИ НАЧАЛА СДЕЛКИ 

for message in messages:
    if message["typeMessage"] != "textMessage" and message["typeMessage"] != "extendedTextMessage":
        continue
    if message["timestamp"] < deal_start_time:
        continue
    if message["type"] == "outgoing":
        chat_history += "Оператор: " + message["textMessage"] + "\n"
    elif message["type"] == "incoming":
        chat_history += "Клиент: " + message["textMessage"] + "\n"

print(chat_history)


system_prompt = f"""
Ты — интеллектуальный классификатор обращений клиентов оптики.

Твоя задача — определить **причину обращения клиента** по истории чата.  
Выбирай **только одну причину** из списка ниже.

Если в истории нет конкретного вопроса, и клиент просто не ответил — укажи `"Не ответил"`.  
Если обращение завершилось без ответа или автоматически закрыто системой — укажи `"Закрыта автоматически"`.

Список возможных причин обращения:
1. Уведомления
2. Услуга подбора МКЛ (проверка)
3. Услуга детская проверка зрения
4. Услуга лечение глаз
5. Услуга ремонта очков
6. Услуга трэйдин
7. Услуга сверки очков на точность
8. Купить очки для зрения
9. Купить очковые линзы
10. Купить СЗ
11. Купить МКЛ
12. Купить подарочный сертификат
13. Покупка повторного заказа очков для зрения
14. Узнать статус заказа
15. Сотрудничество
16. Найм
17. Услуга подбора очков (проверка)
18. Отзывы и обратная связь
19. Не ответил
20. Закрыта автоматически

Инструкция:
- Проанализируй сообщение или диалог клиента.
- Определи, какая категория из списка выше наиболее точно описывает цель обращения.
- Используй только одну категорию.
- Ответ должен быть строго в формате JSON:
{{
  "reason": "<название категории>"
}}
- Не добавляй комментариев, объяснений или текста вне JSON.

---

{examples_text}

---

Теперь классифицируй по следующей истории сообщений с клиентом:
"""


model = genai.GenerativeModel("models/gemini-2.5-flash")

response = model.generate_content(
    [
        {"role": "user", "parts": system_prompt + "\n" + chat_history}
    ],
    generation_config=genai.types.GenerationConfig(
        temperature=0.0,
    )
)

answer = response.text.strip() if response.text else ""

if not answer:
    print("Модель не вернула текстовый ответ.")
else:
    # Удаляем обёртку ```json ... ```
    cleaned = re.sub(r"^```json|```$", "", answer.strip(), flags=re.MULTILINE).strip()

    try:
        data = json.loads(cleaned)
        print(data)
    except json.JSONDecodeError:
        print("Ошибка парсинга JSON. Вот что вернулось:")
        print(answer)
