from django.contrib import admin
from .models import User, Image, ChatGroup, GroupMembership, UserAdmin, GroupAdmin, Message

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Image)
admin.site.register(ChatGroup, GroupAdmin)
admin.site.register(GroupMembership)
admin.site.register(Message)

