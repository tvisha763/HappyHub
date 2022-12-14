# Generated by Django 4.0.6 on 2023-01-02 02:08

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChatGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=50, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('description', models.CharField(default='', max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=30, unique=True)),
                ('email', models.CharField(max_length=60, unique=True)),
                ('fname', models.CharField(max_length=30)),
                ('lname', models.CharField(max_length=30)),
                ('contact', models.CharField(max_length=60)),
                ('phone', models.CharField(default='', max_length=10)),
                ('password', models.CharField(max_length=1000)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('salt', models.CharField(max_length=1023)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='APP.chatgroup')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='APP.user')),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(upload_to='media')),
                ('date', models.DateField(auto_now_add=True)),
                ('mood', models.CharField(default='', max_length=30)),
                ('moodnum', models.IntegerField(default=0)),
                ('journal', models.CharField(blank=True, max_length=10000)),
                ('diet', models.CharField(blank=True, max_length=10000)),
                ('exercise', models.CharField(blank=True, max_length=10000)),
                ('sleep', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userMood', to='APP.user')),
            ],
        ),
        migrations.CreateModel(
            name='GroupMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_joined', models.DateField(default=django.utils.timezone.now)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='APP.chatgroup')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='APP.user')),
            ],
        ),
        migrations.AddField(
            model_name='chatgroup',
            name='members',
            field=models.ManyToManyField(through='APP.GroupMembership', to='APP.user'),
        ),
    ]
