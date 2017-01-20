from django.core.management.base import BaseCommand, CommandError
from galkwiapp.models import *
from django.utils import timezone


REQUIRED_YES = 1
REQUIRED_NO = 1
EXPIRE_DAYS = 3000
MIN_DAYS = 0 # !


class Command(BaseCommand):
    help = 'Periodic job'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.count()

    def count(self):
        proposals = Proposal.objects.all().filter(status='VOTING').order_by('date')[:999]
        now = timezone.now()
        print('total %d\n' % len(proposals))
        for proposal in proposals:
            votes_yes = Vote.objects.all().filter(proposal=proposal).filter(vote='YES')
            votes_no = Vote.objects.all().filter(proposal=proposal).filter(vote='NO')
            print('proposal %d, vote: %d/%d' % (proposal.id, votes_yes.count(), votes_no.count()))
            if (now - proposal.date).days < MIN_DAYS:
                print('  PENDING (less than %d days)' % MIN_DAYS)
            elif votes_no.count() >= REQUIRED_NO:
                print('  REJECTED')
                proposal.reject()
            elif votes_yes.count() >= REQUIRED_YES:
                print('  APPROVED')
                proposal.apply()
            elif (now - proposal.date).days >= EXPIRE_DAYS:
                print('  EXPIRED')
                proposal.expire()
            print('\n')
