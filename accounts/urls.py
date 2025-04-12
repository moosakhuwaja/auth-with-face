from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.landing_page, name='landing-page'),
    path('login-signup/', views.login_signup, name='login-signup'),
    path('dashboard/', views.dashboard, name='dashboard-page'),
    path('logout/', views.logout, name='logout'),
    path('deactive/', views.deactive, name='deactive')
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
