# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import permalink, signals
from django.contrib.auth.models import User
from datetime import datetime

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
    ('noun',u'명사'),
    ('verb',u'동사'),
    ('adjective',u'형용사'),
    ('adverb',u'부사'),
    ('pronoun',u'대명사'),
    ('interjection',u'감탄사'),
    ('determiner',u'관형사'),
    ('special:forbidden',u'특수:금지어'),
    ('special:derived',u'특수:파생형'),
]

class Word(models.Model):
    ## word data
    word = models.CharField(verbose_name=u'단어', max_length=100)
    pos = models.CharField(verbose_name=u'품사', max_length=100, choices=POS_CHOICES)
    props = models.CharField(verbose_name=u'속성', max_length=100, blank=True)
    stem = models.CharField(verbose_name=u'어근', max_length=100, blank=True)
    etym = models.CharField(verbose_name=u'어원', max_length=100, blank=True)
    orig = models.CharField(verbose_name=u'본딧말', max_length=100, blank=True)
    comment = models.CharField(verbose_name=u'부가 설명', max_length=1000, blank=True)
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
        name = '%d: %s (%s)' % (self.id, self.word, self.pos)
        if not self.valid:
            name += ' INVALID'
        return name
    def get_absolute_url(self):
        return '/entry/%d/' % self.id
    def save(self):
        return super(Entry, self).save()
    #@permalink
    #def get_absolute_url(self):
    #    return ('galkwi.views.entry_detail', (), {'entry_id': self.id})

PROPOSAL_ACTION_CHOCIES = [
    ('ADD', u'추가'),
    ('REMOVE', u'제거'),
    ('UPDATE', u'변경'),
]

PROPOSAL_STATUS_CHOICES = [
    ('DRAFT', u'편집 중'),
    ('VOTING', u'투표 중'),
    ('CANCELED', u'취소'),
    ('APPROVED', u'허용'),
    ('REJECTED', u'거절'),
    ('EXPIRED', u'만료'),
]

class Proposal(Word):
    # ## edit
    date = models.DateTimeField(verbose_name=u'제안 시각')
    editor = models.ForeignKey(User)
    action = models.CharField(verbose_name=u'동작', max_length=100, choices=PROPOSAL_ACTION_CHOCIES)
    rationale = models.CharField(verbose_name=u'제안 이유', max_length=1000, blank=True)
    old_entry = models.ForeignKey(Entry, related_name='+', null=True)
    # ## status
    status = models.CharField(max_length=1000, choices=PROPOSAL_STATUS_CHOICES)
    new_entry = models.ForeignKey(Entry, related_name='proposal', null=True)
    status_date = models.DateTimeField()
    class Meta:
    #    ordering = ['-date', 'status', 'action']
        permissions = [
            ("can_propose", "Can propose an action"),
        ]
    def __str__(self):
        return '%d: %s by %s' % (self.id, self.action, self.editor.username)
    def get_absolute_url(self):
        return '/proposal/%d/' % self.id
    #@permalink
    #def get_absolute_url(self):
    #    return ('galkwi.views.proposal_detail', (), {'proposal_id': self.id})
    def save(self):
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
    ('YES', u'예'),
    ('NO', u'아니요'),
]

class Vote(models.Model):
    date = models.DateTimeField()
    reviewer = models.ForeignKey(User)
    proposal = models.ForeignKey(Proposal)
    vote = models.CharField(verbose_name=u'찬반', max_length=1000, choices=VOTE_CHOICES)
    reason = models.CharField(verbose_name=u'이유', max_length=1000, blank=True)
    def __str__(self):
        return '%s on %s by %s' % (self.vote,
                                   self.proposal.id, self.reviewer.username)
    class Meta:
        ordering = ['-date']
        permissions = [
            ("can_vote", "Can vote on proposal"),
        ]
    def get_absolute_url(self):
        return '/vote/%d/' % self.id
    #@permalink
    #def get_absolute_url(self):
    #    return ('galkwi.views.vote_detail', (), {'vote_id': self.id()})

