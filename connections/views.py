from django.shortcuts import render
from django.db import models

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Interest, ChatMessage
from .forms import InterestForm, ChatMessageForm
from django.db.models import Q

User = get_user_model()

@login_required
def user_list(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'connections/user_list.html', {'users': users})

@login_required
def send_interest(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)
    if request.method == 'POST':
        form = InterestForm(request.POST)
        if form.is_valid():
            interest = form.save(commit=False)
            interest.sender = request.user
            interest.recipient = recipient
            interest.save()
            return redirect('user_list')
    else:
        form = InterestForm()
    return render(request, 'connections/send_interest.html', {'form': form, 'recipient': recipient})

@login_required
def interest_list(request):
    received_interests = Interest.objects.filter(recipient=request.user, accepted=None)
    return render(request, 'connections/interest_list.html', {'interests': received_interests})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Interest

@login_required
def accept_reject_interest(request, interest_id):
    interest = get_object_or_404(Interest, id=interest_id, recipient=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            interest.accepted = True
            interest.save()
            return redirect('chat', user_id=interest.sender.id)
        elif action == 'reject':
            interest.accepted = False
            interest.save()
        return redirect('interest_list')
    return render(request, 'connections/accept_reject_interest.html', {'interest': interest})

@login_required
def chat_list(request):
    accepted_interests = Interest.objects.filter(models.Q(sender=request.user) | models.Q(recipient=request.user), accepted=True)
    return render(request, 'connections/chat_list.html', {'interests': accepted_interests})
@login_required
def chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    # Check if there's an accepted interest between the users
    interest = Interest.objects.filter(
        (Q(sender=request.user, recipient=other_user) | Q(sender=other_user, recipient=request.user)),
        accepted=True
    ).first()
    
    if not interest:
        return redirect('user_list')  # Or to an appropriate error page
    
    messages = ChatMessage.objects.filter(
        (Q(sender=request.user, recipient=other_user) | 
         Q(sender=other_user, recipient=request.user))
    ).order_by('timestamp')
    
    return render(request, 'connections/chat.html', {
        'other_user': other_user,
        'messages': messages,
        'room_name': f"{min(request.user.id, other_user.id)}_{max(request.user.id, other_user.id)}"
    })


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

@csrf_exempt
@login_required
def save_message(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        recipient_id = request.POST.get('recipient_id')
        
        recipient = get_object_or_404(User, id=recipient_id)
        
        message = ChatMessage.objects.create(
            sender=request.user,
            recipient=recipient,
            content=content
        )
        
        return JsonResponse({
            'status': 'success',
            'message_id': message.id,
            'sender': request.user.username,
            'content': message.content,
            'timestamp': message.timestamp.strftime("%B %d, %Y %H:%M")
        })
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def load_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    messages = ChatMessage.objects.filter(
        (Q(sender=request.user, recipient=other_user) | 
         Q(sender=other_user, recipient=request.user))
    ).order_by('timestamp')
    
    return render(request, 'chat_messages.html', {'messages': messages})