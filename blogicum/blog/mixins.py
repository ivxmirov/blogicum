from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect

from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Comment, Post


class CommentMixin:
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = ['comment_id', 'post_id']
    template_name = 'blog/comment.html'

    def get_object(self):
        return get_object_or_404(Comment, pk=self.kwargs['comment_id'])

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])


class PostMixin:
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def get_object(self):
        return get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
