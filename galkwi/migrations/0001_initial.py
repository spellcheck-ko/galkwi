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
                ('word', models.CharField(verbose_name=u'단어', max_length=100)),
                ('pos', models.CharField(verbose_name=u'품사', max_length=100, choices=[('noun', u'명사'), ('verb', u'동사'), ('adjective', u'형용사'), ('adverb', u'부사'), ('pronoun', u'대명사'), ('interjection', u'감탄사'), ('determiner', u'관형사'), ('special:forbidden', u'특수:금지어'), ('special:derived', u'특수:파생형')])),
                ('props', models.CharField(verbose_name=u'속성', max_length=100, blank=True)),
                ('stem', models.CharField(verbose_name=u'어근', max_length=100, blank=True)),
                ('etym', models.CharField(verbose_name=u'어원', max_length=100, blank=True)),
                ('orig', models.CharField(verbose_name=u'본딧말', max_length=100, blank=True)),
                ('comment', models.CharField(verbose_name=u'부가 설명', max_length=1000, blank=True)),
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
                ('word', models.CharField(verbose_name=u'단어', max_length=100)),
                ('pos', models.CharField(verbose_name=u'품사', max_length=100, choices=[('noun', u'명사'), ('verb', u'동사'), ('adjective', u'형용사'), ('adverb', u'부사'), ('pronoun', u'대명사'), ('interjection', u'감탄사'), ('determiner', u'관형사'), ('special:forbidden', u'특수:금지어'), ('special:derived', u'특수:파생형')])),
                ('props', models.CharField(verbose_name=u'속성', max_length=100, blank=True)),
                ('stem', models.CharField(verbose_name=u'어근', max_length=100, blank=True)),
                ('etym', models.CharField(verbose_name=u'어원', max_length=100, blank=True)),
                ('orig', models.CharField(verbose_name=u'본딧말', max_length=100, blank=True)),
                ('comment', models.CharField(verbose_name=u'부가 설명', max_length=1000, blank=True)),
                ('date', models.DateTimeField(verbose_name=u'제안 시각')),
                ('action', models.CharField(verbose_name=u'동작', max_length=100, choices=[('ADD', u'추가'), ('REMOVE', u'제거'), ('UPDATE', u'변경')])),
                ('rationale', models.CharField(verbose_name=u'제안 이유', max_length=1000, blank=True)),
                ('status', models.CharField(max_length=1000, choices=[('DRAFT', u'편집 중'), ('VOTING', u'투표 중'), ('CANCELED', u'취소'), ('APPROVED', u'허용'), ('REJECTED', u'거절'), ('EXPIRED', u'만료')])),
                ('status_date', models.DateTimeField()),
                ('editor', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('new_entry', models.ForeignKey(to='galkwi.Entry', related_name='proposal', null=True)),
                ('old_entry', models.ForeignKey(to='galkwi.Entry', related_name='+', null=True)),
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
                ('vote', models.CharField(verbose_name=u'찬반', max_length=1000, choices=[('YES', u'예'), ('NO', u'아니요')])),
                ('reason', models.CharField(verbose_name=u'이유', max_length=1000, blank=True)),
                ('proposal', models.ForeignKey(to='galkwi.Proposal')),
                ('reviewer', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('can_vote', 'Can vote on proposal')],
                'ordering': ['-date'],
            },
        ),
    ]
