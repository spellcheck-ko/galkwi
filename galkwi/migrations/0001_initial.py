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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('word', models.CharField(verbose_name='단어', max_length=100)),
                ('pos', models.CharField(verbose_name='품사', max_length=100, choices=[('명사', '명사'), ('동사', '동사'), ('형용사', '형용사'), ('부사', '부사'), ('대명사', '대명사'), ('감탄사', '감탄사'), ('관형사', '관형사'), ('특수:금지어', '특수:금지어'), ('특수:파생형', '특수:파생형')])),
                ('props', models.CharField(verbose_name='속성', max_length=100)),
                ('stem', models.CharField(verbose_name='어근', max_length=100)),
                ('etym', models.CharField(verbose_name='어원', max_length=100)),
                ('orig', models.CharField(verbose_name='본딧말', max_length=100)),
                ('comment', models.CharField(verbose_name='부가 설명', max_length=1000)),
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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('word', models.CharField(verbose_name='단어', max_length=100)),
                ('pos', models.CharField(verbose_name='품사', max_length=100, choices=[('명사', '명사'), ('동사', '동사'), ('형용사', '형용사'), ('부사', '부사'), ('대명사', '대명사'), ('감탄사', '감탄사'), ('관형사', '관형사'), ('특수:금지어', '특수:금지어'), ('특수:파생형', '특수:파생형')])),
                ('props', models.CharField(verbose_name='속성', max_length=100)),
                ('stem', models.CharField(verbose_name='어근', max_length=100)),
                ('etym', models.CharField(verbose_name='어원', max_length=100)),
                ('orig', models.CharField(verbose_name='본딧말', max_length=100)),
                ('comment', models.CharField(verbose_name='부가 설명', max_length=1000)),
                ('date', models.DateTimeField(verbose_name='제안 시각')),
                ('action', models.CharField(verbose_name='동작', max_length=100, choices=[('ADD', '추가'), ('REMOVE', '제거'), ('UPDATE', '변경')])),
                ('rationale', models.CharField(verbose_name='제안 이유', max_length=1000)),
                ('status', models.CharField(max_length=1000, choices=[('DRAFT', '편집 중'), ('VOTING', '투표 중'), ('CANCELED', '취소'), ('APPROVED', '허용'), ('REJECTED', '거절'), ('EXPIRED', '만료')])),
                ('status_date', models.DateTimeField()),
                ('editor', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('new_entry', models.ForeignKey(to='galkwi.Entry', related_name='proposal')),
                ('old_entry', models.ForeignKey(to='galkwi.Entry', related_name='+')),
            ],
            options={
                'permissions': [('can_propose', 'Can propose an action')],
            },
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('date', models.DateTimeField()),
                ('vote', models.CharField(verbose_name='찬반', max_length=1000, choices=[('YES', '예'), ('NO', '아니요')])),
                ('reason', models.CharField(verbose_name='이유', max_length=1000)),
                ('proposal', models.ForeignKey(to='galkwi.Proposal')),
                ('reviewer', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('can_vote', 'Can vote on proposal')],
                'ordering': ['-date'],
            },
        ),
    ]
