from django.core.mail import send_mail

def send_booking_email(to_email, subject, message):
    send_mail(
        subject,
        message,
        'no-reply@mandap.com',
        [to_email],
        fail_silently=False,
    )
