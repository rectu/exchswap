import requests
import time
import os

API_ENDPOINT = "https://exch.cx/api"
XMR_RESERVE_THRESHOLD = 10
FROM_CURRENCY = "ETH"
TO_CURRENCY = "XMR"

def send_telegram_message(bot_token, chat_id, message):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message,
    }
    response = requests.post(url, json=payload)
    return response.json()

def check_xmr_reserves():
    bot_token = 'TELEGRAM_BOT_HTTP_TOKEN'
    chat_id = 'TELEGRAM_GROUP_CHAT_ID'
    while True:
        try:
            # Send GET request to the API endpoint
            response = requests.get(f"{API_ENDPOINT}/rates")

            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()

                # Get the XMR reserve information
                xmr_reserve = data.get(f"{FROM_CURRENCY}_{TO_CURRENCY}", {}).get("reserve", 0)

                # Convert the reserve value to a floating-point number
                xmr_reserve = float(xmr_reserve)

                # Check if XMR reserves exceed the threshold
                if xmr_reserve > XMR_RESERVE_THRESHOLD:
                    exceed_text = (f"XMR reserves exceed {XMR_RESERVE_THRESHOLD} XMR available: {xmr_reserve} XMR")
                    print(exceed_text)
                    send_telegram_message(bot_token, chat_id, exceed_text)
                    os.system("start python purchaser.py")
                    waiting_text = ("Waiting 25 minutes before looking for more choices.")
                    send_telegram_message(bot_token, chat_id, waiting_text)
                    time.sleep(1500)
                else:
                    below_text = (f"XMR reserves are below {XMR_RESERVE_THRESHOLD} XMR available: {xmr_reserve} XMR")
                    print(below_text)
                    send_telegram_message(bot_token, chat_id, below_text)


            else:
                unabletofetch = (f"Error: Unable to fetch data from the API. Status code: {response.status_code}")
                print(unabletofetch)
                send_telegram_message(bot_token, chat_id, unabletofetch)

        except Exception as e:
            errorType = (f"Error occurred: {e}")
            send_telegram_message(bot_token, chat_id, errorType)

        # Wait for 15 seconds before checking again
        time.sleep(15)

check_xmr_reserves()
