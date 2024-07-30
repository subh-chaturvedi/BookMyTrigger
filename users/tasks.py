import json
from websocket import WebSocketApp
from celery import shared_task
from django.conf import settings
from django.core.management.base import BaseCommand
from users.models import Trigger, BTCPrice
from django.core.mail import send_mail
from django.utils import timezone


# @shared_task
# def send_email_notification(user_email, subject, message):
#     print("mail sending!!!!")
#     send_mail(
#         subject,
#         message,
#         'subhchaturvedi55@gmail.com',  # From email address
#         [user_email],  # To email address
#         fail_silently=False,
    # )

from django.db.models import Q

def send_trigger_email(trigger, current_price):
    subject = 'BTC Trigger Alert'
    message = f'The trigger value of {trigger.value} has been reached. Current BTC price is {current_price}.'
    recipient_list = [trigger.user.email]
    send_mail(subject, message, 'from@example.com', recipient_list)
    print(f'Email sent to {trigger.user.email} for trigger {trigger.id}')


@shared_task
def start_websocket():
    def on_message(ws, message):
        data = json.loads(message)
        # print("DATA SAMPLE",data)
        price = float(data['k']['c'])
        print(f"Current BTC price: {price}")

        # Store the current price in the database
        BTCPrice.objects.create(price=price, timestamp=timezone.now())

        # Define conditions for triggers that need to be updated
        greater_condition = Q(comparison='greater', value__lte=price, status='created')
        lower_condition = Q(comparison='lower', value__gte=price, status='created')

        # Find triggers that need to be triggered
        triggers_to_trigger = Trigger.objects.filter(greater_condition | lower_condition)

        for trigger in triggers_to_trigger:
            send_trigger_email(trigger, price)
        
        # Update the status of the triggered triggers in bulk
        Trigger.objects.filter(id__in=triggers_to_trigger.values_list('id', flat=True)).update(status='triggered')


    def on_error(ws, error):
        print(f"Error: {error}")

    def on_close(ws, close_status_code, close_msg):
        print("### closed ###")

    def on_open(ws):
        print("WebSocket opened.")
        ws.send(json.dumps({
            "method": "SUBSCRIBE",
            "params": [
                "btcusdt@kline_1m"
            ],
            "id": 1
        }))

    ws = WebSocketApp("wss://stream.binance.com:9443/ws/btcusdt@kline_1m",
                      on_open=on_open,
                      on_message=on_message,
                      on_error=on_error,
                      on_close=on_close)

    ws.run_forever()
