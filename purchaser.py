import requests
import json
import time
import subprocess

bot_token = 'TELEGRAM_BOT_TOKEN'
chat_id = 'CHAT_ID'

def send_telegram_message(bot_token, chat_id, message):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message,
    }
    response = requests.post(url, json=payload)
    return response.json()

def create_exchange_order(purchaser_private_key, eth_rpc_url, from_currency, to_currency, to_address, refund_address=None, rate_mode='dynamic', fee_option='f'):
    # API endpoint for creating an exchange order
    api_url = 'https://exch.cx/api/create'

    # Request parameters
    data = {
        'from_currency': from_currency,
        'to_currency': to_currency,
        'to_address': to_address,
        'refund_address': refund_address,
        'rate_mode': rate_mode,
        'fee_option': fee_option,
    }

    headers = {
        'Authorization': "NEIN",
        'X-Requested-With': 'XMLHttpRequest'  # Set X-Requested-With header to mimic XHR request
    }

    try:
        response = requests.post(api_url, data=data, headers=headers)
        response_data = response.json()

        if 'orderid' in response_data:
            order_id = response_data['orderid']
            createdExch = (f"Exchange order created successfully. Order ID: {order_id}")
            print(createdExch)
            send_telegram_message(bot_token, chat_id, create_exchange_order)
            return order_id
        else:
            failedTocreate = ("Failed to create exchange order.")
            print(failedTocreate)
            send_telegram_message(bot_token, chat_id, failedTocreate)
            print(response_data)
            send_telegram_message(bot_token, chat_id, response_data)
            return None

    except requests.exceptions.RequestException as e:
        errorWhile = (f"Error occurred while creating exchange order: {e}")
        print(errorWhile)
        send_telegram_message(bot_token, chat_id, errorWhile)
        return None

def get_exchange_order_info(order_id):
    # API endpoint for getting exchange order information
    api_url = f'https://exch.cx/api/order?orderid={order_id}'

    headers = {
        'X-Requested-With': 'XMLHttpRequest'  # Set X-Requested-With header to mimic XHR request
    }

    try:
        response = requests.get(api_url, headers=headers)
        response_data = response.json()

        if 'state' in response_data:
            state = response_data['state']
            print(f"Exchange order state: {state}")
            return response_data
        else:
            print("Failed to retrieve exchange order information.")
            print(response_data)
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error occurred while retrieving exchange order information: {e}")
        return None

if __name__ == "__main__":
    # Load variables from config.json file
    with open('config.json') as config_file:
        config_data = json.load(config_file)

    purchaser_private_key = config_data.get('purchaser_private_key')
    eth_rpc_url = config_data.get('eth_rpc_url')
    from_currency = config_data.get('from_currency', 'ETH')
    to_currency = config_data.get('to_currency', 'XMR')
    to_address = config_data.get('to_address', 'RECEIVER_XMR_ADDRESS')
    refund_address = config_data.get('refund_address', None)
    rate_mode = config_data.get('rate_mode', 'dynamic')
    fee_option = config_data.get('fee_option', 'f')

# Create the exchange order
    order_id = create_exchange_order(
        purchaser_private_key, eth_rpc_url, from_currency, to_currency, to_address, refund_address, rate_mode, fee_option
    )

    # Get exchange order information
    if order_id:
        order_info = get_exchange_order_info(order_id)
        if order_info:
            print("Order information:")
            print("--------------------------------------------------------------------------------------")
            print(order_info)
            send_telegram_message(bot_token, chat_id, order_info)
            print("--------------------------------------------------------------------------------------")

            # Extract required variables
            from_addr = order_info.get('from_addr')
            max_input = order_info.get('max_input')
            min_input = order_info.get('min_input')
            order_id = order_info.get('orderid')

            # Output variables
            print("from_addr:", from_addr)
            print("max_input:", max_input)
            print("min_input:", min_input)
            print("order_id:", order_id)

            # Save variables to a file
            output_data = {
                'order_id': order_id
            }

            with open('order.json', 'w') as output_file:
                json.dump(output_data, output_file)

            print("Variables saved to order.json.")
            print("Sending ETH... ")
            command = f"PATH_TO_CAST.EXE send --private-key {purchaser_private_key} {from_addr} --value 0.5ether --rpc-url {eth_rpc_url}"
            subprocess.run(command, shell=True)

            # Monitor order status every 10 seconds
            while True:
                order_info = get_exchange_order_info(order_id)
                if order_info:
                    status = order_info.get('state')
                    print(f"Current order status: {status}")
                    send_telegram_message(bot_token, chat_id, status)
                    if status in ['COMPLETE', 'CANCELLED', 'REFUNDED']:
                        print("Completed: ", status)
                        break
                time.sleep(10)