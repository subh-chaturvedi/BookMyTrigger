from django.apps import AppConfig

class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        from users.tasks import start_websocket
        start_websocket.delay()
