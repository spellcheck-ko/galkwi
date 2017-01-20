from django.core.management.base import BaseCommand, CommandError
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
        entries = Entry.objects.filter(valid=True)
        entries = entries.order_by('word')
        file.write('<exported-data>\n')
        for entry in entries:
            if not entry.valid:
                continue
            file.write('<Entry>\n')
            file.write('<word>%s</word>\n' % entry.word)
            file.write('<pos>%s</pos>\n' % entry.pos)
            if entry.props:
                file.write('<props>%s</props>\n' % xml_escape(entry.props))
            if entry.stem:
                file.write('<stem>%s</stem>\n' % entry.stem)
            if entry.etym:
                file.write('<etym>%s</etym>\n' % entry.etym)
            if entry.comment:
                file.write('<comment>%s</comment>\n' % xml_escape(entry.comment))
            file.write('<editors>')
            for editor in entry.editors.all():
                file.write('<name>%s</name>' % editor.username)
            file.write('</editors>\n')
            file.write('<editor>%s</editor>\n' % entry.editor.username)
            file.write('<date>%s</date>\n' % entry.date.strftime('%Y-%m-%d %H:%M:%S'))
            file.write('</Entry>\n')
        file.write('</exported-data>\n')
