# Moodbook

## Overview
Moodbook is a web-based social media application built with Flask (Python) for the backend and vanilla HTML/CSS/JavaScript for the frontend. It allows users to register, log in, create posts, like and comment on posts, and manage their profiles. The app emphasizes a dark, modern UI with animations and a focus on user interaction in a "mood-sharing" community.

## Architecture
- **Backend**: Flask web framework with RESTful API endpoints.
- **Database**: MySQL for data persistence, with tables for users, posts, likes, and comments.
- **Frontend**: Static HTML pages served by Flask, styled with CSS, and interactive via JavaScript (fetch API for AJAX calls).
- **Authentication**: Session-based with CORS enabled for cross-origin requests.
- **Security**: Password hashing using SHA-256, login-required decorators for protected routes.

## Key Features
1. **User Management**:
   - Registration with name, email, and password.
   - Login/logout with session management.
   - Password confirmation on registration.

2. **Post Management**:
   - Create posts with title and content.
   - View all posts on the home page, sorted by creation date.
   - Like/unlike posts (toggle functionality).
   - Add comments to posts.
   - Delete own posts from profile page.

3. **Profile Page**:
   - View user's own posts.
   - Delete posts directly from the profile.

4. **UI/UX**:
   - Dark theme with neon green/blue accents.
   - Responsive design with animations (fade-in, slide effects).
   - Dynamic loading of posts, likes, and comments via JavaScript.
   - Navigation between pages (home, create post, profile).

## File Structure
- `app.py`: Main Flask application with all routes and logic.
- `config.py`: Database configuration and table creation SQL.
- `requirements.txt`: Python dependencies (Flask, Flask-CORS, MySQL connector).
- `home.html`: Main feed page with welcome section and post list.
- `login.html`: Login form.
- `register.html`: Registration form.
- `create_post.html`: Form to create new posts.
- `profile.html`: User profile with personal posts.
- `styles.css`: Comprehensive CSS for styling and animations.
- `script.js`: JavaScript for dynamic interactions (loading posts, liking, commenting, etc.).

## Database Schema
- **registered_users**: id, fullname, email, password, created_at.
- **posts**: id, user_id, title, content, created_at.
- **likes**: id, user_id, post_id, created_at (unique constraint on user-post pairs).
- **comments**: id, user_id, post_id, content, created_at.

## API Endpoints
- `POST /register`: Register new user.
- `POST /login`: Authenticate user.
- `POST /logout`: End session.
- `POST /create_post`: Create new post (requires login).
- `GET /posts`: Fetch all posts with likes/comments counts.
- `POST /like/<post_id>`: Like/unlike a post.
- `POST /comment`: Add comment to post.
- `GET /comments/<post_id>`: Fetch comments for a post.
- `GET /api/profile`: Fetch user's posts.
- `DELETE /delete_post/<post_id>`: Delete user's post.
- Static file serving for HTML/CSS/JS.

## Technologies Used
- **Python**: Flask for web server and API.
- **MySQL**: Relational database.
- **HTML/CSS/JS**: Frontend without frameworks.
- **Hashlib**: For password hashing.
- **OS**: For session secret key generation.

## Setup and Deployment
1. Install dependencies: `pip install -r requirements.txt`.
2. Configure MySQL in `config.py` (host, user, password, database).
3. Run `app.py` to start the server (debug mode enabled).
4. Access via browser at `http://localhost:5000` (redirects to login.html).

## Recent Changes
- Removed user count, posts count, and likes count from the home page welcome section to simplify the UI.

This project demonstrates a full-stack web application with user authentication, CRUD operations, and interactive features, suitable for a small-scale social platform.
