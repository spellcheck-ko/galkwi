from django.shortcuts import redirect
from social_core.pipeline.partial import partial
from django.contrib.auth.models import Permission


def set_new_user(backend, user, response, is_new=False, *args, **kwargs):
    if is_new:
        p = Permission.objects.get(codename='can_suggest')
        user.user_permissions.add(p)
    return None
