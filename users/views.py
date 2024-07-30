from django.shortcuts import render, redirect, get_object_or_404


# Create your views here.

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Trigger
from .serializers import TriggerSerializer
from rest_framework import generics, filters
from django.core.cache import cache
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import TriggerForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from .models import BTCPrice
import io
import base64
from django.http import HttpResponse
from dotenv import load_dotenv
from pathlib import Path
import os

# Load .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


def home(request):
    return render(request, 'home.html')


@csrf_exempt
def test_mailing_service(request):
    if request.method == 'POST':
        # Extract custom password from the request
        custom_password = request.POST.get('password')
        correct_password = os.getenv('TESTMAIL_PASSWORD')  # Replace with your actual custom password

        if custom_password == correct_password:
            # Test sending an email
            send_mail(
                'Trigger Mail',
                'Hi Subh, your trigger for BTC/USDT $68670 was hit now.',
                settings.DEFAULT_FROM_EMAIL,
                ['subhchatu@gmail.com'],  # Replace with the recipient's email address
                fail_silently=False,
            )
            return JsonResponse({'status': 'success', 'message': 'Test email sent successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid password'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})



class TriggerListCreate(generics.ListCreateAPIView):
    serializer_class = TriggerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Trigger.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TriggerDelete(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, format=None):
        try:
            trigger = Trigger.objects.get(pk=pk, user=request.user)
            trigger.status = 'deleted'
            trigger.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Trigger.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class TriggerListView(generics.ListAPIView):
    serializer_class = TriggerSerializer

    def get_queryset(self):
        status = self.request.query_params.get('status')
        # cache_key = 'triggers_status_{}'.format(status if status else 'all')
        # cached_data = cache.get(cache_key)

        # if cached_data is not None:
        #     return cached_data

        queryset = Trigger.objects.all()
        if status:
            queryset = queryset.filter(status=status)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serialized_data = self.get_serializer(page, many=True).data
            # cache.set(cache_key, serialized_data, timeout=60*15)  # Cache timeout: 15 minutes
            return page
        
        serialized_data = self.get_serializer(queryset, many=True).data
        # cache.set(cache_key, serialized_data, timeout=60*15)
        return queryset


def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('triggers')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

from django.contrib.auth import logout as auth_logout

def logout(request):
    auth_logout(request)
    return redirect('login')



@login_required
def triggers(request):
    user_triggers = Trigger.objects.filter(user=request.user)
    return render(request, 'triggers.html', {'triggers': user_triggers})

@login_required
def create_trigger(request):
    if request.method == 'POST':
        form = TriggerForm(request.POST)
        if form.is_valid():
            trigger = form.save(commit=False)
            trigger.user = request.user
            trigger.save()
            return redirect('triggers')
    else:
        form = TriggerForm()
    return render(request, 'create_trigger.html', {'form': form})

@login_required
def delete_trigger(request, trigger_id):
    trigger = get_object_or_404(Trigger, id=trigger_id, user=request.user)
    if request.method == 'POST':
        trigger.status = 'deleted'
        trigger.save()
        return redirect('triggers')
    return render(request, 'confirm_delete.html', {'trigger': trigger})
