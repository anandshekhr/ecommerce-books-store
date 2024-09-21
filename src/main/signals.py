from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Question, Answer
from .tasks import send_notification_email
from django.contrib.auth.models import Group
from django.utils.html import format_html

@receiver(post_save,sender=Question)
def notify_teachers_on_new_questions(sender,instance,created, **kwargs):
    if created:
        subject = 'New Question Posted'
        message = f"A new question has been posted: {format_html(instance.content)}"
        teachers_group = Group.objects.get(name="teachers")
        recipient_list = [user.email for user in teachers_group.user_set.all()]
        send_notification_email.delay(subject,message,recipient_list)

@receiver(post_save,sender=Answer)
def notify_users_on_new_answer(sender,instance,created, **kwargs):
    if created:
        subject = "New Reply to Your Question"
        message = f"A new reply has been added to the question: {format_html(instance.question.content)}"
        recipient_list = [instance.question.user.email]
        send_notification_email.delay(subject,message,recipient_list)