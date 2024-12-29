from django import forms
from .models import ChatGroup, GroupMessage


class ChatMessageCreateForm(forms.ModelForm):
    class Meta:
        model = GroupMessage
        fields = ['body']
        widgets = {
            'body' : forms.TextInput(attrs={ 'class':'p-4 text-black','placeholder':'Add message ...', 'maxlength':'300',  'max-length':'300'})
        }
        
class NewGroupFrom(forms.ModelForm):
    class Meta:
        model = ChatGroup
        fields = ['groupchat_name']
        widgets = {
            'groupchat_name' : forms.TextInput(attrs={'placeholder': 'Add group name', 'class':'p-4 text-black', 'maxlength':'100',  'autofocus':True})
        }

class ChatRoomEditForm(forms.ModelForm):
    class Meta:
        model = ChatGroup
        fields = ['groupchat_name']
        widgets = {
            'groupchat_name' : forms.TextInput(attrs={'placeholder': 'Add group name', 'class':'p-4 text-black', 'maxlength':'100',  'autofocus':True})
        }