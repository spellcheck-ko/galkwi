from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from galkwiapp.models import Entry
from xml.sax.saxutils import escape as xml_escape


class Command(BaseCommand):
    help = 'Export XML word data'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)

    def handle(self, *args, **options):
        filename = options['filename']
        self.do_export(open(filename, 'w'))

    def do_export(self, file):
        entries = Entry.objects.filter(latest__deleted=False)
        entries = entries.order_by('latest__word__word')
        file.write('<galkwi-exported version="2.0">\n')
        for entry in entries:
            rev = entry.latest
            word = rev.word
            file.write('<Entry>\n')
            file.write(' <word>%s</word>\n' % xml_escape(word.word))
            file.write(' <pos>%s</pos>\n' % xml_escape(word.pos))
            if word.props:
                file.write(' <props>%s</props>\n' % xml_escape(word.props))
            if word.stem:
                file.write(' <stem>%s</stem>\n' % xml_escape(word.stem))
            if word.etym:
                file.write(' <etym>%s</etym>\n' % xml_escape(word.etym))
            if word.description:
                file.write(' <description>%s</description>\n' % xml_escape(word.description))
            file.write(' <revisions>\n')
            while rev:
                file.write('  <revision>\n')
                file.write('   <name>%s</name>\n' % xml_escape(rev.user.username))
                timestamp = rev.timestamp.astimezone(timezone.utc)
                file.write('   <datetime>%s</datetime>\n' % timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
                if rev.comment:
                    file.write('  <comment>%s</comment>\n' % xml_escape(rev.comment))
                file.write('  </revision>\n')
                rev = rev.parent
            file.write(' </revisions>\n')
            file.write('</Entry>\n')
        file.write('</galkwi-exported>\n')
