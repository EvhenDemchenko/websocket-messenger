from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from asgiref.sync import async_to_sync
from a_rchat.forms import *
from .models import ChatGroup
# Create your views here.
@login_required
def chat_view(request, chatroom_name='public-chat'):
    chat_group = get_object_or_404(ChatGroup , group_name = chatroom_name)
    chat_messages = chat_group.chat_messages.all()[:30] # last 30 messages 
    form = ChatMessageCreateForm()

    other_user = None
    
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404()
        for member in chat_group.members.all():
            if member != request.user:
                other_user = member
                break

    if chat_group.groupchat_name:
        if request.user not in chat_group.members.all():
            chat_group.members.add(request.user)
    
    if request.htmx:
        form = ChatMessageCreateForm(request.POST)
        if form.is_valid():
            chat_message = form.save(commit=False)
            chat_message.author = request.user
            chat_message.group = chat_group
            chat_message.save()
            
            context = {
                'message':chat_message,
                'user ': request.user,
            }

            return render(request, 'a_rchat/partials/chat_message.html', context)

    context = {
        'chat_messages':chat_messages,
        'form':form,
        'other_user':other_user,
        'chatroom_name':chatroom_name,
        'chat_group':chat_group,
    }
    return render(request , 'a_rchat/chat.html',context)


def get_or_create_chatroom(request, username):
    if request.user.username ==  username:
        return redirect('chat:home')
    
    other_user = User.objects.get(username = username)
    my_private_chatrooms = request.user.chat_groups.filter(is_private=True)
    
    if my_private_chatrooms.exists():
        for chatroom in my_private_chatrooms:
            if other_user in chatroom.members.all():
                return redirect('chat:chat-room', chatroom.group_name)
    else:
        chatroom = ChatGroup.objects.create( is_private = True )
        chatroom.members.add(other_user, request.user)   
        return redirect('chat:chat-room', chatroom.group_name)

@login_required
def create_groupchat(request):
    form = NewGroupFrom()

    if request.method == 'POST':
        form = NewGroupFrom(request.POST)
        if form.is_valid():
            new_groupchat = form.save(commit=False)
            new_groupchat.admin = request.user
            new_groupchat.save()
            new_groupchat.members.add(request.user)
            return redirect("chat:chat-room", chatroom_name=new_groupchat.group_name )

    context = {
        'form':form
    }

    return render(request, 'a_rchat/create_groupchat.html', context)

@login_required
def chatroom_edit_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup , group_name = chatroom_name)
    if request.user != chat_group.admin:
        raise Http404()
    

    form = ChatRoomEditForm(instance=chat_group) # populating form with chat_group data
    
    if request.method == 'POST':
        form = ChatRoomEditForm(request.POST, instance=chat_group)

        if form.is_valid():
            form.save()

            remove_members = request.POST.getlist('remove_members')
            for member_id in remove_members:
                member = User.objects.get(id=member_id)
                chat_group.members.remove(member)

            return redirect("chat:chat-room", chatroom_name=chat_group.group_name )

    context = {
        'form':form,
        'chat_group':chat_group
    }

   

    return render(request, 'a_rchat/chatroom_edit.html', context)

@login_required
def chatroom_delete_view(request, chatroom_name):
    if request.method == 'POST':
        chat_group: ChatGroup = get_object_or_404(ChatGroup , group_name = chatroom_name)
        chat_group.delete()
        return redirect("chat:home")
    context = {}
    return render(request, 'a_rchat/chatroom_delete.html', context)


@login_required
def chatroom_leave_view(request, chatroom_name):
    chat_group: ChatGroup = get_object_or_404(ChatGroup , group_name = chatroom_name)
    chat_group.members.remove(request.user)
    return redirect("chat:home")



def chat_file_upload(request , chatroom_name):
    chat_group = get_object_or_404(ChatGroup , group_name = chatroom_name)

    if request.htmx and request.FILES:
        file = request.FILES['file']
        message = GroupMessage.objects.create(
            file=file,
            author=request.user,
            group=chat_group
        )

        channel_layer = get_channel_layer()
        event = {
            'type':'message_handler',
            'message_id':message.id
        }

        async_to_sync(channel_layer.group_send)(
            chatroom_name,event
        )
    return HttpResponse()

         

