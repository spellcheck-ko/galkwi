# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.auth.models
from django.conf import settings
import django.core.validators
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', default=False, verbose_name='superuser status')),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', verbose_name='username', max_length=30, error_messages={'unique': 'A user with that username already exists.'}, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], unique=True)),
                ('first_name', models.CharField(verbose_name='first name', blank=True, max_length=30)),
                ('last_name', models.CharField(verbose_name='last name', blank=True, max_length=30)),
                ('email', models.EmailField(verbose_name='email address', blank=True, max_length=254)),
                ('is_staff', models.BooleanField(help_text='Designates whether the user can log into this admin site.', default=False, verbose_name='staff status')),
                ('is_active', models.BooleanField(help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', default=True, verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('tos_rev', models.DateTimeField(null=True, verbose_name='약관 동의')),
                ('join_at', models.DateTimeField(null=True, verbose_name='가입')),
                ('groups', models.ManyToManyField(help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups', blank=True, to='auth.Group', related_name='user_set', related_query_name='user')),
                ('user_permissions', models.ManyToManyField(help_text='Specific permissions for this user.', verbose_name='user permissions', blank=True, to='auth.Permission', related_name='user_set', related_query_name='user')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('word', models.CharField(verbose_name='단어', max_length=100)),
                ('pos', models.CharField(verbose_name='품사', max_length=100, choices=[('명사', '명사'), ('동사', '동사'), ('형용사', '형용사'), ('부사', '부사'), ('대명사', '대명사'), ('감탄사', '감탄사'), ('관형사', '관형사'), ('특수:금지어', '특수:금지어'), ('특수:파생형', '특수:파생형')])),
                ('props', models.CharField(verbose_name='속성', blank=True, max_length=100)),
                ('stem', models.CharField(verbose_name='어근', blank=True, max_length=100)),
                ('etym', models.CharField(verbose_name='어원', blank=True, max_length=100)),
                ('orig', models.CharField(verbose_name='본딧말', blank=True, max_length=100)),
                ('comment', models.CharField(verbose_name='부가 설명', blank=True, max_length=1000)),
                ('date', models.DateTimeField()),
                ('valid', models.BooleanField(default=True)),
                ('editor', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('overrides', models.ForeignKey(to='galkwi.Entry')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('word', models.CharField(verbose_name='단어', max_length=100)),
                ('pos', models.CharField(verbose_name='품사', max_length=100, choices=[('명사', '명사'), ('동사', '동사'), ('형용사', '형용사'), ('부사', '부사'), ('대명사', '대명사'), ('감탄사', '감탄사'), ('관형사', '관형사'), ('특수:금지어', '특수:금지어'), ('특수:파생형', '특수:파생형')])),
                ('props', models.CharField(verbose_name='속성', blank=True, max_length=100)),
                ('stem', models.CharField(verbose_name='어근', blank=True, max_length=100)),
                ('etym', models.CharField(verbose_name='어원', blank=True, max_length=100)),
                ('orig', models.CharField(verbose_name='본딧말', blank=True, max_length=100)),
                ('comment', models.CharField(verbose_name='부가 설명', blank=True, max_length=1000)),
                ('date', models.DateTimeField(verbose_name='제안 시각')),
                ('action', models.CharField(verbose_name='동작', max_length=100, choices=[('ADD', '추가'), ('REMOVE', '제거'), ('UPDATE', '변경')])),
                ('rationale', models.CharField(verbose_name='제안 이유', blank=True, max_length=1000)),
                ('status', models.CharField(max_length=1000, choices=[('DRAFT', '편집 중'), ('VOTING', '투표 중'), ('CANCELED', '취소'), ('APPROVED', '허용'), ('REJECTED', '거절'), ('EXPIRED', '만료')])),
                ('status_date', models.DateTimeField()),
                ('editor', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('new_entry', models.ForeignKey(null=True, to='galkwi.Entry', related_name='making_proposal')),
                ('old_entry', models.ForeignKey(null=True, to='galkwi.Entry', related_name='removing_proposal')),
            ],
            options={
                'permissions': [('can_propose', 'Can propose an action')],
            },
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('date', models.DateTimeField()),
                ('vote', models.CharField(verbose_name='찬반', max_length=1000, choices=[('YES', '예'), ('NO', '아니요')])),
                ('reason', models.CharField(verbose_name='이유', blank=True, max_length=1000)),
                ('proposal', models.ForeignKey(to='galkwi.Proposal')),
                ('reviewer', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('can_vote', 'Can vote on proposal')],
                'ordering': ['-date'],
            },
        ),
    ]
