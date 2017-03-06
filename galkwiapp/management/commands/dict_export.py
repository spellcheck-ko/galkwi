from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from galkwiapp.models import Entry
import json


def json_str(s):
    return ('%s' % json.dumps(s, ensure_ascii=False))

class Command(BaseCommand):
    help = 'Export JSON word data'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)
        parser.add_argument('--license', nargs=1)

    def handle(self, *args, **options):
        filename = options['filename']
        self.do_export(open(filename, 'w'), **options)

    def do_export(self, file, **options):
        contributors_set = set()
        try:
            license = options['license'][0]
        except KeyError:
            license = None

        def write_entry(file, entry):
            word = entry.latest.word
            file.write('{\n')
            file.write(' "word":%s,\n' % json_str(word.word))
            file.write(' "pos":%s' % json_str(word.pos))
            if word.props:
                file.write(',\n')
                props = word.props.split(',')
                props_json = ','.join([json_str(s) for s in props])
                file.write(' "props": [%s]' % props_json)
            if word.stem:
                file.write(',\n')
                file.write(' "stem":%s' % json_str(word.stem))
            file.write('\n}')

            rev = entry.latest
            while rev:
                contributors_set.add(rev.user.username)
                if rev.reviewer:
                    contributors_set.add(rev.reviewer.username)
                rev = rev.parent

        entries = Entry.objects.filter(latest__deleted=False)
        if license:
            entries = entries.filter(latest__license=license)
        entries = entries.order_by('latest__word__word')
        file.write('{\n')
        file.write('"entries":[\n')
        if len(entries) > 0:
            write_entry(file, entries[0])
            for entry in entries[1:]:
                file.write(',\n')
                write_entry(file, entry)
            file.write('\n')
        file.write('],\n')
        file.write('"contributors":[\n')
        contributors = sorted(list(contributors_set))
        file.write(' ' + ',\n '.join([json_str(c) for c in contributors]) + '\n')
        file.write(']\n')
        file.write('}\n')
