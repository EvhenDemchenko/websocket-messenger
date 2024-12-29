from pydoc import text
import re
from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
import json
from django.contrib.auth.decorators import login_required
from django.db.models import Q



from django.template.loader import render_to_string
from a_rchat.models import ChatGroup, GroupMessage
from asgiref.sync import async_to_sync

class ChatroomConsumer(WebsocketConsumer):

    def connect(self):
        self.user = self.scope['user']
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name']  
        self.chatroom = get_object_or_404(ChatGroup, group_name = self.chatroom_name)

        async_to_sync(self.channel_layer.group_add)(
            self.chatroom_name, self.channel_name
        )
        

        #implements online count add user to online list
        if self.user not in self.chatroom.users_online.all():
            self.chatroom.users_online.add(self.user)
            self.update_online_count()

        self.accept()

    def disconnect(self, close_code):
        
        async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_name, self.channel_name
        )

        if self.user in self.chatroom.users_online.all():
            self.chatroom.users_online.remove(self.user)
            self.update_online_count()


    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        body = text_data_json['body']

        message = GroupMessage.objects.create(
            body = body,
            author = self.user,
            group = self.chatroom,
        )

        event={
            'type':'message_handler',
            'message_id':message.id
        }    

        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name, event
        )

    def message_handler(self,event):
        message_id = event['message_id']
        message = GroupMessage.objects.get(id = message_id)

        context = {
            'message':message,
            'user': self.user,
        }

        html = render_to_string('a_rchat/partials/chat_message.html', context = context)
        self.send(text_data = html)


    def update_online_count(self):
        online_count = self.chatroom.users_online.count()

        event ={
            'type': 'online_count_handler',
            'online_count': online_count
        }

        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name, event
        )

    def online_count_handler(self,event):
        online_count = event['online_count']

        context = {
            'online_count': online_count,
            'chat_group': self.chatroom,
        }

        html = render_to_string('a_rchat/partials/online_count.html', context)
        self.send(text_data = html)


class OnlineStatusConsumer(WebsocketConsumer):
    def connect(self):
       
        self.user = self.scope['user']
        self.group_name = 'online-status'
        self.group = get_object_or_404(ChatGroup, group_name = self.group_name)
        
        if self.user not in self.group.users_online.all():
            self.group.users_online.add(self.user)

        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )

        self.accept()
        self.online_status()

    def disconnect(self, close_code):
        if self.user in self.group.users_online.all():
            self.group.users_online.remove(self.user)

        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )
    
        self.online_status()

    def online_status(self):
        event ={
            'type':'online_status_handler',
        }
        async_to_sync(self.channel_layer.group_send)(
            self.group_name, event
        )

    def online_status_handler(self,event):
        online_users = self.group.users_online.all().exclude(id=self.user.id)
        
        public_chat_users = ChatGroup.objects.get(group_name="public-chat").users_online.exclude(id = self.user.id)
        my_chats = self.user.chat_groups.all()
        private_chat_with_users = [chat for chat in my_chats.filter(is_private=True) if chat.users_online.exclude(id=self.user.id)]
        group_chat_with_users = [chat for chat in my_chats.filter(is_private=False) if chat.users_online.exclude(
            Q(id=self.user.id)|
            Q(chat_groups__group_name="public-chat")
        )]

        if public_chat_users or private_chat_with_users or group_chat_with_users :
            online_in_chats = True
        else:
            online_in_chats = False
            

        context = {
            'online_users':online_users,
            'online_in_chats':online_in_chats
        }

        html = render_to_string('a_rchat/partials/online_status.html', context)
        self.send(text_data=html)