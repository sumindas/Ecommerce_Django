from django import forms
from user.models import ReplyMessage

class ReplyMessageForm(forms.Form):
    user_name = forms.CharField(max_length=255)
    message_text = forms.CharField(widget=forms.Textarea)

class ReplyForm(forms.ModelForm):
    class Meta:
        model = ReplyMessage
        fields = ['review','admin','message_text']
        
        
class GlobalSearchForm(forms.Form):
    search_query = forms.CharField(label='Search', max_length=100)
