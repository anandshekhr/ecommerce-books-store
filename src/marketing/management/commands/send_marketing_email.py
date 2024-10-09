from django.core.management.base import BaseCommand
from marketing.models import EmailSendRequestLog, EmailContent, EmailWhatsappTable, TbEmailSentLog
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from email.utils import formataddr
from email.header import Header
import smtplib

class Command(BaseCommand):
    help = 'Send Marketing Emails to 100 emails every day'

    def handle(self, *args, **kwargs):
        try:
            self.stdout.write(self.style.SUCCESS(f'Emails sending job starts at {datetime.now()}'))
            try:
                email_log_previous = EmailSendRequestLog.objects.latest()
                if email_log_previous:
                    start = int(email_log_previous.end_index) + 1
                    end = start + 5
            except EmailSendRequestLog.DoesNotExist:
                start = 0
                end = 5

            EmailSendRequestLog.objects.create(name='scheduled-email-teachers',start_index=start,end_index=end)
            # email_list= GoogleSearchResult.objects.raw(f'Select id, email, phone from tb_google_search_results where email is not null LIMIT {limit} OFFSET {offset}')
            sql = 'SELECT id, email, mobile FROM marketing_emailwhatsapptable WHERE email IS NOT NULL LIMIT %s'
            email_list = EmailWhatsappTable.objects.raw(sql, [int(end)])
            email_list = email_list[int(start):]
            
            # get template
            try:
                e_content = EmailContent.objects.latest()
            except EmailContent.DoesNotExist:
                self.stdout.write(self.style.ERROR('Email Content Does Not Exists.'))
                return
            
            if e_content:
                subject = e_content.subject


            # Set up the SMTP server
            server = smtplib.SMTP(e_content.smtp_server, e_content.smtp_port)
            server.starttls()
            server.login(e_content.sender_email, e_content.sender_password)

            # Send emails
            for index, row in enumerate(email_list):
                a = row.email.split('@')
                b = a[1].split('.') if len(a) > 1 else a[0]
                if not b[0].startswith('yahoo'):
                    
                    # Create a new message object for each email
                    msg = MIMEMultipart()
                    msg['From'] = "Books Store <"+e_content.sender_email+">"
                    msg['To'] = row.email
                    msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
                    msg['Subject'] = Header(subject, 'utf-8')

                    # Attach the plain text and HTML parts
                    part1 = MIMEText(e_content.content, 'plain')
                    msg.attach(part1)

                    try:
                        server.sendmail(e_content.sender_email, row.email, msg.as_string())
                        TbEmailSentLog.objects.create(email=row.email)
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Failed: {row.email}: {e}"))

            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Some Errors Occurred: {str(e)}'))
        finally:
            self.stdout.write(self.style.SUCCESS(f"Emails Sending job completed at: {datetime.now()}"))
            server.quit()