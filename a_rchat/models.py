from django.db import models
from django.contrib.auth.models import User
import shortuuid
import os
# Create your models here.
class ChatGroup(models.Model):
    group_name = models.CharField(max_length=100, unique=True, default=shortuuid.uuid)

    groupchat_name = models.CharField(max_length=128, unique=True,null=True , blank=True)
    admin = models.ForeignKey(User , related_name='group_admin', null=True, blank=True,  on_delete=models.SET_NULL)

    users_online = models.ManyToManyField(User, related_name='online_in_groups', blank =True)
    is_private = models.BooleanField(default=False)

    members = models.ManyToManyField(User, related_name="chat_groups", blank=True)

    def __str__(self):
        return self.group_name
    
class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup,related_name='chat_messages', on_delete=models.CASCADE)
    author= models.ForeignKey(User , on_delete=models.CASCADE) 
    body = models.CharField(max_length=300, null=True, blank=True)
    file = models.FileField(upload_to='files/', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def filename(self):
        if self.file:
            return os.path.basename(self.file.name)
        else:
            return None
        




    def __str__(self):
        if self.body:
            return f'{self.author.username} : {self.body}'
        elif self.file:
            return f'{self.author.username} :  {self.file}'
        
    @property
    def is_image(self):
        if self.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp')):
            return True
        else:
            return False
    
    class Meta:
        ordering = ['created']