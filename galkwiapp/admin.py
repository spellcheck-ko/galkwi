from django.contrib import admin
from galkwiapp.models import *

WORD_FIELDS = ['word', 'pos', 'stem', 'props', 'etym', 'orig', 'comment']


class UserAdmin(admin.ModelAdmin):
    pass


class EntryAdmin(admin.ModelAdmin):
    # fieldsets = [
    #     (None,		{'fields': WORD_FIELDS}),
    #     ("Edit Info",	{'fields': ['editor', 'date']}),
    #     ("Status",	{'fields': ['valid', 'overrides']}),
    # ]
    # list_display = ['word', 'valid', 'pos']
    # search_fields = ['word']
    pass


class RevisionAdmin(admin.ModelAdmin):
    pass


class WordAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(Revision, RevisionAdmin)
admin.site.register(Word, WordAdmin)
