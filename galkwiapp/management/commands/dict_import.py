from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from datetime import datetime
from galkwiapp.models import *
from xml import sax

class ImporterV1(sax.ContentHandler):
    def __init__(self):
        self.text = ''
        self.elements = []
        self.users = {}
        self.count = 0

    def find_or_add_user(self, username):
        q = User.objects.filter(username=username)
        if q.count() == 0:
            user = User()
            user.username = username
            user.email = username + '@gmail.com'
            user.save()
            return user
        else:
            return q[0]

    def startElement(self, name, attrs):
        self.elements.append(name)
        if name == 'Entry':
            self.entry = Entry()
            self.rev = Revision()
            self.word = Word()
        elif name == 'editors':
            self.editors = []
        self.text = ''

    def endElement(self, name):
        if name == 'Entry':
            self.word.save()
            self.rev.word = self.word
            self.rev.status = Revision.STATUS_APPROVED
            self.rev.save()
            self.entry.update_rev(self.rev)
            self.entry.save()

            for e in self.editors:
                if e != self.rev.user:
                    # append fake history
                    rev = Revision()
                    rev.word = self.word # use the same word?
                    rev.user = e
                    rev.timestamp = self.rev.timestamp
                    rev.parent = self.rev.parent
                    rev.status = Revision.STATUS_REPLACED
                    rev.entry = self.entry
                    rev.save()
                    self.rev.parent = rev

            self.rev.entry = self.entry
            self.rev.save()

            self.count += 1
            if (self.count % 10) == 0:
                print('count: %d' % self.count)

        elif name == 'word':
            self.word.word = self.text
        elif name == 'pos':
            self.word.pos = self.text
        elif name == 'props':
            self.word.props = self.text
        elif name == 'stem':
            self.word.stem = self.text
        elif name == 'etym':
            self.word.etym = self.text
        elif name == 'comment':
            self.word.description = self.text
        elif name == 'editor':
            user = self.find_or_add_user(self.text)
            self.rev.user = user
        elif name == 'date':
            d = datetime.strptime(self.text, '%Y-%m-%d %H:%M:%S')
            self.rev.timestamp = datetime(d.year, d.month, d.day, d.hour, d.month, d.second, 0, timezone.utc)
        elif name == 'name' and self.elements[-2] == 'editors':
            user = self.find_or_add_user(self.text)
            self.editors.append(user)
        self.elements.pop()

    def endDocument(self):
        pass

    def characters(self, text):
        self.text = self.text + text


class Command(BaseCommand):
    help = 'Import XML word data'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        filename = options['filename']
        self.do_import(filename)

    @transaction.atomic
    def do_import(self, filename):
        f = open(filename)
        l = f.readline()
        if l.startswith('<?xml'):
            l = f.readline()
        if l.startswith('<exported-data'):
            sax.parse(filename, ImporterV1())
        else:
            print('not implemented: %s' % l)
