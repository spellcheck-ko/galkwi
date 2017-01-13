# workaround for https://github.com/omab/python-social-auth/pull/1031

from django.utils.deprecation import MiddlewareMixin
import social_django.middleware

class SocialAuthExceptionMiddlewareMixin(
        social_django.middleware.SocialAuthExceptionMiddleware,
        MiddlewareMixin):
    """Work around Django 1.10 middleware incompatibility."""

    pass
