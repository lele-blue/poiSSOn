# Generated by Django 5.1.1 on 2024-10-19 20:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_service_require_2fa_if_configured_and_more'),
        ('sessions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='originmigrationtoken',
            name='parent_session',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='sessions.session', null=True),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='SessionTreeEdge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('child', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='parent', to='sessions.session')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='children', to='sessions.session')),
            ],
        ),
    ]
