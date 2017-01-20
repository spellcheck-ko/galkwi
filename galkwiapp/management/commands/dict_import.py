from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime
from galkwiapp.models import Entry, User
from xml import sax


class Importer(sax.ContentHandler):
    def __init__(self):
        self.text = ''
        self.elements = []
        self.users = {}

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
        elif name == 'editors':
            self.editors = []
        self.text = ''

    def endElement(self, name):
        if name == 'Entry':
            self.entry.save()
            for e in self.editors:
                self.entry.editors.add(e)
        elif name == 'word':
            self.entry.word = self.text
        elif name == 'pos':
            self.entry.pos = self.text
        elif name == 'props':
            self.entry.props = self.text
        elif name == 'stem':
            self.entry.stem = self.text
        elif name == 'etym':
            self.entry.etym = self.text
        elif name == 'comment':
            self.entry.comment = self.text
        elif name == 'name' and self.elements[-2] == 'editors':
            user = self.find_or_add_user(self.text)
            self.editors.append(user)
        elif name == 'editor':
            user = self.find_or_add_user(self.text)
            self.entry.editor = user
        elif name == 'date':
            d = datetime.strptime(self.text, '%Y-%m-%d %H:%M:%S')
            self.entry.date = datetime(d.year, d.month, d.day, d.hour, d.month, d.second, 0, timezone.utc)
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

    def do_import(self, filename):
        sax.parse(filename, Importer())
