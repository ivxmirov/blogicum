from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path(
        'posts/create/',
        views.PostCreateView.as_view(),
        name='create_post'
    ),
    path(
        'posts/<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'posts/<int:post_id>/comment/',
        views.CommentCreateView.as_view(),
        name='comment_create'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<comment_id>/',
        views.CommentDeleteView.as_view(),
        name='comment_delete'
    ),
    path(
        'posts/<int:post_id>/edit_comment/<comment_id>/',
        views.CommentUpdateView.as_view(),
        name='comment_edit'
    ),
    path(
        'posts/<int:post_id>/delete/',
        views.PostDeleteView.as_view(),
        name='post_delete'
    ),
    path(
        'posts/<int:post_id>/edit/',
        views.PostUpdateView.as_view(),
        name='post_edit'
    ),
    path(
        'category/<slug:category_slug>/',
        views.category_posts,
        name='category_posts'
    ),
    path(
        'profile/<slug:username>/',
        CreateView.as_view(
            template_name='blog/profile.html',
            form_class=UserCreationForm
        ),
        name='profile'
    )
]
