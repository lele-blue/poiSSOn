# Generated by Django 5.0.7 on 2024-08-23 12:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_alter_service_origin'),
        ('oidc_provider', '0026_client_multiple_response_types'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.CharField(max_length=32)),
                ('name', models.CharField(max_length=32)),
            ],
        ),
        migrations.AddField(
            model_name='service',
            name='oidc_client',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='oidc_provider.client'),
        ),
        migrations.AddField(
            model_name='user',
            name='sso_groups',
            field=models.ManyToManyField(related_name='users', to='main.group'),
        ),
    ]
