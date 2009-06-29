# -*- coding: utf-8 -*-

REQUIRED_YES = 1
REQUIRED_NO = 1
EXPIRE_DAYS = 14
MIN_DAYS = 1

from django.http import HttpResponse
from datetime import datetime
from google.appengine.ext import db
from google.appengine.api.datastore import Query
from galkwi.models import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import permission_required
from xml.sax.saxutils import escape as xml_escape

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
        if (now - proposal.date).days < MIN_DAYS:
            response.write('  PENDING (less than %d days)' % MIN_DAYS)
        elif votes_no.count() >= REQUIRED_NO:
            response.write('  REJECTED')
            proposal.reject()
        elif votes_yes.count() >= REQUIRED_YES:
            response.write('  APPROVED')
            proposal.apply()
        elif (now - proposal.date).days >= EXPIRE_DAYS:
            response.write('  EXPIRED')
            proposal.expire()
        response.write('\n')
    return response
count = permission_required('galkwi.can_vote')(count)

EXPORT_CHUNK_SIZE = 100

def export(request):
    start = request.GET.get('start')
    response = HttpResponse(mimetype='application/xml')
    query = Entry.all()
    if start:
        query.filter('word >=', start)
    query.filter('valid =', True)
    query.order('word')
    entries = query.fetch(EXPORT_CHUNK_SIZE)
    response.write('<exported-data>\n')
    for entry in entries:
        if not entry.valid:
            continue
        response.write('<Entry>\n')
        response.write('<word>%s</word>\n' % entry.word)
        response.write('<pos>%s</pos>\n' % entry.pos)
        if entry.props:
            response.write('<props>%s</props>\n' % xml_escape(entry.props))
        if entry.stem:
            response.write('<stem>%s</stem>\n' % entry.stem)
        if entry.etym:
            response.write('<etym>%s</etym>\n' % entry.etym)
        if entry.comment:
            response.write('<comment>%s</comment>\n' % xml_escape(entry.comment))
        response.write('<editors>')
        for ekey in entry.editors:
            editor = db.get(ekey)
            response.write('<name>%s</name>' % editor.username)
        response.write('</editor>\n')
        response.write('<editor>%s</editor>\n' % entry.editor.username)
        response.write('<date>%s</date>\n' % entry.date.strftime('%Y-%m-%d %H:%M:%S'))
        response.write('</Entry>\n')
    response.write('</exported-data>\n')
    return response
