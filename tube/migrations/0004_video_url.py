# Generated by Django 2.2.13 on 2020-06-12 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tube', '0003_auto_20200612_1803'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='url',
            field=models.CharField(default='', max_length=512, verbose_name='url'),
            preserve_default=False,
        ),
    ]
