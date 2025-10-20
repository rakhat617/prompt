import json

_examples_cache = None 


def get_examples_text():
    global _examples_cache
    if _examples_cache is not None:
        return _examples_cache
    
    with open("examples.json", "r", encoding="utf-8") as f:
        examples = json.load(f)

    text = "Примеры:\n"
    for ex in examples:
        text += f'\nПричина: {ex["Ответ"]["reason"]}\n'
        text += f'Контекст: {ex.get("Контекст", "")}\n'
        text += "Примеры сообщений клиента:\n"
        for msg in ex["Примеры сообщений"]:
            text += f'- {msg}\n'
        text += "\n"

    _examples_cache = text
    return text