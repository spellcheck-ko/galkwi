# -*- coding: utf-8 -*-
from django import forms
from django.core import validators
from django.forms.utils import ValidationError
from galkwiapp.models import *
from django.contrib.auth.models import Permission
from django.utils.translation import ugettext_lazy as _


def true_validator(value):
    if not value:
        raise ValidationError(_("위 사항에 동의해야 합니다"))

tos_text = """\
작업한 데이터는 자유로운 라이선스로 배포됩니다

이용자가 이 사이트에 제출한 모든 단어 데이터는 맞춤법 검사와 같은 한국어 정보 처리 소프트웨어에 MPL 2.0 라이선스로 (http://www.mozilla.org/MPL/ 참고) 이용됩니다.

이 라이선스는 사용을 제약하는 라이선스가 아니라 제한 없는 자유로운 사용을 보장하기 위한 라이선스입니다. 이용자가 참여를 중단하는 경우에도 이미 편집한 데이터 내용은 이후에도 여전히 같은 라이선스로 배포되며 삭제되지 않습니다.


저작권 문제가 없는 데이터를 입력하십시오

이 사이트에서는 위에서 말한 라이선스로 배포하는 데 저작권 문제가 없는 단어 데이터만 수집합니다. 타인의 저작권을 침해하는 데이터를 입력할 경우 해당 데이터는 삭제되며 저작권 침해에 따른 책임은 전적으로 입력한 사람에게 있습니다.

외부의 단어 데이터를 그대로 또는 자동으로 입력하지 마십시오. 인터넷에서 다운로드할 수 있다고 해서 자유롭게 이용할 수 있다는 뜻은 아닙니다. 현재까지 알려진 다운로드할 수 있는 한글 단어 데이터 중에서 명백히 자유롭게 배포할 수 있는 데이터는 한 개도 없습니다. 단어와 품사 정보와 같은 데이터는 저작권의 대상이 아니라고 논란이 생길 수도 있으나, 이 사이트에서는 이러한 논란의 여지도 없는 데이터만 수집합니다.
"""


class UserRegistrationForm(forms.Form):
    terms = forms.CharField(label='', initial=tos_text, widget=forms.Textarea(attrs={'readonly': 'readonly'}))
    agree = forms.BooleanField(label='위 사항에 동의합니다', required=True)

    def signup(self, request, user):
        user.save()


class EntrySearchForm(forms.Form):
    word = forms.CharField(label='단어')


SUGGESTION_REVIEW_CHOICES = (
    ('HOLD', '보류'),
    ('APPROVE', '허용'),
    ('REJECT', '거절'),
)

class SuggestionReviewForm(forms.Form):
    review = forms.ChoiceField(choices=SUGGESTION_REVIEW_CHOICES, widget=forms.RadioSelect())
    comment = forms.CharField(label='리뷰 이유', required=False)


class SuggestionCancelForm(forms.Form):
    pass

error_messages = {
    'required': _('This field is required.'),
    'invalid': _('Enter a valid value.'),
}


class SuggestionEditForm(forms.ModelForm):
    description = forms.CharField(label='설명', widget=forms.Textarea, required=False)
    comment = forms.CharField(label='제안 이유', required=False)
    class Meta:
        model = Word
        exclude = []


class SuggestionRemoveForm(forms.ModelForm):
    class Meta:
        model = Revision
        fields = ['review_comment']
