# notifications/utils.py

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO


def notify_booking_request(customer_email, username, hall_name, booking_date, guest_count, phone, notes):
    subject = "Booking Request Submitted"
    message = render_to_string('notifications/booking_request_email.txt', {
        'username': username,
        'hall_name': hall_name,
        'booking_date': booking_date,
        'guest_count': guest_count,
        'phone': phone,
        'notes': notes or "None"
    })
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [customer_email])


def notify_owner_about_booking(owner_email, hall_name, customer_name, date, customer_phone, guest_count):
    subject = "New Booking Request Received"
    message = render_to_string('notifications/owner_booking_alert.txt', {
        'hall_name': hall_name,
        'customer_name': customer_name,
        'date': date,
        'phone': customer_phone,
        'guest_count': guest_count,
    })
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [owner_email])


def notify_booking_approval(customer_email, username, hall_name, date):
    subject = "Your Booking is Confirmed"
    message = render_to_string('notifications/booking_approved_email.txt', {
        'username': username,
        'hall_name': hall_name,
        'date': date,
    })
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [customer_email])


def notify_cancellation_request(owner_email, hall_name, customer_name, date):
    subject = "Booking Cancellation Request"
    message = render_to_string('notifications/owner_cancellation_request.txt', {
        'hall_name': hall_name,
        'customer_name': customer_name,
        'date': date,
    })
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [owner_email])


def notify_cancellation_approved(customer_email, username, hall_name, date):
    subject = "Booking Cancellation Approved"
    message = render_to_string('notifications/cancellation_approved_email.txt', {
        'username': username,
        'hall_name': hall_name,
        'date': date,
    })
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [customer_email])
    
def generate_invoice_pdf(username, hall_name, location, price, date):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
     # Title
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(300, 750, "Booking Confirmation Invoice")

    # Greeting
    p.setFont("Helvetica", 12)
    p.drawString(50, 700, f"Dear {username},")
    p.drawString(50, 680, "Thank you for booking with Mandap! Here are your details:")

    # Booking Details
    y = 640
    for label, value in [
        ("Hall Name:", hall_name),
        ("Location:", location),
        ("Price:", f"₹{price}"),
        ("Date:", str(date)),
    ]:
        p.drawString(60, y, f"{label}")
        p.drawString(160, y, value)
        y -= 20

    # Footer
    p.drawString(50, 580, "We look forward to making your event memorable!")
    p.drawString(50, 560, "— The Mandap Team")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer
