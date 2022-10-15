
from django.db import models
from django.forms import CharField
from django.utils import timezone
from django.contrib import admin


class User(models.Model):
    username = models.CharField(max_length=30, unique=True)
    email = models.CharField(max_length=60, unique=True)
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30)
    contact = models.CharField(max_length=60)
    phone = models.CharField(max_length=10, default='')
    password = models.CharField(max_length=1000)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    salt = models.CharField(max_length=1023)
    def __str__(self):
        return '%s - %s' % (self.username, self.fname + ' ' + self.lname)

class Image(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="userMood")
    img=models.ImageField(upload_to="media")
    date=models.DateField(auto_now_add=True)
    mood=models.CharField(max_length=30, default='')
    moodnum = models.IntegerField(default=0)
    journal = models.CharField(max_length=10000, blank=True)
    diet = models.CharField(max_length=10000, blank=True)
    exercise = models.CharField(max_length=10000, blank=True)
    sleep = models.IntegerField(default=0)
    def __str__(self):
        return '%s - %s' % (self.user, self.mood)

        
class ChatGroup(models.Model):
    name = models.CharField(max_length=50, default='', unique = True)
    created_at = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=300, default='')
    members = models.ManyToManyField(User, through='GroupMembership')
    def __str__(self):
        return '%s - %s' % (self.name, self.created_at)

class GroupMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    date_joined = models.DateField(default=timezone.now)
    def __str__(self):
        return '%s - %s' % (self.user, self.group)
        
class MembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 1

class UserAdmin(admin.ModelAdmin):
    inlines = (MembershipInline,)

class GroupAdmin(admin.ModelAdmin):
    inlines = (MembershipInline,)

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s - %s' % (self.user.username, self.group.name)