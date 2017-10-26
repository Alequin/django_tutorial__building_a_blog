# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count

def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None
    if(tag_slug):
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    to_send = {'page': page, 'posts': posts, 'tag': tag}
    return render(request, 'blog/post/list.html', to_send)

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
        slug=post,
        status='published',
        publish__year=year,
        publish__month=month,
        publish__day=day
    )

    comments = post.comments.filter(active=True)
    comment_form = None
    if(request.method == 'POST'):
        comment_form = CommentForm(data=request.POST)
        if(comment_form.is_valid()):
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    post_tags_id = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_id).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=(Count('tags'))).order_by('-same_tags', '-publish')[:4]

    to_send = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'similar_posts': similar_posts
    }
    return render(request, 'blog/post/detail.html', to_send)

def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    form = None
    if(request.method == 'POST'):
        form = EmailPostForm(request.POST)
        if(form.is_valid()):
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you read "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url, '1', '2')
            # send_mail(subject, message, 'admin@blog.com', [cd['to']])
            print('send does not work due to SMTPDataError')
            sent = True
    else:
        form = EmailPostForm()

    to_send = {
        'post': post,
        'form': form,
        'sent': sent
    }
    return render(request, 'blog/post/share.html', to_send)
