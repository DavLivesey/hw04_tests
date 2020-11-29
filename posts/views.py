from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        "index.html",
        {"page": page, 'paginator': paginator}
        )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {
        'group': group, 'page': page, 'paginator': paginator
        })


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post_get = form.save(commit=False)
            post_get.author = request.user
            post_get.save()
            return redirect('index')
    form = PostForm()
    return render(request, 'new.html', {'form': form})


@login_required
def groups(request):
    all_groups = Group.objects.all()
    paginator = Paginator(all_groups, 7)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'group_all.html',
        {'groups': all_groups, 'page': page, 'paginator': paginator}
        )


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'profile.html',
        {'author': user, 'page': page, 'paginator': paginator}
        )


def post_view(request, username, post_id):    
    post = get_object_or_404(
        Post,
        author__username=username,
        pk=post_id
        )
    return render(request, 'post.html', {'author': post.author, 'post': post})


def post_edit(request, username, post_id):    
    post = get_object_or_404(
        Post,
        pk=post_id,
        author__username=username
        )
    if request.user != post.author:
        return redirect('post', post_id=post_id)
    form = PostForm(request.POST or None, instance=post)          
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)
    else:        
        edit = True
        return render(request, 'new.html', {'form': form, 'post': post, 'edit': edit})
