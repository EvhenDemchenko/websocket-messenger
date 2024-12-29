from django.urls import path

from .views import *
app_name = 'chat'


urlpatterns = [
    path('', chat_view, name="home"),
    path('<username>', get_or_create_chatroom, name="start-chat"),
    path('room/<chatroom_name>', chat_view, name='chat-room'),
    path('new_groupchat/', create_groupchat, name='new-groupchat'),
    path('chat/edit/<chatroom_name>', chatroom_edit_view, name='edit-chatroom'),
    path('chat/delete/<chatroom_name>', chatroom_delete_view, name='delete-chatroom'),
    path('chat/leave/<chatroom_name>', chatroom_leave_view, name='chatroom-leave'),
    path('chat/fileupload/<chatroom_name>', chat_file_upload, name='chat-file-upload'),

]
