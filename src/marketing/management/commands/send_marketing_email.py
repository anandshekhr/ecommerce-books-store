from django.core.management.base import BaseCommand
from marketing.models import EmailSendRequestLog, EmailContent, EmailWhatsappTable, TbEmailSentLog
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from email.utils import formataddr
from email.header import Header
import smtplib
from django.utils import timezone


DEFAULT_BATCH_SIZE = 100


class Command(BaseCommand):
    help = "Send marketing emails in daily batches"

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=DEFAULT_BATCH_SIZE,
            help='Number of emails to send per run'
        )
        parser.add_argument(
            '--log-name',
            type=str,
            required=True,
            help='Name for EmailSendRequestLog entry'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        log_name = options['log_name']
        server = None

        self.stdout.write(self.style.SUCCESS(
            f"Email job started at {timezone.now()}"
        ))

        try:
            start, end = self._get_batch_range(limit, log_name)
            recipients = self._get_recipients(start, end)

            if not recipients:
                self.stdout.write(self.style.WARNING("No recipients found."))
                return

            email_content = self._get_email_content()
            server = self._get_smtp_server(email_content)

            self._send_emails(server, email_content, recipients)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Job failed: {e}"))

        finally:
            if server:
                server.quit()

            self.stdout.write(self.style.SUCCESS(
                f"Email job finished at {timezone.now()}"
            ))

    # -------------------------
    # Helper Methods
    # -------------------------

    def _get_batch_range(self, limit, log_name):
        try:
            last_log = EmailSendRequestLog.objects.filter(
                name=log_name
            ).latest()
            start = last_log.end_index + 1
        except EmailSendRequestLog.DoesNotExist:
            start = 0

        end = start + limit

        EmailSendRequestLog.objects.create(
            name=log_name,
            start_index=start,
            end_index=end
        )

        return start, end


    def _get_recipients(self, start, end):
        sql = """
            SELECT id, email, mobile
            FROM marketing_emailwhatsapptable
            WHERE email IS NOT NULL
            LIMIT %s
        """
        queryset = EmailWhatsappTable.objects.raw(sql, [end])
        return queryset[start:end]

    def _get_email_content(self):
        try:
            return EmailContent.objects.latest()
        except EmailContent.DoesNotExist:
            raise Exception("EmailContent does not exist.")

    def _get_smtp_server(self, content):
        server = smtplib.SMTP(content.smtp_server, int(content.smtp_port))
        server.starttls()
        server.login(content.sender_email, content.sender_password)
        return server

    def _send_emails(self, server, content, recipients):
        subject = content.subject
        body = content.content.read().decode('utf-8')

        for row in recipients:
            if not self._is_allowed_domain(row.email):
                continue

            msg = MIMEMultipart()
            msg['From'] = f"{content.sender_name} <{content.sender_email}>"
            msg['To'] = row.email
            msg['Date'] = timezone.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
            msg['Subject'] = Header(subject, 'utf-8')

            msg.attach(MIMEText(body, 'plain'))

            try:
                server.sendmail(
                    content.sender_email,
                    row.email,
                    msg.as_string()
                )
                TbEmailSentLog.objects.create(email=row.email)

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed {row.email}: {e}")
                )

    def _is_allowed_domain(self, email):
        try:
            domain = email.split('@')[1].lower()
            return not domain.startswith('yahoo')
        except IndexError:
            return False
