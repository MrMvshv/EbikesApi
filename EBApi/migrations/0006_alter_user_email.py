# Generated by Django 5.0.6 on 2024-10-23 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("EBApi", "0005_alter_user_email"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
