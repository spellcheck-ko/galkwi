# -*- coding: utf-8 -*-

import datetime
from google.appengine.ext import db
from google.appengine.tools import bulkloader

class galkwi_entry(db.Model):
    word = db.StringProperty(verbose_name='단어')
    word_substrings = db.StringListProperty()
    pos = db.StringProperty(verbose_name='품사')
    props = db.StringProperty(verbose_name='속성')
    stem = db.StringProperty(verbose_name='어근')
    etym = db.StringProperty(verbose_name='어원')
    orig = db.StringProperty(verbose_name='본딧말')
    comment = db.TextProperty(verbose_name='부가 설명')
    def rebuild_substrings(self):
        length = len(unicode(self.word))
        substrings = []
        for a in range(0, length):
            for b in range(a + 1, length + 1):
                substrings.append(self.word[a:b])
        self.word_substrings = substrings
    ## edit
    date = db.DateTimeProperty()
    #editor = db.ReferenceProperty(User, collection_name='entry_editor_set')
    ## status
    valid = db.BooleanProperty(default=True)
    overrides = db.SelfReferenceProperty()
  

class EntryLoader(bulkloader.Loader):
  def __init__(self):
    bulkloader.Loader.__init__(self, 'galkwi_entry',
                               [('word', lambda x: unicode(x, 'utf-8')),
                                ('pos', lambda x: unicode(x, 'utf-8')),
                                ('stem', lambda x: unicode(x, 'utf-8')),
                                ('props', lambda x: unicode(x, 'utf-8')),
                                ('etym', lambda x: unicode(x, 'utf-8')),
                                ('orig', lambda x: unicode(x, 'utf-8')),
                                ('comment', lambda x: ('%s' % unicode(x, 'utf-8'))),
                                ('date',
                                 lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')),
                                ('valid', bool),
                               ])

loaders = [EntryLoader]
