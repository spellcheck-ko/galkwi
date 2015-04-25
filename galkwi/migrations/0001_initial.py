# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('word', models.CharField(max_length=100, verbose_name='단어')),
                ('pos', models.CharField(choices=[('명사', '명사'), ('동사', '동사'), ('형용사', '형용사'), ('부사', '부사'), ('대명사', '대명사'), ('감탄사', '감탄사'), ('관형사', '관형사'), ('특수:금지어', '특수:금지어'), ('특수:파생형', '특수:파생형')], max_length=100, verbose_name='품사')),
                ('props', models.CharField(max_length=100, verbose_name='속성', blank=True)),
                ('stem', models.CharField(max_length=100, verbose_name='어근', blank=True)),
                ('etym', models.CharField(max_length=100, verbose_name='어원', blank=True)),
                ('orig', models.CharField(max_length=100, verbose_name='본딧말', blank=True)),
                ('comment', models.CharField(max_length=1000, verbose_name='부가 설명', blank=True)),
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
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('word', models.CharField(max_length=100, verbose_name='단어')),
                ('pos', models.CharField(choices=[('명사', '명사'), ('동사', '동사'), ('형용사', '형용사'), ('부사', '부사'), ('대명사', '대명사'), ('감탄사', '감탄사'), ('관형사', '관형사'), ('특수:금지어', '특수:금지어'), ('특수:파생형', '특수:파생형')], max_length=100, verbose_name='품사')),
                ('props', models.CharField(max_length=100, verbose_name='속성', blank=True)),
                ('stem', models.CharField(max_length=100, verbose_name='어근', blank=True)),
                ('etym', models.CharField(max_length=100, verbose_name='어원', blank=True)),
                ('orig', models.CharField(max_length=100, verbose_name='본딧말', blank=True)),
                ('comment', models.CharField(max_length=1000, verbose_name='부가 설명', blank=True)),
                ('date', models.DateTimeField(verbose_name='제안 시각')),
                ('action', models.CharField(choices=[('ADD', '추가'), ('REMOVE', '제거'), ('UPDATE', '변경')], max_length=100, verbose_name='동작')),
                ('rationale', models.CharField(max_length=1000, verbose_name='제안 이유', blank=True)),
                ('status', models.CharField(choices=[('DRAFT', '편집 중'), ('VOTING', '투표 중'), ('CANCELED', '취소'), ('APPROVED', '허용'), ('REJECTED', '거절'), ('EXPIRED', '만료')], max_length=1000)),
                ('status_date', models.DateTimeField()),
                ('editor', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('new_entry', models.ForeignKey(related_name='making_proposal', to='galkwi.Entry', null=True)),
                ('old_entry', models.ForeignKey(related_name='removing_proposal', to='galkwi.Entry', null=True)),
            ],
            options={
                'permissions': [('can_propose', 'Can propose an action')],
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('tos_rev', models.DateTimeField(null=True, verbose_name='약관 동의')),
                ('join_at', models.DateTimeField(verbose_name='가입')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('date', models.DateTimeField()),
                ('vote', models.CharField(choices=[('YES', '예'), ('NO', '아니요')], max_length=1000, verbose_name='찬반')),
                ('reason', models.CharField(max_length=1000, verbose_name='이유', blank=True)),
                ('proposal', models.ForeignKey(to='galkwi.Proposal')),
                ('reviewer', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
                'permissions': [('can_vote', 'Can vote on proposal')],
            },
        ),
    ]
