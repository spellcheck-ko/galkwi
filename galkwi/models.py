# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import permalink, signals
from django.contrib.auth.models import User
from datetime import datetime

#class Person(models.Model):
#    user = User()
#
#class UserProfile(models.Model):
#    pass

#    user = models.ForeignKey(User, unique=True)
#    level = models.IntegerField(default=1)
#    def title(self):
#        if (self.level == 0):
#            return '구경꾼'
#        elif (self.level < 100):
#            return '편집자'
#        elif (self.level < 200):
#            return '검토자'
#        elif (self.level < 1000):
#            return '관리자'
#        else:
#            return '킹왕짱'
#    def is_editor(self):
#        return (self.level > 0)
#    def is_reviewer(self):
#        return (self.level >= 100)
#    def is_admin(self):
#        return (self.level >= 900)
#    def is_king(self):
#        return (self.level >= 1000)


POS_CHOICES = [
    ('명사','명사'),
    ('동사','동사'),
    ('형용사','형용사'),
    ('부사','부사'),
    ('대명사','대명사'),
    ('감탄사','감탄사'),
    ('관형사','관형사'),
    ('특수:금지어','특수:금지어'),
    ('특수:파생형','특수:파생형'),
]

class Word(models.Model):
    ## word data
    word = models.CharField(verbose_name='단어', max_length=100)
    pos = models.CharField(verbose_name='품사', max_length=100, choices=POS_CHOICES)
    props = models.CharField(verbose_name='속성', max_length=100)
    stem = models.CharField(verbose_name='어근', max_length=100)
    etym = models.CharField(verbose_name='어원', max_length=100)
    orig = models.CharField(verbose_name='본딧말', max_length=100)
    comment = models.CharField(verbose_name='부가 설명', max_length=1000)
    class Meta:
        abstract = True
        

# word entry in dictionary
class Entry(Word):
    ## edit
    date = models.DateTimeField()
    #editors = models.ListProperty(models.Key)
    editor = models.ForeignKey(User)
    ## status
    valid = models.BooleanField(default=True)
    overrides = models.ForeignKey('self')
    # class Meta:
    #     ordering = ['word', 'pos', 'valid']
    def __str__(self):
        name = '%d: %s (%s)' % (self.key().id(), self.word, self.pos)
        if not self.valid:
            name += ' INVALID'
        return name
    def get_absolute_url(self):
        return '/entry/%d/' % self.key().id()
    def save(self):
        self.rebuild_substrings()
        return super(Entry, self).save()
    #@permalink
    #def get_absolute_url(self):
    #    return ('galkwi.views.entry_detail', (), {'entry_id': self.id})

PROPOSAL_ACTION_CHOCIES = [
    ('ADD', '추가'),
    ('REMOVE', '제거'),
    ('UPDATE', '변경'),
]

PROPOSAL_STATUS_CHOICES = [
    ('DRAFT', '편집 중'),
    ('VOTING', '투표 중'),
    ('CANCELED', '취소'),
    ('APPROVED', '허용'),
    ('REJECTED', '거절'),
    ('EXPIRED', '만료'),
]

class Proposal(Word):
    # ## edit
    date = models.DateTimeField(verbose_name='제안 시각')
    editor = models.ForeignKey(User)
    action = models.CharField(verbose_name='동작', max_length=100, choices=PROPOSAL_ACTION_CHOCIES)
    rationale = models.CharField(verbose_name='제안 이유', max_length=1000)
    old_entry = models.ForeignKey(Entry, related_name='+')
    # ## status
    status = models.CharField(max_length=1000, choices=PROPOSAL_STATUS_CHOICES)
    new_entry = models.ForeignKey(Entry, related_name='proposal')
    status_date = models.DateTimeField()
    class Meta:
    #    ordering = ['-date', 'status', 'action']
        permissions = [
            ("can_propose", "Can propose an action"),
        ]
    def __str__(self):
        return '%d: %s by %s' % (self.key().id(), self.action, self.editor.username)
    def get_absolute_url(self):
        return '/proposal/%d/' % self.key().id()
    #@permalink
    #def get_absolute_url(self):
    #    return ('galkwi.views.proposal_detail', (), {'proposal_id': self.id})
    def save(self):
        self.rebuild_substrings()
        return super(Proposal, self).save()
    def cancel(self):
        self.status = 'CANCELED'
        self.status_date = datetime.now()
        self.save()
    def reject(self):
        self.status = 'REJECTED'
        self.status_date = datetime.now()
        self.save()
    def expire(self):
        self.status = 'EXPIRED'
        self.status_date = datetime.now()
        self.save()
    def apply(self):
        if self.status != 'VOTING':
            return
        # FIXME: need transaction
        if self.action == 'ADD':
            entry = Entry()
            entry.word = self.word
            entry.pos = self.pos
            entry.stem = self.stem
            entry.props = self.props
            entry.etym = self.etym
            entry.orig = self.orig
            entry.comment = self.comment
            entry.date = self.date
            entry.editors = [ self.editor.key() ]
            entry.editor = self.editor
            entry.save()
            self.new_entry = entry
            self.status = 'APPROVED'
            self.status_date = datetime.now()
            self.save()
        elif self.action == 'REMOVE':
            entry = self.old_entry
            entry.valid = False
            entry.save()
            self.status = 'APPROVED'
            self.status_date = datetime.now()
            self.save()
        elif self.action == 'UPDATE':
            entry = Entry()
            entry.word = self.word
            entry.pos = self.pos
            entry.stem = self.stem
            entry.props = self.props
            entry.etym = self.etym
            entry.orig = self.orig
            entry.comment = self.comment
            entry.date = self.date
            entry.editor = self.editor
            entry.editors = self.old_entry.editors
            if not self.editor.key() in entry.editors:
                entry.editors.append(self.editor.key())
            entry.overrides = self.old_entry
            entry.save()
            self.new_entry = entry
            entry = self.old_entry
            entry.valid = False
            entry.save()
            self.status = 'APPROVED'
            self.status_date = datetime.now()
            self.save()

VOTE_CHOICES = [
    ('YES', '예'),
    ('NO', '아니요'),
]

class Vote(models.Model):
    date = models.DateTimeField()
    reviewer = models.ForeignKey(User)
    proposal = models.ForeignKey(Proposal)
    vote = models.CharField(verbose_name='찬반', max_length=1000, choices=VOTE_CHOICES)
    reason = models.CharField(verbose_name='이유', max_length=1000)
    def __str__(self):
        return '%s on %s by %s' % (self.vote,
                                   self.proposal.key().id(), self.reviewer.username)
    class Meta:
        ordering = ['-date']
        permissions = [
            ("can_vote", "Can vote on proposal"),
        ]
    def get_absolute_url(self):
        return '/vote/%d/' % self.key().id()
    #@permalink
    #def get_absolute_url(self):
    #    return ('galkwi.views.vote_detail', (), {'vote_id': self.id()})

