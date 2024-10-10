from django.db import models
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _

class TbEmailSentLog(models.Model):
    email = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(_("created_at"), auto_now=False, auto_now_add=True)
    mobile = models.TextField(blank=True, null=True)


class EmailWhatsappTable(models.Model):
    name = models.CharField(max_length=5000, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=5000, blank=True, null=True)
    mobile = models.CharField(max_length=2000, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    pincode = models.CharField(max_length=2000, blank=True, null=True)
    business = models.TextField(blank=True, null=True)
    job_title = models.CharField(max_length=5000, blank=True, null=True)
    city = models.CharField(max_length=2000, blank=True, null=True)
    website = models.CharField(max_length=2000, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)
    


# Create your models here.
class EmailContent(models.Model):
    subject = models.CharField(_("Subject"), max_length=50)
    text = models.CharField(_("Text body"), max_length=50,null=True,blank=True)
    header = models.CharField(_("Header"), max_length=50,null=True, blank=True)
    content = models.TextField(_("Body Content"))
    sender_email = models.CharField(_("sender_email"), max_length=50,null=True, blank=True)
    sender_password = models.CharField(_("sender_password"), max_length=50,null=True, blank=True)
    smtp_server = models.CharField(_("smtp_server"), max_length=50,null=True, blank=True)
    smtp_port = models.CharField(_("smtp_port"), max_length=50,null=True, blank=True)

    created_at = models.DateTimeField(_("Created At"), auto_now=False, auto_now_add=True)
    modified_at = models.DateTimeField(_("Modified At"), auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = _("EmailContent")
        verbose_name_plural = _("EmailContents")
        get_latest_by = 'created_at'


    def __str__(self):
        return "{id}".format(id=self.pk)

    def get_absolute_url(self):
        return reverse("EmailContent_detail", kwargs={"pk": self.pk})
    
    def subject_preview(self):
        return strip_tags(self.subject.html)[:75] + "..." if len(self.subject.html) > 75 else strip_tags(self.subject.html)

    subject_preview.short_description = 'subject Preview'

class EmailSendRequestLog(models.Model):
    name = models.CharField(_("name"), max_length=50)
    start_index = models.CharField(_("Start"), max_length=50)
    end_index = models.CharField(_("End"), max_length=50)
    created_at = models.DateTimeField(_("Requested At"), auto_now=False, auto_now_add=True)
    
    class Meta:
        verbose_name = _("EmailSendRequestLog")
        verbose_name_plural = _("EmailSendRequestLogs")
        get_latest_by = 'created_at'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("EmailSendRequestLog_detail", kwargs={"pk": self.pk})

