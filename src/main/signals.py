from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Question, Answer
# from .tasks import send_notification_email
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.core.mail import send_mail
import threading
from bookstore.utils import HashIdConverter

obj = HashIdConverter()
def send_notification_email(subject,message,recipient_list):
    send_mail(subject,message,'shopping@vamscentral.com',recipient_list,fail_silently=False,html_message=message)

@receiver(post_save,sender=Question)
def notify_teachers_on_new_questions(sender,instance,created, **kwargs):
    hashed_id = obj.to_url(instance.id)
    if created:
        subject = 'New Question Posted on VAMS eBook Store'
        reply_link = f'<a href="https://www.vamsbookstore.int/questions/{hashed_id}/">Click Here</a> to post a reply'
        email_content = format_html(
            """
            <html>
                <head>
                <style>
                body {{
                    font-family: "DM Sans", sans-serif;
                    overflow-x: hidden;
                    background-color: grey;
                }}
                h1, h2, h3 {{
                    font-family: 'DM Sans', sans-serif; /* Example: Different font for headings */
                }}
                </style>
                </head>
                <body>
                    <h3>A new question has been posted:</h3>
                    <p>{content}</p>
                    <p>{link}</p>
                </body>
            </html>
            """,
            content=format_html(instance.content), 
            link=format_html(reply_link)
        )
        message = f"A new question has been posted: {format_html(instance.content)} \n click here to post a reply"
        teachers_group = Group.objects.get(name="teachers")
        recipient_list = [user.email for user in teachers_group.user_set.all()]
        # send_notification_email.delay(subject,message,recipient_list)
        threading.Thread(target=send_notification_email, args=(subject, email_content, recipient_list)).start()

@receiver(post_save,sender=Answer)
def notify_users_on_new_answer(sender,instance,created, **kwargs):
    hashed_id = obj.to_url(instance.id)
    if created:
        subject = "New Reply to Your Question"
        reply_link = f'<a href="https://www.vamsbookstore.int/questions/{hashed_id}/">Click Here</a> to view reply'
        email_content = format_html(
            """
            <html>
                <head>
                <style>
                body {{
                    font-family: "DM Sans", sans-serif;
                    overflow-x: hidden;
                    background-color: grey;
                }}
                h1, h2, h3 {{
                    font-family: 'DM Sans', sans-serif; /* Example: Different font for headings */
                }}
                </style>
                </head>
                <body>
                    <h3>You got a new Reply to your question: </h3>
                    <p>{content}</p>
                    <p>{link}</p>
                </body>
            </html>
            """,
            content=format_html(instance.question.content), 
            link=format_html(reply_link)
        )
        message = f"A new reply has been added to the question: {format_html(instance.question.content)}"
        recipient_list = [instance.question.user.email]
        # send_notification_email.delay(subject,message,recipient_list)
        threading.Thread(target=send_notification_email, args=(subject, message, recipient_list)).start()