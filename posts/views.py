from django.shortcuts import render, redirect
from accounts.models import User, Session
from .models import Post, Comment
from django.contrib import messages
from django.http import JsonResponse


def show_posts(request):
    user_id = request.session.get('user_id')
    token = request.session.get('token')
    if user_id and token:
        try:
            session = Session.objects.get(session_token=token, is_active=True)
            user = session.user
            posts = Post.objects.filter(status=True).select_related(
                'user').order_by('-created_at')
            return render(request, 'posts.html', {'user': user, 'posts': posts})
        except Session.DoesNotExist:
            messages.error(request, 'Session expired or invalid.')
            request.session.flush()
            return redirect('login-signup')
    else:
        return redirect('login-signup')


# views.py
def create_post(request):
    token = request.session.get('token')
    if not token:
        return JsonResponse({'message': 'Session expired or invalid.', 'type': 'error'}, status=401)

    try:
        session = Session.objects.get(session_token=token, is_active=True)
        user = session.user
    except Session.DoesNotExist:
        return JsonResponse({'message': 'Session expired or invalid.', 'type': 'error'}, status=401)

    if request.method == 'POST':
        description = request.POST.get('description')
        if description:
            post = Post.objects.create(user=user, description=description)
            return JsonResponse({
                'message': 'Post created successfully!',
                'type': 'success',
                'post': {
                    'id': post.id,
                    'description': post.description,
                    'username': user.username,
                    'time': 'Just now'
                }
            })
        else:
            return JsonResponse({'message': 'Description cannot be empty.', 'type': 'error'}, status=400)

    return JsonResponse({'message': 'Invalid request method.', 'type': 'error'}, status=405)


def comment(request):
    token = request.session.get('token')
    if not token:
        return JsonResponse({'message': 'Session expired or invalid.', 'type': 'error'}, status=401)

    try:
        session = Session.objects.get(session_token=token, is_active=True)
        user = session.user
    except Session.DoesNotExist:
        return JsonResponse({'message': 'Session expired or invalid.', 'type': 'error'}, status=401)

    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        description = request.POST.get('description')

        if not post_id or not description:
            return JsonResponse({'message': 'Post ID and description are required.', 'type': 'error'}, status=400)

        try:
            post = Post.objects.get(id=post_id, status=True)
            Comment.objects.create(
                post_id=post, description=description, user=user)
            return JsonResponse({
                'message': 'Comment added successfully!',
                'type': 'success',
                'comment': {
                    'description': description,
                    'username': user.username,
                    'time': 'Just now'
                }
            })
        except Post.DoesNotExist:
            return JsonResponse({'message': 'Post not found.', 'type': 'error'}, status=404)

    return JsonResponse({'message': 'Invalid request method.', 'type': 'error'}, status=405)


def get_comments(request):
    post_id = request.GET.get('post_id')
    if not post_id:
        return JsonResponse({'message': 'Post ID is required.', 'type': 'error'}, status=400)

    try:
        comments = Comment.objects.filter(
            post_id=post_id, status=True).select_related('user').order_by('created_at')
        comments_data = [{
            'description': comment.description,
            'username': comment.user.username,
            'time': comment.created_at.strftime('%b %d, %Y %I:%M %p')
        } for comment in comments]

        return JsonResponse({'comments': comments_data, 'type': 'success'})
    except Exception as e:
        return JsonResponse({'message': str(e), 'type': 'error'}, status=500)


# views.py
def edit_post(request):
    token = request.session.get('token')
    if not token:
        return JsonResponse({'message': 'Session expired or invalid.', 'type': 'error'}, status=401)

    try:
        session = Session.objects.get(session_token=token, is_active=True)
        user = session.user
    except Session.DoesNotExist:
        return JsonResponse({'message': 'Session expired or invalid.', 'type': 'error'}, status=401)

    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        description = request.POST.get('description')

        if not post_id or not description:
            return JsonResponse({'message': 'Post ID and description are required.', 'type': 'error'}, status=400)

        try:
            post = Post.objects.get(id=post_id, user=user)
            post.description = description
            post.save()
            return JsonResponse({
                'message': 'Post updated successfully!',
                'type': 'success',
                'post': {
                    'id': post.id,
                    'description': post.description,
                    'time': 'Just now'
                }
            })
        except Post.DoesNotExist:
            return JsonResponse({'message': 'Post not found or you are not authorized to edit it.', 'type': 'error'}, status=404)

    return JsonResponse({'message': 'Invalid request method.', 'type': 'error'}, status=405)


def delete_post(request):
    token = request.session.get('token')
    if not token:
        return JsonResponse({'message': 'Session expired or invalid.', 'type': 'error'}, status=401)

    try:
        session = Session.objects.get(session_token=token, is_active=True)
        user = session.user
    except Session.DoesNotExist:
        return JsonResponse({'message': 'Session expired or invalid.', 'type': 'error'}, status=401)

    if request.method == 'POST':
        post_id = request.POST.get('post_id')

        if not post_id:
            return JsonResponse({'message': 'Post ID is required.', 'type': 'error'}, status=400)

        try:
            post = Post.objects.get(id=post_id, user=user)
            post.status = False
            post.save()
            return JsonResponse({
                'message': 'Post deleted successfully!',
                'type': 'success'
            })
        except Post.DoesNotExist:
            return JsonResponse({'message': 'Post not found or you are not authorized to delete it.', 'type': 'error'}, status=404)

    return JsonResponse({'message': 'Invalid request method.', 'type': 'error'}, status=405)
