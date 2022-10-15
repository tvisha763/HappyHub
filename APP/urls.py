from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('logout', views.logout, name="logout"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('home', views.home, name='home'),
    path('moodChecker', views.moodChecker, name='moodChecker'),
    path('takePhoto', views.takePhoto, name='takePhoto'),
    path('help', views.help, name='help'),
    path('group', views.group, name='group'),
    path('joinGroup', views.joinGroup, name='joinGroup'),
    path('leaveGroup', views.leaveGroup, name='leaveGroup'),
    path('groupChat/<int:group_id>/', views.groupChat, name="groupChat"),
]