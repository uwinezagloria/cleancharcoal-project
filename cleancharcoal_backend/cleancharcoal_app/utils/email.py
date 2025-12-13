from django.conf import settings
from django.core.mail import send_mail

def send_email(to_email: str, subject: str, message: str) -> None:
    send_mail(
        subject=subject,
        message=message,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=[to_email],
        fail_silently=False,
    )

