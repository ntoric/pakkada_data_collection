from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Family',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('family_json', models.JSONField()),
            ],
            options={
                'verbose_name': 'Family',
                'verbose_name_plural': 'Families',
                'ordering': ['-created_at'],
            },
        ),
    ]
