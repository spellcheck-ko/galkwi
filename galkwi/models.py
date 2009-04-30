# -*- coding: utf-8 -*-
from django.db.models import permalink, signals
from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from django.contrib.auth.models import User
from datetime import datetime

class Person(db.Model):
    user = db.UserProperty()

class UserProfile(db.Model):
    pass

#    user = models.ForeignKey(User, unique=True)
#    level = models.IntegerField(default=1)
#    def title(self):
#        if (self.level == 0):
#            return u'구경꾼'
#        elif (self.level < 100):
#            return u'편집자'
#        elif (self.level < 200):
#            return u'검토자'
#        elif (self.level < 1000):
#            return u'관리자'
#        else:
#            return u'킹왕짱'
#    def is_editor(self):
#        return (self.level > 0)
#    def is_reviewer(self):
#        return (self.level >= 100)
#    def is_admin(self):
#        return (self.level >= 900)
#    def is_king(self):
#        return (self.level >= 1000)


POS_CHOICES = [
    u'명사',
    u'동사',
    u'형용사',
    u'부사',
    u'대명사',
    u'감탄사',
    u'관형사',
    u'특수:금지어',
    u'특수:파생형',
]

class Word(db.Model):
    ## word data
    word = db.StringProperty(verbose_name='단어')
    word_substrings = db.StringListProperty()
    pos = db.StringProperty(verbose_name='품사', choices=POS_CHOICES)
    props = db.StringProperty(verbose_name='속성')
    stem = db.StringProperty(verbose_name='어근')
    etym = db.StringProperty(verbose_name='어원')
    orig = db.StringProperty(verbose_name='본딧말')
    comment = db.TextProperty(verbose_name='부가 설명')
    class Meta:
        abstract = True
    def rebuild_substrings(self):
        length = len(unicode(self.word))
        substrings = []
        for a in range(0, length):
            for b in range(a + 1, length + 1):
                substrings.append(self.word[a:b])
        self.word_substrings = substrings
        

# word entry in dictionary
class Entry(Word):
    ## edit
    date = db.DateTimeProperty()
    editor = db.ReferenceProperty(User, collection_name='entry_editor_set')
    ## status
    valid = db.BooleanProperty(default=True)
    #overrides = db.SelfReferenceProperty(collection_name='entry_overrides_set'
    overrides = db.SelfReferenceProperty()
    # class Meta:
    #     ordering = ['word', 'pos', 'valid']
    def __unicode__(self):
        name = '%d: %s (%s)' % (self.key().id(), self.word, self.pos)
        if not self.valid:
            name += ' INVALID'
        return name
    def get_absolute_url(self):
        return '/entry/%d/' % self.key().id()
    #@permalink
    #def get_absolute_url(self):
    #    return ('galkwi.views.entry_detail', (), {'entry_id': self.id})

PROPOSAL_ACTION_CHOCIES = [
    'ADD',
    'REMOVE',
    'UPDATE',
#     ('ADD', '추가'),
#     ('REMOVE', '제거'),
#     ('UPDATE', '변경'),
]

PROPOSAL_STATUS_CHOICES = [
    'DRAFT',
    'VOTING',
    'CANCELED',
    'APPROVED',
    'REJECTED',
    'EXPIRED',
#     ('DRAFT', '편집 중'),
#     ('VOTING', '투표 중'),
#     ('CANCELED', '취소'),
#     ('APPROVED', '허용'),
#     ('REJECTED', '거절'),
#     ('EXPIRED', '만료'),
]

class Proposal(Word):
    # ## edit
    date = db.DateTimeProperty(verbose_name='제안 시각')
    editor = db.ReferenceProperty(User, collection_name='proposal_editor_set')
    action = db.StringProperty(verbose_name='동작',
                               choices=PROPOSAL_ACTION_CHOCIES)
    rationale = db.TextProperty(verbose_name='제안 이유')
    old_entry = db.ReferenceProperty(Entry, collection_name='proposal_old_entry_set')
    # ## status
    status = db.StringProperty(choices=PROPOSAL_STATUS_CHOICES)
    new_entry = db.ReferenceProperty(Entry, collection_name='proposal_new_entry_set')
    status_date = db.DateTimeProperty()
    class Meta:
    #    ordering = ['-date', 'status', 'action']
        permissions = [
            ("can_propose", "Can propose an action"),
        ]
    def __unicode__(self):
        return '%d: %s by %s' % (self.key().id(), self.action, self.editor.username)
    def get_absolute_url(self):
        return '/proposal/%d/' % self.key().id()
    #@permalink
    #def get_absolute_url(self):
    #    return ('galkwi.views.proposal_detail', (), {'proposal_id': self.id})
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
            entry.editor = self.editor
            entry.rebuild_substrings()
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
            entry.overrides = self.old_entry
            entry.rebuild_substrings()
            entry.save()
            self.new_entry = entry
            entry = self.old_entry
            entry.valid = False
            entry.save()
            self.status = 'APPROVED'
            self.status_date = datetime.now()
            self.save()

VOTE_CHOICES = [
    'YES',
    'NO',
]

class Vote(db.Model):
    date = db.DateTimeProperty()
    reviewer = db.ReferenceProperty(User)
    proposal = db.ReferenceProperty(Proposal)
    vote = db.StringProperty(verbose_name='찬반', choices=VOTE_CHOICES,
                             required=True)
    reason = db.TextProperty(verbose_name='이유')
    def __unicode__(self):
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

