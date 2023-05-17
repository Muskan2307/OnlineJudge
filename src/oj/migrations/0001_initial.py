# Generated by Django 3.2 on 2023-03-29 13:40

from django.db import migrations, models
import django.db.models.deletion
import froala_editor.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Statement', froala_editor.fields.FroalaField()),
                ('Name', models.CharField(max_length=100)),
                ('Difficulty', models.CharField(max_length=10)),
                ('TimeLimit', models.IntegerField(help_text='in sec')),
                ('MemLimit', models.IntegerField(help_text='in kb')),
            ],
        ),
        migrations.CreateModel(
            name='TestCases',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Input', models.TextField()),
                ('Output', models.TextField()),
                ('Problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='oj.problem')),
            ],
        ),
    ]
