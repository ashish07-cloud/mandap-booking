from django.contrib import admin
from django.urls import path, include
from users import views as user_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_views.index, name='index'),
    path('users/', include('users.urls', namespace='users')),
    path('booking/', include('booking.urls', namespace='booking')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
]

# Static file config
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ✅ Custom error handlers (should be at the end)
handler404 = 'marriage_hall_booking.views.error_404_view'
handler500 = 'marriage_hall_booking.views.custom_500_view'
handler403 = 'marriage_hall_booking.views.custom_403_view'
handler400 = 'marriage_hall_booking.views.custom_400_view'
