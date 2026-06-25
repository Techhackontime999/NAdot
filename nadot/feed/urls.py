from django.urls import path
from . import views

app_name = 'feed'

urlpatterns = [
    path('', views.feed, name='feed'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/comments/', views.get_comments, name='get_comments'),
    path('post/<int:post_id>/link/', views.get_post_link, name='get_post_link'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/edit/', views.get_post_for_edit, name='get_post_for_edit'),
    path('post/<int:post_id>/update/', views.update_post, name='update_post'),
    path('post/<int:post_id>/repost/', views.repost_post, name='repost_post'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('repost/<int:repost_id>/', views.repost_detail, name='repost_detail'),
    path('repost/<int:repost_id>/like/', views.like_repost, name='like_repost'),
    path('repost/<int:repost_id>/comment/', views.add_repost_comment, name='add_repost_comment'),
    path('repost/<int:repost_id>/comments/', views.get_repost_comments, name='get_repost_comments'),
    path('repost/<int:repost_id>/delete/', views.delete_repost, name='delete_repost'),
    path('repost/<int:repost_id>/update/', views.update_repost, name='update_repost'),
]
