# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404
from .models import Post
from .forms import EmailPostForm
from django.core.mail import send_mail

def post_list(request):
    object_list = Post.published.all()
    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post,
        slug=post,
        status='published',
        publish__year=year,
        publish__month=month,
        publish__day=day
    )
    return render(request, 'blog/post/detail.html', {'post': post})

def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if(request.method == 'POST'):
        form = EmailPostForm(request.POST)
        if(form.is_valid?()):
            cd = form.cleaned_data
            post_url = request.build_absolute_url(post.get_absolute_url())
            subject = '{} ({}) recommends you read "{}"'.format(cd['name'], cd['email'], post['title'])
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url, '1', '2')
            send_mail(subject, message, 'admin@blog.com' [cd['to']])
            sent = True
        else:
            form = EmailPostForm()

    to_send = {
        'post': post
        'form': form
        'sent': sent
    }
    return render(request, 'blog/post/share.html', to_send)
