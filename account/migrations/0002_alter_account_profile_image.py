# Generated by Django 3.2 on 2021-04-15 18:43

import account.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='profile_image',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to=account.models.get_profile_image_filepath),
        ),
    ]
