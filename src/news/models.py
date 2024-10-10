from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


# Create your models here.
class NewsTheHindu(models.Model):
    headline = models.CharField(_("Headlines"), max_length=1000)
    link = models.CharField(_("Link"), max_length=100000)
    sub_title = models.CharField(_("Sub Title"), max_length=1000)
    publish_time = models.CharField(_("Publish Title"), max_length=500,null=True,blank=True)
    author = models.CharField(_("Author"), max_length=500,null=True,blank=True)
    content = models.TextField(_("Contents"))
    created_at = models.DateTimeField(_("Created At"), auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(_("Modified At"), auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = _("NewsTheHindu")
        verbose_name_plural = _("NewsTheHindus")

    def __str__(self):
        return self.headline

    def get_absolute_url(self):
        return reverse("NewsTheHindu_detail", kwargs={"pk": self.pk})
