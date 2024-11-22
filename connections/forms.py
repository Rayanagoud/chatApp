from django import forms
from .models import Interest, ChatMessage

class InterestForm(forms.ModelForm):
    class Meta:
        model = Interest
        fields = ['message']

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['content']