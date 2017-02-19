# -*- coding: utf-8 -*-
from django import forms
from django.core import validators
from django.forms.utils import ValidationError
from galkwiapp.models import *
from django.contrib.auth.models import Permission
from django.utils.translation import ugettext_lazy as _


class EntrySearchForm(forms.Form):
    word = forms.CharField(label='단어')

    def get_word(self):
        if self.is_bound and self.is_valid():
            return self.cleaned_data['word']
        else:
            return None


class SuggestionReviewForm(forms.Form):
    REVIEW_CHOICES = (
        ('HOLD', '보류'),
        ('APPROVE', '허용'),
        ('REJECT', '거절'),
    )

    review = forms.ChoiceField(choices=REVIEW_CHOICES,
                               widget=forms.RadioSelect())
    comment = forms.CharField(label='리뷰 이유', required=False)


class SuggestionCancelForm(forms.Form):
    pass


PROPS_LIST = ('가산명사', '단위명사', '보조용언:-어', '보조용언:-을', '보조용언:-은', '용언합성', '준말용언',
              'ㄷ불규칙', 'ㅂ불규칙', 'ㅅ불규칙', 'ㅎ불규칙', '러불규칙', '르불규칙', '우불규칙', '으불규칙')
PROPS_CHOICES = tuple(zip(PROPS_LIST, PROPS_LIST))

class SuggestionEditForm(forms.ModelForm):
    # override widget
    props = forms.MultipleChoiceField(label='속성', required=False, widget=forms.CheckboxSelectMultiple, choices=PROPS_CHOICES)

    description = forms.CharField(label='설명', widget=forms.Textarea,
                                  required=False)
    # add comment
    comment = forms.CharField(label='제안 이유', required=False)

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            if 'initial' not in kwargs:
                kwargs['initial'] = {}
            try:
                kwargs['initial']['props'] = kwargs['instance'].props.split(',')
            except AttributeError:
                kwargs['initial']['props'] = []
        super(SuggestionEditForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        word = super(SuggestionEditForm, self).save(*args, **kwargs)
        word.props = ','.join(sorted(self.cleaned_data.get('props')))
        return word

    class Meta:
        model = Word
        exclude = []


class SuggestionRemoveForm(forms.Form):
    # add comment
    comment = forms.CharField(label='제안 이유', required=True)


class TermsAgreeForm(forms.Form):
    label_license = "기여한 내용을 MPL/GPL/LGPL 라이선스로 배포하는데 동의합니다. 이 동의는 철회할 수 없습니다."
    label_responsible = "저작권 문제가 없는 데이터만 기여했습니다. 저작권 위반에 따른 책임은 기여자에게 있습니다."

    agree_license = forms.BooleanField(label=label_license)
    agree_responsible = forms.BooleanField(label=label_responsible)


error_messages = {
    'required': _('This field is required.'),
    'invalid': _('Enter a valid value.'),
}
