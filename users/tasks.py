import json
from websocket import WebSocketApp
from celery import shared_task
from django.conf import settings
from django.core.management.base import BaseCommand
from users.models import Trigger, BTCPrice
from django.core.mail import send_mail
from django.utils import timezone


@shared_task
def send_email_notification(user_email, subject, message):
    send_mail(
        subject,
        message,
        'subhchaturvedi55@gmail.com',  # From email address
        [user_email],  # To email address
        fail_silently=False,
    )

@shared_task
def start_websocket():
    def on_message(ws, message):
        data = json.loads(message)
        price = float(data['k']['c'])
        print(f"Current BTC price: {price}")

        # Store the current price in the database
        BTCPrice.objects.create(price=price, timestamp=timezone.now())

        # Fetch the last stored price
        last_price_entry = BTCPrice.objects.last()
        last_price = last_price_entry.price if last_price_entry else None


        #Function to check if the change in price needs to alert any set triggers
        def checkIfTrigger(curr,new,old):
            Diff = [old,new]
            Diff.sort()

            if curr>=Diff[0] and curr<=Diff[1]:
                return True
            else:
                return False
            

        if last_price is not None:

            triggers = Trigger.objects.all()
            for trigger in triggers:
                if (trigger.status != 'triggered') and ((checkIfTrigger(trigger.value,price,last_price) and trigger.status == 'created')):
                    print(f"Alert! {trigger.user.username} - BTC price has reached the trigger value of {trigger.value}.")

                    alert_message = f"Alert! {trigger.user.username} - BTC price has reached the trigger value of {trigger.value}."


                    # Send email notification to the user
                    send_email_notification.delay(trigger.user.email, 'BTC Price Alert', alert_message)


                    trigger.status = 'triggered'
                    trigger.save()

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
