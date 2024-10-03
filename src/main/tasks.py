from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_notification_email(subject,message,recipient_list):
    send_mail(subject,message,'info@vamsbookstore.in',recipient_list,fail_silently=False,html_message=message)