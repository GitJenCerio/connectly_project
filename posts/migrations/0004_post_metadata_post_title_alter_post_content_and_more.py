# Generated by Django 5.1.7 on 2025-03-21 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_post_post_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='metadata',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='title',
            field=models.CharField(default='Untitled', max_length=255),
        ),
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='post_type',
            field=models.CharField(choices=[('blog', 'Blog'), ('announcement', 'Announcement'), ('image', 'Image'), ('video', 'Video')], max_length=20),
        ),
    ]
