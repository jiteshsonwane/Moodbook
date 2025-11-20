document.addEventListener('DOMContentLoaded', function() {
    loadPosts();
});

function loadPosts() {
    fetch('/posts', {
        method: 'GET',
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayPosts(data.posts);
        } else {
            console.error('Failed to load posts:', data.message);
        }
    })
    .catch(error => {
        console.error('Error loading posts:', error);
    });
}

function displayPosts(posts, showDelete = false) {
    const feed = document.getElementById('feed');
    feed.innerHTML = '';

    posts.forEach(post => {
        const postElement = createPostElement(post, showDelete);
        feed.appendChild(postElement);
    });
}

function createPostElement(post, showDelete = false) {
    const postDiv = document.createElement('div');
    postDiv.className = 'product-item';

    const postHeader = document.createElement('div');
    postHeader.className = 'post-header';

    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = post.author.charAt(0).toUpperCase();

    const userInfo = document.createElement('div');
    userInfo.className = 'user-info';

    const authorName = document.createElement('h3');
    authorName.textContent = post.author;

    const timestamp = document.createElement('span');
    timestamp.textContent = new Date(post.created_at).toLocaleTimeString();

    userInfo.appendChild(authorName);
    userInfo.appendChild(timestamp);

    postHeader.appendChild(avatar);
    postHeader.appendChild(userInfo);

    const postContent = document.createElement('div');
    postContent.className = 'post-content';

    const title = document.createElement('h4');
    title.textContent = post.title;

    const content = document.createElement('p');
    content.textContent = post.content;

    postContent.appendChild(title);
    postContent.appendChild(content);

    const postFooter = document.createElement('div');
    postFooter.className = 'post-footer';

    const likeBtn = document.createElement('button');
    likeBtn.className = 'action-btn like-btn';
    likeBtn.textContent = post.user_liked ? '❤️' : '👍';
    likeBtn.onclick = () => toggleLike(post.id, likeBtn);

    const commentBtn = document.createElement('button');
    commentBtn.className = 'action-btn comment-btn';
    commentBtn.textContent = '💬';
    commentBtn.onclick = () => showComments(post.id, postFooter);

    const stats = document.createElement('span');
    stats.className = 'stats';
    stats.textContent = `${post.likes_count} Likes • ${post.comments_count} Comments`;

    postFooter.appendChild(likeBtn);
    postFooter.appendChild(commentBtn);
    postFooter.appendChild(stats);

    if (showDelete) {
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-btn';
        deleteBtn.textContent = '🗑️';
        deleteBtn.onclick = () => deletePost(post.id);
        postFooter.appendChild(deleteBtn);
    }

    postDiv.appendChild(postHeader);
    postDiv.appendChild(postContent);
    postDiv.appendChild(postFooter);

    return postDiv;
}

function toggleLike(postId, button) {
    fetch(`/like/${postId}`, {
        method: 'POST',
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            button.textContent = data.action === 'liked' ? '❤️' : '👍';
            loadPosts(); // Reload to update counts
        } else {
            alert('Failed to like/unlike post: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error toggling like:', error);
    });
}

function showComments(postId, postFooter) {
    // Remove existing comments section if present
    const existingComments = postFooter.querySelector('.comments-section');
    if (existingComments) {
        existingComments.remove();
        return;
    }

    const commentsSection = document.createElement('div');
    commentsSection.className = 'comments-section';

    // Load comments
    fetch(`/comments/${postId}`, {
        method: 'GET',
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const commentsList = document.createElement('div');
            commentsList.className = 'comments-list';

            data.comments.forEach(comment => {
                const commentDiv = document.createElement('div');
                commentDiv.className = 'comment';

                const commentAuthor = document.createElement('strong');
                commentAuthor.textContent = comment.author + ': ';

                const commentContent = document.createElement('span');
                commentContent.textContent = comment.content;

                const commentTime = document.createElement('small');
                commentTime.textContent = ' ' + new Date(comment.created_at).toLocaleString();

                commentDiv.appendChild(commentAuthor);
                commentDiv.appendChild(commentContent);
                commentDiv.appendChild(commentTime);

                commentsList.appendChild(commentDiv);
            });

            const commentForm = document.createElement('div');
            commentForm.className = 'comment-form';

            const commentInput = document.createElement('input');
            commentInput.type = 'text';
            commentInput.placeholder = 'Write a comment...';
            commentInput.className = 'comment-input';

            const commentSubmit = document.createElement('button');
            commentSubmit.textContent = 'Post';
            commentSubmit.className = 'comment-submit';
            commentSubmit.onclick = () => addComment(postId, commentInput.value, commentsList);

            commentForm.appendChild(commentInput);
            commentForm.appendChild(commentSubmit);

            commentsSection.appendChild(commentsList);
            commentsSection.appendChild(commentForm);

            postFooter.appendChild(commentsSection);
        } else {
            console.error('Failed to load comments:', data.message);
        }
    })
    .catch(error => {
        console.error('Error loading comments:', error);
    });
}

function addComment(postId, content, commentsList) {
    if (!content.trim()) {
        alert('Comment cannot be empty');
        return;
    }

    fetch('/comment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
            post_id: postId,
            content: content
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Reload comments
            fetch(`/comments/${postId}`, {
                method: 'GET',
                credentials: 'include'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    commentsList.innerHTML = '';
                    data.comments.forEach(comment => {
                        const commentDiv = document.createElement('div');
                        commentDiv.className = 'comment';

                        const commentAuthor = document.createElement('strong');
                        commentAuthor.textContent = comment.author + ': ';

                        const commentContent = document.createElement('span');
                        commentContent.textContent = comment.content;

                        const commentTime = document.createElement('small');
                        commentTime.textContent = ' ' + new Date(comment.created_at).toLocaleString();

                        commentDiv.appendChild(commentAuthor);
                        commentDiv.appendChild(commentContent);
                        commentDiv.appendChild(commentTime);

                        commentsList.appendChild(commentDiv);
                    });
                }
            });
            loadPosts(); // Reload to update comment count
        } else {
            alert('Failed to add comment: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error adding comment:', error);
    });
}

function deletePost(postId) {
    if (confirm('Are you sure you want to delete this post?')) {
        fetch(`/delete_post/${postId}`, {
            method: 'DELETE',
            credentials: 'include'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Post deleted successfully');
                loadUserPosts(); // Reload user posts
            } else {
                alert('Failed to delete post: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error deleting post:', error);
        });
    }
}

function logout() {
    fetch('/logout', {
        method: 'POST',
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = 'login.html';
        } else {
            alert('Failed to logout: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error logging out:', error);
    });
}
