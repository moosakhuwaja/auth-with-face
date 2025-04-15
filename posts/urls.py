from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_posts, name='show-posts'),
    path('create-post/', views.create_post, name='create-post'),
    path('comment/', views.comment, name='comment'),
    path('edit-post/', views.edit_post, name='edit-post'),
    path('delete-post/', views.delete_post, name='delete-post'),
    path('get-comments/', views.get_comments, name='get-comments'),
]
