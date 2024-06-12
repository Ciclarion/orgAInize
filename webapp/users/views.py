from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import User, Conversation, Message
from .forms import LoginForm
import requests
import json


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    error_message = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.user_type == 'pro':
                    return redirect('pro_dashboard')
                elif user.user_type == 'apprenant':
                    return redirect('chatbot')
            else:
                error_message = "Nom d'utilisateur ou mot de passe incorrect."
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form, 'error_message': error_message})
    
    
from django.contrib.auth.decorators import login_required


def index_view(request):
    return render(request, 'index.html')
    

@login_required
def pro_dashboard(request):
    if request.user.user_type != 'pro':
        return redirect('chatbot')
    return render(request, 'pro_dashboard.html')


# views.py

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message
import json
import re

@login_required
def chat(request):
    conversations = Conversation.objects.filter(user=request.user)
    selected_conversation = conversations.first() if conversations.exists() else None
    return render(request, 'chatbot.html', {'conversations': conversations, 'selected_conversation': selected_conversation})



@login_required
def chat_api(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        message_text = data.get('message')
        
        if message_text:
            # Enregistrer le message utilisateur dans la base de données
            Message.objects.create(conversation=conversation, sender='User', text=message_text)
            
            # Envoyer le message au serveur LangChain
            messages = list(conversation.messages.all())
            print(messages)

            print(messages)
            payload = {
                'question': message_text,
                'conversation_id': conversation_id,
                'user_id': request.user.id,
                'chat_history': [
                    {'sender': msg.sender, 'text': msg.text} 
                    for msg in messages[:-1]
                ],
                'access': 'interne' if request.user.user_type == 'pro' else 'externe'
            }
            
            try:
                response = requests.post('http://127.0.0.1:8005/chat', json=payload)
                response_data = response.json()
                
                if response.status_code == 200:
                    bot_response = response_data['result']
                    print(bot_response)
                    prefixes = ["\n","Answer:", "A:"]
                    for prefix in prefixes:
                        if bot_response.startswith(prefix):
                            bot_response = bot_response[len(prefix):].strip()
                    Message.objects.create(conversation=conversation, sender='orgAInize', text=bot_response)
                    return JsonResponse({'response': bot_response})
                else:
                    print("Error Failed to get response from the bot:", response_data)
                    return JsonResponse({'error': 'Failed to get response from the bot'}, status=500)
            except requests.exceptions.RequestException as e:
                print("Error Failed to get response from the bot:", response_data)
                return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def new_conversation(request):
    if request.method == 'POST':
        conversation = Conversation.objects.create(user=request.user)
        return JsonResponse({'conversation_id': conversation.id})
    return JsonResponse({'error': 'Invalid request'}, status=400)
    
@login_required
def get_conversation(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    messages = conversation.messages.all().values('sender', 'text', 'timestamp')
    return JsonResponse({'messages': list(messages)})

    

