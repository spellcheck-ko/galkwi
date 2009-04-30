# -*- coding: utf-8 -*-

REQUIRED_YES = 1
REQUIRED_NO = 1
EXPIRE_DAYS = 14

from django.http import HttpResponse
from datetime import datetime
from google.appengine.ext import db
from google.appengine.api.datastore import Query
from galkwi.models import *
from django.contrib.auth.models import User

def count(request):
    proposals = Proposal.all().filter('status =', 'VOTING').order('date').fetch(999)
    now = datetime.now()
    response = HttpResponse(mimetype='text/plain')
    response.write('total %d\n' % len(proposals))
    for proposal in proposals:
        votes_yes = Vote.all().filter('proposal =', proposal).filter('vote =', 'YES')
        votes_no = Vote.all().filter('proposal =', proposal).filter('vote =', 'NO')
        response.write('proposal %d, vote: %d/%d' % (proposal.key().id(),
                                                     votes_yes.count(),
                                                     votes_no.count()))
        if votes_no.count() >= REQUIRED_NO:
            response.write('  REJECTED')
            proposal.reject()
        elif votes_yes.count() >= REQUIRED_YES:
            response.write('  APPROVED')
            proposal.apply()
        elif (now - proposal.date).days >= EXPIRE_DAYS:
            response.write('  EXPIRED')
            proposal.expire()
        #else:
        #    response.write('  APPROVED')
        #    proposal.apply()
        response.write('\n')
    return response
