# models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.urls import reverse

class RequestDataLog(models.Model):
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=255)
    body = models.TextField()
    user_agent = models.CharField(max_length=255)
    client_ip = models.CharField(max_length=50,null=True,blank=True)
    country = models.CharField(max_length=200,null=True,blank=True)
    mobile = models.BooleanField(default=False)
    is_new_user = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.method} {self.path}'

class ErrorLog(models.Model):
    user_token = models.CharField(_("User Token"), max_length=500, null=True, blank=True)
    error_message = models.TextField(_("Error Message"))
    error_details = models.TextField(_("Error Details"))
    api_name = models.CharField(_("Api Name"), max_length=50, null=True, blank=True)
    timestamp = models.DateTimeField(_("Timestamp"), auto_now=False, auto_now_add=False)

    class Meta:
        verbose_name = _("ErrorLog")
        verbose_name_plural = _("ErrorLogs")

    def __str__(self):
        return self.error_message

    def get_absolute_url(self):
        return reverse("ErrorLog_detail", kwargs={"pk": self.pk})
