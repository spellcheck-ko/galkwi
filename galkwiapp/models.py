from django.db import models
from django.contrib.auth import models as auth_models
from django.utils import timezone


class User(auth_models.AbstractUser):
    REQUIRED_FIELDS = ['email']

POS_CHOICES = [
    ('명사', '명사'),
    ('동사', '동사'),
    ('형용사', '형용사'),
    ('부사', '부사'),
    ('부사:상태', '부사:상태'),
    ('부사:성상', '부사:성상'),
    ('부사:지시', '부사:지시'),
    ('부사:정도', '부사:정도'),
    ('부사:부정', '부사:부정'),
    ('부사:양태', '부사:양태'),
    ('부사:접속', '부사:접속'),
    ('대명사', '대명사'),
    ('감탄사', '감탄사'),
    ('관형사', '관형사'),
    ('특수:금지어', '특수:금지어'),
    ('특수:파생형', '특수:파생형'),
]


# word entry in dictionary
class Word(models.Model):
    # word data
    word = models.CharField(verbose_name='단어', max_length=100)
    pos = models.CharField(verbose_name='품사', max_length=100, choices=POS_CHOICES)
    props = models.CharField(verbose_name='속성', max_length=100, blank=True)
    stem = models.CharField(verbose_name='어근', max_length=100, blank=True)
    etym = models.CharField(verbose_name='어원', max_length=100, blank=True)
    orig = models.CharField(verbose_name='본딧말', max_length=100, blank=True)
    description = models.CharField(verbose_name='설명', max_length=1000, blank=True)

    def __str__(self):
        name = '%s(%s)' % (self.word, self.pos)
        return name

    class Meta:
        index_together = [
            ['word', 'pos']
        ]


class Entry(models.Model):
    title = models.CharField(verbose_name='제목', max_length=100)
    latest = models.ForeignKey('Revision', related_name='revision_latest', null=True, blank=True)
    # TODO: discuss

    class Meta:
        verbose_name_plural = 'Entries'
    #     ordering = ['word', 'pos', 'valid']

    def __str__(self):
        name = '%s' % (self.title)
        return name

    def get_absolute_url(self):
        return '/entry/%d/' % (self.id)

    def update_rev(self, rev):
        self.latest = rev
        if rev.deleted:
            word = rev.parent.word
            self.title = 'OBSOLETE:%s(%s)' % (word.word, word.pos)
        else:
            word = rev.word
            self.title = '%s(%s)' % (word.word, word.pos)
        if rev.parent:
            old_rev = rev.parent
            old_rev.status = Revision.STATUS_REPLACED
            old_rev.save()
        self.save()


class Revision(models.Model):
    STATUS_DRAFT = 0
    STATUS_REVIEWING = 1
    STATUS_CANCELED = 2
    STATUS_APPROVED = 3
    STATUS_REJECTED = 4
    STATUS_REPLACED = 5

    STATUS_CHOICES = (
        (STATUS_DRAFT, '편집 중'),
        (STATUS_REVIEWING, '리뷰 중'),
        (STATUS_CANCELED, '취소'),
        (STATUS_APPROVED, '허용'),
        (STATUS_REJECTED, '거절'),
        (STATUS_REPLACED, '대체됨'),
    )

    status = models.IntegerField(verbose_name='상태', choices=STATUS_CHOICES)
    entry = models.ForeignKey(Entry, verbose_name='단어 항목', null=True, blank=True)
    parent = models.ForeignKey('self', verbose_name='이전 리비전', null=True, blank=True)
    # content or deleted
    word = models.ForeignKey(Word, verbose_name='단어 데이터', null=True, blank=True)
    deleted = models.BooleanField(verbose_name='삭제', default=False)

    comment = models.CharField(verbose_name='설명', max_length=1000, blank=True)
    user = models.ForeignKey(User, verbose_name='편집자')
    # user_text = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(verbose_name='제안 시각')

    reviewer = models.ForeignKey(User, verbose_name='리뷰어', related_name='reviewer', null=True, blank=True)
    review_comment = models.CharField(verbose_name='리뷰 설명', max_length=1000, blank=True)
    review_timestamp = models.DateTimeField(verbose_name='리뷰 시각', null=True, blank=True)

    class Meta:
        ordering = ['-timestamp', 'status']
        permissions = [
            ("can_suggest", "Can suggest a change"),
            ("can_review", "Can review a suggestion"),
        ]

    def __str__(self):
        name = '%d:' % self.id
        if self.action_is_add():
            name += 'ADD:' + str(self.word)
        elif self.action_is_remove():
            name += 'REMOVE:' + str(self.parent.word)
        elif self.action_is_update():
            name += 'UPDATE:' + str(self.word)
        return name

    def action_name(self):
        if self.parent is None:
            return 'ADD'
        else:
            if self.deleted:
                return 'REMOVE'
            else:
                return 'UPDATE'

    def action_is_add(self):
        return self.parent is None

    def action_is_remove(self):
        return self.parent is not None and self.deleted

    def action_is_update(self):
        return self.parent is not None and not self.deleted

    def status_name(self):
        return Revision.STATUS_CHOICES[self.status][1]

    def status_is_approved(self):
        return self.status == Revision.STATUS_APPROVED

    def status_is_reviewing(self):
        return self.status == Revision.STATUS_REVIEWING

    def get_absolute_url(self):
        return '/suggestion/%d/' % (self.id)

    def approve(self, reviewer, comment):
        if self.status != Revision.STATUS_REVIEWING:
            return
        if self.action_is_add():
            entry = Entry()
            entry.save()
            self.entry = entry
        else:
            entry = self.entry
        entry.update_rev(self)
        self.reviewer = reviewer
        self.review_comment = comment
        self.review_timestamp = timezone.now()
        self.status = Revision.STATUS_APPROVED
        self.save()

    def reject(self, reviewer, comment):
        self.reviewer = reviewer
        self.review_comment = comment
        self.review_timestamp = timezone.now()
        self.status = Revision.STATUS_REJECTED
        self.save()

    def cancel(self):
        self.status = Revision.STATUS_CANCELED
        self.save()
