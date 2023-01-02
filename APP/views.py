from contextvars import Context
from operator import contains
from geopy.geocoders import Nominatim
from unicodedata import name
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Image, ChatGroup, GroupMembership, Message
import bcrypt
from keras.models import load_model
from PIL import ImageOps
import numpy as np
import requests
from datetime import date
import time
import uuid
from urllib.request import urlopen
import urllib
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from PIL import Image as pic
import os
from django.utils import timezone
from datetime import timedelta
from datetime import datetime
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
import base64
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
import json

# # # Create your views here.
# def debug(request):
#     return render(request, 'home.html')
def signup(request):
    if not request.session.get('logged_in') or not request.session.get('username'):
        if request.method == "POST":
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            username = request.POST.get('username')
            password = request.POST.get('password').encode("utf8")
            confirmPass = request.POST.get('confirmPass').encode("utf8")
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            contact = request.POST.get('contact')
            inputs = [email, username, password, confirmPass, phone, fname, lname, contact]

            # checking if confirm password matches password   
            if (password != confirmPass):
                messages.error(request, "The passwords do not match.")
                return redirect('signup')

            for inp in inputs:
                if inp == '':
                    messages.error(request, "Please input all the information.")
                    return redirect('signup')

            if password != '' and len(password) < 6:
                messages.error(request, "Your password must be at least 6 charecters.")
                return redirect('signup')

            if "@" not in email:
                messages.error(request, "Please enter your email address.")
                return redirect('signup')

            if "@" not in contact:
                messages.error(request, "Please enter your close contact's email address.")
                return redirect('signup')

            if User.objects.filter(email=email).exists():
                messages.error(request, "An account with this email already exists. If this is you, please log in.")
                return redirect('signup')
            
            if User.objects.filter(username=username).exists():
                messages.error(request, "An account with this username already exists. Please pick another one.")
                return redirect('signup')

            else:
                salt = bcrypt.gensalt()
                user = User()
                user.email = email
                user.username = username
                user.fname = fname
                user.contact = contact
                user.lname = lname
                user.phone = phone
                user.password = bcrypt.hashpw(password, salt)
                user.salt = salt
                user.save()
                user = User.objects.get(username=username)
                context = {
                    'user': user
                    }
                member = GroupMembership()
                member.user = user
                member.group = ChatGroup.objects.get(name="Happy Hub")
                member.save()
                message = render_to_string('newUserEmail.html', context)
                subject = '🎉Welcome to Happy Hub!🎉'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [user.email]
                message2 = render_to_string('closeContact.html', context)
                subject2 = '🎉'+fname+' '+lname+' has listed YOU as a close contact!'+'🎉'
                recipient_list2 = [user.contact]
                send_mail(subject, message, email_from, recipient_list)
                send_mail(subject2, message2, email_from, recipient_list2)
                return redirect('login')
        else:
            if request.session.get('logged_in'):
                return redirect('/login')
    else:
        return redirect('dashboard')

    return render(request, 'auth/signup.html')
def login(request):
    if not request.session.get('logged_in') or not request.session.get('username'):
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password').encode("utf8")
            inputs = [username, password]

            for inp in inputs:
                if inp == '':
                    messages.error(request, "Please input all the information.")
                    return redirect('login')

            

            if User.objects.filter(username=username).exists():
                saved_hashed_pass = User.objects.filter(username=username).get().password.encode("utf8")[2:-1]
                saved_salt = User.objects.filter(username=username).get().salt.encode("utf8")[2:-1]
                user  = User.objects.filter(username=username).get()
                request.session["username"] = user.username
                request.session['logged_in'] = True
            
                salted_password = bcrypt.hashpw(password, saved_salt)
                if salted_password == saved_hashed_pass:
                    return redirect('dashboard')
                else:
                    messages.error(request, "Your password is incorrect.")
                    return redirect('login')

            else:
                messages.error(request, "An account with this username does not exist. Please sign up.")
                return redirect('login')

        else:
            if request.session.get('logged_in'):
                return redirect('/login')

        return render(request, 'auth/login.html')
    else:
        return redirect('dashboard')

def logout(request):
    if not request.session.get('logged_in') or not request.session.get('username'):
        return redirect('/login')
    else:
        request.session["username"] = None
        request.session['logged_in'] = False
        return redirect('/')



def home(request):
        return render(request, 'home.html')


def moodChecker(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    else:
        
        return render(request, 'moodChecker.html')

def classifyImage(request, image, path):
    
    # Load the model
    model = load_model('APP/converted_keras/keras_model.h5', compile=False)

    # Create the array of the right shape to feed into the keras model
    # The 'length' or number of images you can put into the array is
    # determined by the first position in the shape tuple, in this case 1.
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    # Replace this with the path to your image
    image = pic.open(f"media/{path}").convert('RGB')
    #resize the image to a 224x224 with the same strategy as in TM2:
    #resizing the image to be at least 224x224 and then cropping from the center
    size = (224, 224)
    
    image = ImageOps.fit(image, size, pic.ANTIALIAS)

    #turn the image into a numpy array
    image_array = np.asarray(image)
    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
    # Load the image into the array
    data[0] = normalized_image_array

    # run the inference
    prediction = model.predict(data)
    print(str(round(max(prediction[0])*100)) + "% certainty")
    
    if prediction[0][0] == max(prediction[0]):
        return("sad")
    elif prediction[0][1] == max(prediction[0]):
        return("happy")
    elif prediction[0][2] == max(prediction[0]):
        return("anxious")

def mailCheck(request):
    unhappy = 0
    user = User.objects.get(username=request.session["username"])
    context = {
                'user': user
                }
    dangers = ["harm", "suicide", "kill", "abuse", "assault", "knife", "gun", "murder", "suicidal", "rape", "hurt", "cut", "burn", "beat", "sad", "depressed"]
    threeDays = timezone.now() - timedelta(days=3)
    week = timezone.now() - timedelta(days=7)
    data = Image.objects.filter(date__gte=threeDays, user=user)
    dataweek = Image.objects.filter(date__gte=week, user=user)
    for d in data:
        for danger in dangers:
            if danger in d.journal:
                email_from = settings.EMAIL_HOST_USER
                message = render_to_string('dangerMail.html', context)
                subject = '💀'+'We are afraid that '+user.fname+' '+user.lname+' might try to harm themself or others.'+'💀'
                recipient_list = [user.contact]
                send_mail(subject, message, email_from, recipient_list)
            
    for d in dataweek:
        if d.moodnum == 1 or d.moodnum == 2:
            unhappy+=1
    if unhappy >= 3.5:
        message = render_to_string('checkin.html', context)
        subject = '😭Check-in😭'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user.email]
        message2 = render_to_string('contactCheckIn.html', context)
        subject2 = '😭It looks like'+user.fname+' '+user.lname+' had a bad week!'+'😭'
        recipient_list2 = [user.contact]
        send_mail(subject, message, email_from, recipient_list)
        send_mail(subject2, message2, email_from, recipient_list2)


def takePhoto(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    if request.method== 'POST':      
        today = date.today()
        
        user = User.objects.get(username=request.session["username"])
        img = request.POST.get("photo").replace('data:image/png;base64,', '')
        if img == None:
            messages.error(request, "Please submit an image.")
            return render(request, 'moodChecker.html')
        elif Image.objects.filter(user=user, date=today).exists():
            image_file_like = ContentFile(base64.b64decode(img))
            a=str(uuid.uuid4())
            image = Image.objects.get(user=user, date=today)
            image.img.save(f"{a}.png", image_file_like, save=True)
            path = f"media/{a}.png"
            journal = request.POST.get('journal')
            diet = request.POST.get('diet')
            exercise = request.POST.get('exercise')
            sleep = request.POST.get('sleep')
            if classifyImage(request, image, path) == "sad":
                toUpdate = Image.objects.filter(user=user, date=today) 
                toUpdate.update(img = path, mood="sad", journal=journal, moodnum=1, diet=diet, exercise=exercise, sleep=sleep)
            elif classifyImage(request, image, path) == "anxious":
                toUpdate = Image.objects.filter(user=user, date=today) 
                toUpdate.update(img = path, mood="anxious", moodnum=2, journal=journal, diet=diet, exercise=exercise, sleep=sleep)
            elif classifyImage(request, image, path) == "happy":
                toUpdate = Image.objects.filter(user=user, date=today) 
                toUpdate.update(img = path, mood="happy", moodnum=3, journal=journal, diet=diet, exercise=exercise, sleep=sleep)
            mailCheck(request)

            return render(request, 'moodChecker.html')
        
        else:
            image_file_like = ContentFile(base64.b64decode(img))
            a=str(uuid.uuid4())
            journal = request.POST.get('journal')
            diet = request.POST.get('diet')
            exercise = request.POST.get('exercise')
            sleep = request.POST.get('sleep')
            image = Image.objects.create(user=user, journal=journal, diet=diet, exercise=exercise, sleep=sleep)
            
            image.img.save(f"{a}.png", image_file_like, save=True)
            path = f"media/{a}.png"
            if classifyImage(request, image, path) == "sad":
                image.mood = ("sad")
                image.moodnum = 1
            elif classifyImage(request, image, path) == "anxious":
                image.mood = ("anxious")
                image.moodnum = 2
            elif classifyImage(request, image, path) == "happy":
                image.mood = ("happy")
                image.moodnum = 3

            image.save()
            
            mailCheck(request)

            return render(request, 'moodChecker.html')
            





def help(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    else:
        if request.method == "POST":
            address = request.POST.get('address')
            zipcode = request.POST.get('zip')
            state = request.POST.get('state')
            country = request.POST.get('country')
            radiusM = float(request.POST.get('radius'))
            radiusNum = radiusM*1609.344
            radius = str(radiusNum)
            if address == '' or zipcode == '' or state == '' or country == '' or radius == '':
                 messages.error(request, "Please enter all the information.")
                 hospitals = []
                 context = {
                    'hospitals' : hospitals,
                
                 }

               

                 return (request, 'findHelp.html', context)
            else:
                geolocator = Nominatim(user_agent = "locationFinder")

                location = geolocator.geocode(address + ', ' + zipcode + ', ' + state + ', ' + country)

                
                
                url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+str(location.latitude)+"%2C"+str(location.longitude)+"&radius="+radius+"&type=hospital&keyword=mental&key=AIzaSyCoIcNeDmGAIe1rdyv6LRmChS3UyaJBDB0"

                payload={}
                headers = {}

                response = requests.request("GET", url, headers=headers, data=payload)
            

                responses = json.loads(response.text).get('results')
                
                
                class Hospital:
                    def __init__(self, name, address, rating, opening_hours):
                        self.name = name
                        self.address = address
                        self.rating = rating
                        self.opening_hours = opening_hours
                hospitals = []

                
                for r in range(len(responses)):
                    hospitals.append(Hospital(responses[r].get('name'), responses[r].get('vicinity'), responses[r].get('rating'), responses[r].get('opening_hours')))

                context = {
                    'hospitals' : hospitals,
                    
                }

                if len(hospitals) == 0:
                    messages.error(request, "Expand your radius")

                return render(request, 'findHelp.html', context)
            

        else:
            hospitals = []
            context = {
                'hospitals' : hospitals,
            
            }

            

            return render(request, 'findHelp.html', context)

        
def group(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    else:
        allGroups = ChatGroup.objects.all()
        groups = []
        allMembers = GroupMembership.objects.all()
        if request.method == "POST":
            user = User.objects.get(username=request.session["username"])
            name = request.POST.get('name')
            description = request.POST.get('description')
            membership = GroupMembership()
            group = ChatGroup()
            if ChatGroup.objects.filter(name=name).exists():
                messages.error(request, "A group with this name already exists. You can create a group with a different name, or join that group.")
                return redirect('group')
            else:
                group.name = name
                group.description = description
                group.save()
                membership.user = user
                membership.group = group
                membership.save()

        
            
        class Group:
            def __init__(self, name, description, members, number):
                self.name = name
                self.description = description
                self.members = members
                self.n = n
        
        for group in range(len(allGroups)):
            n = 0
            for g in GroupMembership.objects.filter(group = allGroups[group]):
                n = n+1
            groups.append(Group(allGroups[group].name, allGroups[group].description, GroupMembership.objects.filter(group = allGroups[group]), n))
            
       

        context = {
            'groups': groups
        }
        return render(request, 'group.html', context)

def joinGroup(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    else:
        if request.method == "POST":
            user = User.objects.get(username=request.session["username"])
            membership = GroupMembership()
            group = request.POST.get('group')
            find = ChatGroup.objects.get(name = group)
            membership.user = user
            membership.group = find
            membership.save()
            messages.error(request, "You have joined " + group)
            context = {
                'user': user,
                'group' : group
                }
            message = render_to_string('joinGroup.html', context)
            subject = '🎉Welcome to '+ group +'!🎉'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            send_mail(subject, message, email_from, recipient_list)
        return redirect('group')

def dashboard(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    else:
        user = User.objects.get(username=request.session["username"])
        week = timezone.now() - timedelta(days=7)
        data = Image.objects.filter(date__gte=week, user=user)
        fullData = Image.objects.filter(user=user)
        length = len(Image.objects.filter(user=user))
        #allGroups = ChatGroup.members.filter(user = user)
        groups = []
        allMembers = GroupMembership.objects.filter(user = user)
        dates = []
        for d in data:
            dates.append(str(d.date))

        allDates = []
        for d in fullData:
            allDates.append(str(d.date))

        happyWeek = 0
        sadWeek = 0
        anxWeek = 0
        happyFull = 0
        sadFull = 0
        anxFull = 0

        for d in data:
            if d.moodnum == 1:
                sadWeek += 1
            elif d.moodnum == 2:
                anxWeek +=1
            else:
                happyWeek +=1
        
        for d in fullData:
            if d.moodnum == 1:
                sadFull += 1
            elif d.moodnum == 2:
                anxFull +=1
            else:
                happyFull +=1
        class Group:
            def __init__(self, name, description, members, number, id):
                self.name = name
                self.description = description
                self.members = members
                self.n = n
                self.id = id
        
        for group in range(len(allMembers)):
            n = 0
            id = GroupMembership.objects.get(id=allMembers[group].id).group.id
            for g in GroupMembership.objects.filter(group = allMembers[group].group):
                n = n+1
            groups.append(Group(allMembers[group].group.name, allMembers[group].group.description, GroupMembership.objects.filter(group = allMembers[group].group), n, id))
            print()
            
        
        
        Context = {
            'uname': user.username,
            'data':data,
            'dates':dates,
            'fullData':fullData,
            'fullDataRev':fullData.reverse(),
            'allDates':allDates,
            'happyWeek' : happyWeek,
            'sadWeek' : sadWeek,
            'anxWeek' : anxWeek,
            'happyFull' : happyFull,
            'sadFull' : sadFull,
            'anxFull' : anxFull,
            'length' : length,
            'groups' : groups
        }
        return render(request, 'dashboard.html', Context)


def leaveGroup(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    else:
        if request.method == "POST":
            user = User.objects.get(username=request.session["username"])
            name = request.POST.get("group")
            group = ChatGroup.objects.get(name=name)
            GroupMembership.objects.filter(user=user, group=group).delete()
            messages.error(request, "You have left " + name)
            return redirect('dashboard')

def groupChat(request, group_id):
    if not request.session.get('logged_in'):
        return redirect('/login')
    else:
        username = request.session.get("username")
        user = User.objects.get(username=request.session["username"])
        group = ChatGroup.objects.get(id=group_id)
        if request.method == "POST":
            message = request.POST.get("message")
            text = Message()
            text.group = group
            text.user = user
            text.message = message
            text.save()
        class Id():
            def __init__(self, id):
                self.id = id
        
        id = Id(group_id)
        n=0
        for g in GroupMembership.objects.filter(group = group):
                n = n+1

        context = {
            "chat" : Message.objects.filter(group=group),
            "id" : id,
            "group" : group,
            "number" : n,
            "members" : GroupMembership.objects.filter(group = group)
        }
        return render(request, 'groupChat.html', context)

def emergency(request):
    return render(request, 'emergency.html')

# def newUserMail(request, uname):
#     user = User.objects.get(username=uname)
#     context = {
#         'user': user
#         }
#     message = render_to_string('newUserEmail.html', context)
#     subject = '🎉Welcome to Happy Hub!🎉'
#     email_from = settings.EMAIL_HOST_USER
#     recipient_list = [user.email]
#     send_mail(subject, message, email_from, recipient_list)