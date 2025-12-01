from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import hashlib
import os
from functools import wraps

from config import DB_CONFIG, CREATE_TABLES_SQL

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True)


def init_db():
    """
    Create the database (if it doesn't exist) and then create all tables.
    This runs once on startup.
    """
    try:
        # Connect WITHOUT specifying database first
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()

        # Create database if needed and use it
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")

        # Create tables
        for sql in CREATE_TABLES_SQL:
            cursor.execute(sql)

        conn.commit()
        print("Database and tables initialized successfully")
    except Error as e:
        print(f"Error during DB init: {e}")
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass


def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return wrapper


# ✅ Initialize DB (database + tables) on startup
init_db()


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not all([name, email, password]):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    hashed_password = hash_password(password)

    connection = get_db_connection()
    if connection is None:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()
        # Check if user already exists
        cursor.execute("SELECT id FROM registered_users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': 'User already exists'}), 409

        # Insert new user
        cursor.execute(
            "INSERT INTO registered_users (fullname, email, password) VALUES (%s, %s, %s)",
            (name, email, hashed_password)
        )
        connection.commit()
        return jsonify({'success': True, 'message': 'User registered successfully'}), 201
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'success': False, 'message': 'Registration failed'}), 500
    finally:
        if connection:
            connection.close()


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({'success': False, 'message': 'Email and password are required'}), 400

    hashed_password = hash_password(password)

    connection = get_db_connection()
    if connection is None:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, fullname FROM registered_users WHERE email = %s AND password = %s",
            (email, hashed_password)
        )
        user = cursor.fetchone()
        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {'id': user[0], 'name': user[1]}
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'success': False, 'message': 'Login failed'}), 500
    finally:
        if connection:
            connection.close()


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200


@app.route('/create_post', methods=['POST'])
@login_required
def create_post():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not all([title, content]):
        return jsonify({'success': False, 'message': 'Title and content are required'}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO posts (user_id, title, content) VALUES (%s, %s, %s)",
            (session['user_id'], title, content)
        )
        connection.commit()
        return jsonify({'success': True, 'message': 'Post created successfully'}), 201
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'success': False, 'message': 'Failed to create post'}), 500
    finally:
        if connection:
            connection.close()


@app.route('/posts', methods=['GET'])
def get_posts():
    connection = get_db_connection()
    if connection is None:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.id, p.title, p.content, p.created_at, u.fullname as author,
                   COUNT(DISTINCT l.id) as likes_count,
                   COUNT(DISTINCT c.id) as comments_count
            FROM posts p
            JOIN registered_users u ON p.user_id = u.id
            LEFT JOIN likes l ON p.id = l.post_id
            LEFT JOIN comments c ON p.id = c.post_id
            GROUP BY p.id, p.title, p.content, p.created_at, u.fullname
            ORDER BY p.created_at DESC
        """)
        posts = cursor.fetchall()

        # Check if user is logged in and get their likes
        user_likes = []
        if 'user_id' in session:
            cursor.execute("SELECT post_id FROM likes WHERE user_id = %s", (session['user_id'],))
            user_likes = [row['post_id'] for row in cursor.fetchall()]

        for post in posts:
            post['user_liked'] = post['id'] in user_likes

        return jsonify({'success': True, 'posts': posts}), 200
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch posts'}), 500
    finally:
        if connection:
            connection.close()


@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    connection = get_db_connection()
    if connection is None:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()
        # Check if like already exists
        cursor.execute(
            "SELECT id FROM likes WHERE user_id = %s AND post_id = %s",
            (session['user_id'], post_id)
        )
        existing_like = cursor.fetchone()

        if existing_like:
            # Unlike
            cursor.execute(
                "DELETE FROM likes WHERE user_id = %s AND post_id = %s",
                (session['user_id'], post_id)
            )
            action = 'unliked'
        else:
            # Like
            cursor.execute(
                "INSERT INTO likes (user_id, post_id) VALUES (%s, %s)",
                (session['user_id'], post_id)
            )
            action = 'liked'

        connection.commit()
        return jsonify({
            'success': True,
            'message': f'Post {action} successfully',
            'action': action
        }), 200
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'success': False, 'message': 'Failed to like/unlike post'}), 500
    finally:
        if connection:
            connection.close()


@app.route('/comment', methods=['POST'])
@login_required
def add_comment():
    data = request.get_json()
    post_id = data.get('post_id')
    content = data.get('content')

    if not all([post_id, content]):
        return jsonify({'success': False, 'message': 'Post ID and content are required'}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO comments (user_id, post_id, content) VALUES (%s, %s, %s)",
            (session['user_id'], post_id, content)
        )
        connection.commit()
        return jsonify({'success': True, 'message': 'Comment added successfully'}), 201
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'success': False, 'message': 'Failed to add comment'}), 500
    finally:
        if connection:
            connection.close()


@app.route('/comments/<int:post_id>', methods=['GET'])
def get_comments(post_id):
    connection = get_db_connection()
    if connection is None:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.id, c.content, c.created_at, u.fullname as author
            FROM comments c
            JOIN registered_users u ON c.user_id = u.id
            WHERE c.post_id = %s
            ORDER BY c.created_at ASC
        """, (post_id,))
        comments = cursor.fetchall()
        return jsonify({'success': True, 'comments': comments}), 200
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch comments'}), 500
    finally:
        if connection:
            connection.close()


@app.route('/api/profile', methods=['GET'])
@login_required
def get_user_posts():
    connection = get_db_connection()
    if connection is None:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.id, p.title, p.content, p.created_at, u.fullname as author, p.user_id,
                   COUNT(DISTINCT l.id) as likes_count,
                   COUNT(DISTINCT c.id) as comments_count
            FROM posts p
            JOIN registered_users u ON p.user_id = u.id
            LEFT JOIN likes l ON p.id = l.post_id
            LEFT JOIN comments c ON p.id = c.post_id
            WHERE p.user_id = %s
            GROUP BY p.id, p.title, p.content, p.created_at, u.fullname, p.user_id
            ORDER BY p.created_at DESC
        """, (session['user_id'],))
        posts = cursor.fetchall()

        cursor.execute("SELECT post_id FROM likes WHERE user_id = %s", (session['user_id'],))
        user_likes = [row['post_id'] for row in cursor.fetchall()]

        for post in posts:
            post['user_liked'] = post['id'] in user_likes

        return jsonify({'success': True, 'posts': posts}), 200
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'success': False, 'message': 'Failed to fetch user posts'}), 500
    finally:
        if connection:
            connection.close()


@app.route('/delete_post/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    connection = get_db_connection()
    if connection is None:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()

        cursor.execute("SELECT user_id FROM posts WHERE id = %s", (post_id,))
        post = cursor.fetchone()
        if not post or post[0] != session['user_id']:
            return jsonify({'success': False, 'message': 'Unauthorized or post not found'}), 403

        cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))
        connection.commit()
        return jsonify({'success': True, 'message': 'Post deleted successfully'}), 200
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({'success': False, 'message': 'Failed to delete post'}), 500
    finally:
        if connection:
            connection.close()


@app.route('/')
def index():
    return send_from_directory('static', 'login.html')


@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


@app.route('/profile')
def profile_page():
    return send_from_directory('static', 'profile.html')


if __name__ == '__main__':
    app.run(debug=True)
