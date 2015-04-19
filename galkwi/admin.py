from django.contrib import admin
from galkwi.models import *

WORD_FIELDS = ['word', 'pos', 'stem', 'props', 'etym', 'orig', 'comment']

class EntryAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,		{'fields': WORD_FIELDS}),
        ("Edit Info",	{'fields': ['editor', 'date']}),
        ("Status",	{'fields': ['valid', 'overrides']}),
    ]
    list_display = ['word', 'valid', 'pos']
    search_fields = ['word']
    pass

class ProposalAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,		{'fields': ['action', 'editor', 'date', 'rationale',
                                    'old_entry']}),
        ('Word Data',	{'fields': WORD_FIELDS, 'classes': ['collapse']}),
        ('Status',	{'fields': ['status', 'new_entry', 'status_date']}),
    ]
    list_display = ['date', 'action', 'status', 'word']
    list_filter = ['date']
    pass

admin.site.register(Entry, EntryAdmin)
admin.site.register(Proposal, ProposalAdmin)
admin.site.register(Vote)
