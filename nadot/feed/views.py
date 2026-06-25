import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.conf import settings
from django.db.models import Prefetch, Q
from .models import DocumentPage
from .models import Post, Comment, PostAttachment, Repost
from .forms import PostForm, CommentForm
from core.validators import AttachmentUploadValidator
from .document_processor import extract_pdf_pages

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
VIDEO_EXTENSIONS = {'.mp4', '.webm', '.mov', '.avi', '.mkv'}
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.flac', '.aac', '.wma'}
DOCUMENT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.ppt', '.pptx', '.txt', '.csv'}


def _get_file_type(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext in IMAGE_EXTENSIONS:
        return 'image'
    if ext in VIDEO_EXTENSIONS:
        return 'video'
    if ext in AUDIO_EXTENSIONS:
        return 'audio'
    if ext in DOCUMENT_EXTENSIONS:
        return 'document'
    return 'document'


def _handle_post_attachments(post, files):
    if not files:
        return
    validator = AttachmentUploadValidator()
    sort_order = 0
    for f in files:
        try:
            validator(f)
        except ValidationError as e:
            raise ValidationError(f"{f.name}: {'; '.join(e.messages)}")
        file_type = _get_file_type(f.name)
        attachment = PostAttachment(post=post, file=f, file_type=file_type, sort_order=sort_order)
        attachment.save()
        sort_order += 1
        if file_type == 'document':
            extract_pdf_pages(attachment)


@login_required
def feed(request):
    form = PostForm()
    error_message = None

    posts = Post.objects.select_related(
        'user__profile'
    ).prefetch_related(
        'likes', 'comments', 'reposts',
        Prefetch('attachments', queryset=PostAttachment.objects.prefetch_related('pages'))
    ).order_by('-created_at')

    reposts = Repost.objects.select_related(
        'user__profile', 'original_post__user__profile'
    ).prefetch_related(
        'likes', 'repost_comments',
        'original_post__likes', 'original_post__comments', 'original_post__reposts',
        Prefetch('original_post__attachments', queryset=PostAttachment.objects.prefetch_related('pages'))
    ).order_by('-created_at')

    feed_items = []
    p_iter = iter(posts)
    r_iter = iter(reposts)
    p = next(p_iter, None)
    r = next(r_iter, None)
    while p is not None or r is not None:
        if r is None or (p is not None and p.created_at >= r.created_at):
            feed_items.append({'type': 'post', 'object': p})
            p = next(p_iter, None)
        else:
            feed_items.append({'type': 'repost', 'object': r})
            r = next(r_iter, None)

    paginator = Paginator(feed_items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    total_count = len(feed_items)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()

            multiple_files = request.FILES.getlist('attachments')
            if multiple_files:
                try:
                    _handle_post_attachments(post, multiple_files)
                except ValidationError as e:
                    post.delete()
                    error_message = '; '.join(e.messages)
                    form.add_error(None, error_message)
                    return render(request, 'feed/index.html', {
                        'page_obj': page_obj,
                        'form': form,
                        'total_posts': total_count,
                        'error_message': error_message
                    })
            return redirect('feed:feed')
    
    return render(request, 'feed/index.html', {
        'page_obj': page_obj,
        'form': form,
        'total_posts': total_count,
        'error_message': error_message
    })

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        is_liked = False
    else:
        post.likes.add(request.user)
        is_liked = True
    return JsonResponse({'likes_count': post.likes.count(), 'is_liked': is_liked})

@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')
        
        if content:
            kwargs = {'post': post, 'user': request.user, 'content': content}
            if parent_id:
                parent = get_object_or_404(Comment, id=parent_id, post=post)
                kwargs['parent'] = parent
            comment = Comment.objects.create(**kwargs)
            avatar_url = None
            if comment.user.profile.avatar:
                avatar_url = comment.user.profile.avatar.url
            return JsonResponse({
                'success': True,
                'comment': {
                    'id': comment.id,
                    'user': comment.user.username,
                    'content': comment.content,
                    'created_at': comment.created_at.strftime('%b %d, %Y at %I:%M %p'),
                    'is_owner': comment.user == request.user,
                    'avatar_url': avatar_url,
                    'parent_id': int(parent_id) if parent_id else None,
                    'total_likes': 0,
                    'is_liked': False
                },
                'comments_count': post.total_comments()
            })
        else:
            return JsonResponse({'success': False, 'error': 'Comment cannot be empty'}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
def get_comments(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.select_related('user').prefetch_related('likes', 'replies__user', 'replies__likes').all()
    
    def serialize_comment(c):
        avatar_url = None
        if c.user.profile.avatar:
            avatar_url = c.user.profile.avatar.url
        replies_data = []
        for reply in c.replies.all():
            reply_avatar = None
            if reply.user.profile.avatar:
                reply_avatar = reply.user.profile.avatar.url
            replies_data.append({
                'id': reply.id,
                'user': reply.user.username,
                'content': reply.content,
                'created_at': reply.created_at.strftime('%b %d, %Y at %I:%M %p'),
                'is_owner': reply.user == request.user,
                'avatar_url': reply_avatar,
                'total_likes': reply.total_likes(),
                'is_liked': request.user in reply.likes.all()
            })
        return {
            'id': c.id,
            'user': c.user.username,
            'content': c.content,
            'created_at': c.created_at.strftime('%b %d, %Y at %I:%M %p'),
            'is_owner': c.user == request.user,
            'avatar_url': avatar_url,
            'total_likes': c.total_likes(),
            'is_liked': request.user in c.likes.all(),
            'replies': replies_data,
            'total_replies': c.total_replies()
        }
    
    comments_data = [serialize_comment(c) for c in comments if c.parent is None]
    
    return JsonResponse({
        'success': True,
        'comments': comments_data,
        'comments_count': len(comments_data)
    })

@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        is_liked = False
    else:
        comment.likes.add(request.user)
        is_liked = True
    return JsonResponse({'likes_count': comment.likes.count(), 'is_liked': is_liked})


@login_required
def get_post_link(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post_url = request.build_absolute_uri(reverse('feed:post_detail', args=[post_id]))
    return JsonResponse({'success': True, 'url': post_url})

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('user__profile').prefetch_related(
            'likes', 'comments',
            Prefetch('attachments', queryset=PostAttachment.objects.prefetch_related('pages'))
        ),
        id=post_id
    )
    comments = post.comments.select_related('user__profile').all()
    
    return render(request, 'feed/post_detail.html', {
        'post': post,
        'comments': comments
    })


@login_required
def like_repost(request, repost_id):
    repost = get_object_or_404(Repost, id=repost_id)
    if request.user in repost.likes.all():
        repost.likes.remove(request.user)
        is_liked = False
    else:
        repost.likes.add(request.user)
        is_liked = True
    return JsonResponse({'likes_count': repost.likes.count(), 'is_liked': is_liked})


@login_required
def add_repost_comment(request, repost_id):
    if request.method == 'POST':
        repost = get_object_or_404(Repost, id=repost_id)
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')

        if content:
            kwargs = {'repost': repost, 'user': request.user, 'content': content}
            if parent_id:
                parent = get_object_or_404(Comment, id=parent_id, repost=repost)
                kwargs['parent'] = parent
            comment = Comment.objects.create(**kwargs)
            avatar_url = None
            if comment.user.profile.avatar:
                avatar_url = comment.user.profile.avatar.url
            return JsonResponse({
                'success': True,
                'comment': {
                    'id': comment.id,
                    'user': comment.user.username,
                    'content': comment.content,
                    'created_at': comment.created_at.strftime('%b %d, %Y at %I:%M %p'),
                    'is_owner': comment.user == request.user,
                    'avatar_url': avatar_url,
                    'parent_id': int(parent_id) if parent_id else None,
                    'total_likes': 0,
                    'is_liked': False
                },
                'comments_count': repost.total_comments()
            })
        else:
            return JsonResponse({'success': False, 'error': 'Comment cannot be empty'}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


@login_required
def get_repost_comments(request, repost_id):
    repost = get_object_or_404(Repost, id=repost_id)
    comments = repost.repost_comments.select_related('user').prefetch_related('likes', 'replies__user', 'replies__likes').all()

    def serialize_comment(c):
        avatar_url = None
        if c.user.profile.avatar:
            avatar_url = c.user.profile.avatar.url
        replies_data = []
        for reply in c.replies.all():
            reply_avatar = None
            if reply.user.profile.avatar:
                reply_avatar = reply.user.profile.avatar.url
            replies_data.append({
                'id': reply.id,
                'user': reply.user.username,
                'content': reply.content,
                'created_at': reply.created_at.strftime('%b %d, %Y at %I:%M %p'),
                'is_owner': reply.user == request.user,
                'avatar_url': reply_avatar,
                'total_likes': reply.total_likes(),
                'is_liked': request.user in reply.likes.all()
            })
        return {
            'id': c.id,
            'user': c.user.username,
            'content': c.content,
            'created_at': c.created_at.strftime('%b %d, %Y at %I:%M %p'),
            'is_owner': c.user == request.user,
            'avatar_url': avatar_url,
            'total_likes': c.total_likes(),
            'is_liked': request.user in c.likes.all(),
            'replies': replies_data,
            'total_replies': c.total_replies()
        }

    comments_data = [serialize_comment(c) for c in comments if c.parent is None]

    return JsonResponse({
        'success': True,
        'comments': comments_data,
        'comments_count': len(comments_data)
    })


@login_required
def repost_detail(request, repost_id):
    repost = get_object_or_404(
        Repost.objects.select_related('user__profile', 'original_post__user__profile').prefetch_related(
            'likes', 'repost_comments', 'original_post__likes', 'original_post__comments',
            Prefetch('original_post__attachments', queryset=PostAttachment.objects.prefetch_related('pages'))
        ),
        id=repost_id
    )
    post = repost.original_post
    comments = post.comments.select_related('user__profile').all()
    return render(request, 'feed/post_detail.html', {
        'post': post,
        'repost': repost,
        'comments': comments
    })


@login_required
def repost_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        repost_type = request.POST.get('repost_type', 'repost')
        content = request.POST.get('content', '').strip().lstrip('|')

        if repost_type not in ['repost', 'repost_thought']:
            return JsonResponse({'success': False, 'error': 'Invalid repost type'}, status=400)

        if repost_type == 'repost_thought' and not content:
            return JsonResponse({'success': False, 'error': 'Content is required for repost with thought'}, status=400)

        repost = Repost.objects.create(
            user=request.user,
            original_post=post,
            content=content if repost_type == 'repost_thought' else None,
            repost_type=repost_type
        )

        return JsonResponse({
            'success': True,
            'repost_count': post.total_reposts(),
            'message': 'Post reposted successfully'
        })

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


@login_required
def delete_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        
        # Check if the user owns the post
        if post.user != request.user:
            return JsonResponse({'success': False, 'error': 'You do not have permission to delete this post'}, status=403)
        
        # Delete attachment files from disk
        for att in post.attachments.all():
            if att.file:
                try:
                    att.file.delete(save=False)
                except Exception:
                    pass
        post.delete()
        
        return JsonResponse({'success': True, 'message': 'Post deleted successfully'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
def get_post_for_edit(request, post_id):
    """Get post data for editing"""
    post = get_object_or_404(Post, id=post_id)
    
    # Check if the user owns the post
    if post.user != request.user:
        return JsonResponse({'success': False, 'error': 'You do not have permission to edit this post'}, status=403)
    
    attachments = [{
        'id': att.id,
        'url': att.file.url,
        'type': att.file_type,
        'name': att.filename(),
        'size': att.file_size(),
        'sort_order': att.sort_order
    } for att in post.attachments.all()]

    return JsonResponse({
        'success': True,
        'post': {
            'id': post.id,
            'content': post.content,
            'image': post.image.url if post.image else None,
            'attachments': attachments
        }
    })

@login_required
def update_post(request, post_id):
    """Update post content and/or image"""
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        
        # Check if the user owns the post
        if post.user != request.user:
            return JsonResponse({'success': False, 'error': 'You do not have permission to edit this post'}, status=403)
        
        # Update content
        content = request.POST.get('content', '').strip()
        if content:
            # Wrap plain text in paragraph tags for consistency
            if not content.startswith('<'):
                content = f'<p>{content}</p>'
            post.content = content
        
        # Handle image removal
        if request.POST.get('remove_image') == 'true':
            if post.image:
                post.image.delete()
                post.image = None
        
        # Handle new image upload
        if 'image' in request.FILES:
            # Delete old image if exists
            if post.image:
                post.image.delete()
            post.image = request.FILES['image']
        
        # Handle attachment removal
        remove_ids = request.POST.get('remove_attachment_ids', '')
        if remove_ids:
            ids = []
            for x in remove_ids.split(','):
                x = x.strip()
                if x.isdigit():
                    ids.append(int(x))
            if ids:
                PostAttachment.objects.filter(id__in=ids, post=post).delete()

        # Handle new attachment uploads
        multiple_files = request.FILES.getlist('attachments')
        if multiple_files:
            try:
                _handle_post_attachments(post, multiple_files)
            except ValidationError as e:
                return JsonResponse({
                    'success': False,
                    'error': '; '.join(e.messages)
                }, status=400)

        post.save()
        
        attachments = [{
            'id': att.id,
            'url': att.file.url,
            'type': att.file_type,
            'name': att.filename(),
            'size': att.file_size(),
            'sort_order': att.sort_order
        } for att in post.attachments.all()]

        return JsonResponse({
            'success': True,
            'message': 'Post updated successfully',
            'post': {
                'id': post.id,
                'content': post.content,
                'image': post.image.url if post.image else None,
                'attachments': attachments
            }
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


@login_required
def delete_repost(request, repost_id):
    if request.method == 'POST':
        repost = get_object_or_404(Repost, id=repost_id)
        if repost.user != request.user:
            return JsonResponse({'success': False, 'error': 'You do not have permission to delete this repost'}, status=403)
        repost.delete()
        return JsonResponse({'success': True, 'message': 'Repost deleted successfully'})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


@login_required
def update_repost(request, repost_id):
    if request.method == 'POST':
        repost = get_object_or_404(Repost, id=repost_id)
        if repost.user != request.user:
            return JsonResponse({'success': False, 'error': 'You do not have permission to edit this repost'}, status=403)
        if repost.repost_type != 'repost_thought':
            return JsonResponse({'success': False, 'error': 'Only reposts with thought can be edited'}, status=400)
        content = request.POST.get('content', '').strip().lstrip('|')
        if not content:
            return JsonResponse({'success': False, 'error': 'Content is required'}, status=400)
        repost.content = content
        repost.save()
        return JsonResponse({'success': True, 'message': 'Repost updated successfully', 'content': repost.content})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
