Mandap Booking Platform 🎪
A Django-based solution for traditional wedding venue reservations

Python 3.9+
Django 4.0+

Overview
A full-stack web application designed to streamline the process of booking mandaps (traditional wedding pavilions) for Hindu weddings. The platform handles complete booking lifecycle management with secure payment integration.

✨ Key Features
User Management
JWT-based authentication system
Role-based access control (Admin/User)
Email verification workflow
Booking System
Real-time mandap availability checking
Multi-step booking process with date selection
Booking modification/cancellation system
Payment Integration
Razorpay/Stripe payment gateway integration
Payment success/failure handling
Invoice generation
Notification System
Email notifications for booking updates
SMS alerts for critical updates
In-app notification center
🛠 Technology Stack
Component	Technology
Frontend	HTML5, CSS3, JavaScript
Backend	Django 4.0+
Database	PostgreSQL
Authentication	Django REST Framework JWT
Payment Gateway	Razorpay API
Deployment	Docker, Nginx


🚀 Installation Guide
Prerequisites
Python 3.9+
PostgreSQL 12+
Redis (for caching)
# Clone repository
git clone https://github.com/ashish07-cloud/mandap-booking.git
cd mandap-booking

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
⚙ Configuration
Create .env file:

