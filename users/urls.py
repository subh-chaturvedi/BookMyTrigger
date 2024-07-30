from django.urls import path
from .views import login, triggers, create_trigger, delete_trigger, logout, test_mailing_service
from .views import home
from .views import TriggerListCreate, TriggerDelete, TriggerListView

urlpatterns = [
    path('alerts/create/', TriggerListCreate.as_view(), name='trigger-list-create'),
    path('alerts/delete/<int:pk>/', TriggerDelete.as_view(), name='trigger-delete'),
    path('alerts/', TriggerListView.as_view(), name='trigger-list'),
    path('login/', login, name='login'),
    path('triggers/', triggers, name='triggers'),
    path('triggers/create/', create_trigger, name='create_trigger'),
    path('triggers/delete/<int:trigger_id>/', delete_trigger, name='delete_trigger'),
    path('logout/', logout, name='logout'),
    path('test-mailing-service/', test_mailing_service, name='test_mailing_service'),
    path('', home, name='home'),
]
