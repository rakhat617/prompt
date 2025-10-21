import requests

def get_numbers_func(url):
    response = requests.request("GET", url)

    messages = response.json()
    numbers = []

    for message in messages:
        if "@g.us" in message["chatId"]:
            continue
        sender_id = message.get("senderId")
        sender_number = sender_id.split("@")[0]
        if sender_number not in numbers:
            numbers.append(sender_number)
    return numbers