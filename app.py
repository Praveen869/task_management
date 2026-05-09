import re
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_socketio import SocketIO, emit
# pyrefly: ignore [missing-import]
from flask_bcrypt import Bcrypt
from models import get_db_connection, create_tables
from analytics import get_analytics
from config import Config

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
bcrypt = Bcrypt(app)
socketio = SocketIO(app, cors_allowed_origins='*')

# =====================
# AUTH ROUTES
# =====================

@app.route('/')
def home():
    """Redirects the user to the dashboard if logged in, otherwise to the login page."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles new user registration via HTML form or JSON API."""
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
            
        username = data.get('username', '')
        email = data.get('email', '')
        raw_password = data.get('password', '')
        
        # Validation
        if len(username) < 3:
            error_msg = 'Username must be at least 3 characters long.'
            if request.is_json: return jsonify({'error': error_msg}), 400
            flash(error_msg, 'danger')
            return render_template('register.html')
            
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            error_msg = 'Invalid email format.'
            if request.is_json: return jsonify({'error': error_msg}), 400
            flash(error_msg, 'danger')
            return render_template('register.html')
            
        # Strict Password Validation
        if len(raw_password) < 8:
            error_msg = 'Password must be at least 8 characters long.'
        elif not re.search(r"[A-Z]", raw_password):
            error_msg = 'Password must contain at least one uppercase letter.'
        elif not re.search(r"[a-z]", raw_password):
            error_msg = 'Password must contain at least one lowercase letter.'
        elif not re.search(r"\d", raw_password):
            error_msg = 'Password must contain at least one digit.'
        elif not re.search(r"[!@#$%^&*(),.?\":{}|<>]", raw_password):
            error_msg = 'Password must contain at least one special character.'
        else:
            error_msg = None

        if error_msg:
            if request.is_json: return jsonify({'error': error_msg}), 400
            flash(error_msg, 'danger')
            return render_template('register.html')
            
        password = bcrypt.generate_password_hash(raw_password).decode('utf-8')
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, password)
            )
            conn.commit()
            cur.close()
            conn.close()
            
            if request.is_json:
                return jsonify({'message': 'User registered successfully'}), 201
            return redirect(url_for('login'))
        except Exception as e:
            error_msg = str(e)
            if "users_email_key" in error_msg:
                error_msg = "An account with this email already exists."
            elif "users_username_key" in error_msg:
                error_msg = "This username is already taken."
            else:
                error_msg = "An error occurred during registration. Please try again."

            if request.is_json:
                return jsonify({'error': error_msg}), 400
            flash(error_msg, 'danger')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticates a user and establishes a session."""
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
            
        email = data.get('email')
        password = data.get('password')
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            cur.close()
            conn.close()
            
            if user and bcrypt.check_password_hash(user[3], password):
                session['user_id'] = user[0]
                session['username'] = user[1]
                if request.is_json:
                    return jsonify({'message': 'Login successful'}), 200
                return redirect(url_for('dashboard'))
            else:
                if request.is_json:
                    return jsonify({'error': 'Invalid credentials'}), 401
                flash('Invalid credentials', 'danger')
                return render_template('login.html')
        except Exception as e:
            if request.is_json:
                return jsonify({'error': str(e)}), 400
            flash(str(e), 'danger')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Fetch tasks
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE user_id = %s ORDER BY created_at DESC", (session['user_id'],))
    tasks_raw = cur.fetchall()
    cur.close()
    conn.close()
    
    tasks = []
    for t in tasks_raw:
        tasks.append({
            'id': t[0],
            'title': t[1],
            'description': t[2],
            'priority': t[3],
            'status': t[4],
            'created_at': t[6]
        })
    
    # Fetch analytics
    stats_data = get_analytics(session['user_id'])
    stats = {
        'total': stats_data['total_tasks'],
        'completion_rate': stats_data['completion_percentage'],
        'status_counts': {
            'pending': stats_data['pending_tasks'],
            'completed': stats_data['completed_tasks'],
            'in_progress': stats_data['in_progress_tasks']
        },
        'priority_counts': stats_data.get('priority_breakdown', {}),
        'avg_tasks_per_day': stats_data.get('avg_tasks_per_day', 0)
    }
    
    current_user = {'username': session['username']}
    
    return render_template('index.html', current_user=current_user, tasks=tasks, stats=stats)

# =====================
# TASK APIs
# =====================

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE user_id = %s ORDER BY created_at DESC", (session['user_id'],))
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    
    tasks_list = []
    for task in tasks:
        tasks_list.append({
            'id': task[0],
            'title': task[1],
            'description': task[2],
            'priority': task[3],
            'status': task[4],
            'user_id': task[5],
            'created_at': str(task[6])
        })
    
    return jsonify(tasks_list), 200

@app.route('/api/tasks', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    try:
        title = data.get('title')
        description = data.get('description', '')
        priority = data.get('priority', 'medium')
        status = data.get('status', 'pending')
        
        if not title:
            return jsonify({'error': 'Title is required'}), 400
            
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (title, description, priority, status, user_id) VALUES (%s, %s, %s, %s, %s) RETURNING *",
            (title, description, priority, status, session['user_id'])
        )
        task = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        if not task:
            return jsonify({'error': 'Failed to create task'}), 500
            
        new_task = {
            'id': task[0],
            'title': task[1],
            'description': task[2],
            'priority': task[3],
            'status': task[4],
            'created_at': str(task[6])
        }
        
        # WebSocket se live update bhejo
        socketio.emit('task_added', new_task)
        
        return jsonify(new_task), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    try:
        title = data.get('title')
        description = data.get('description', '')
        priority = data.get('priority', 'medium')
        status = data.get('status', 'pending')
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE tasks SET title=%s, description=%s, priority=%s, status=%s WHERE id=%s AND user_id=%s RETURNING *",
            (title, description, priority, status, task_id, session['user_id'])
        )
        task = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        if not task:
            return jsonify({'error': 'Task not found or unauthorized'}), 404
            
        updated_task = {
            'id': task[0],
            'title': task[1],
            'description': task[2],
            'priority': task[3],
            'status': task[4],
            'created_at': str(task[6])
        }
        
        # WebSocket se live update bhejo
        socketio.emit('task_updated', updated_task)
        
        return jsonify(updated_task), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id=%s AND user_id=%s", (task_id, session['user_id']))
        conn.commit()
        cur.close()
        conn.close()
        
        # WebSocket se live update bhejo
        socketio.emit('task_deleted', {'id': task_id})
        
        return jsonify({'message': 'Task deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# =====================
# ANALYTICS API
# =====================

@app.route('/api/analytics', methods=['GET'])
def analytics():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = get_analytics(session['user_id'])
    return jsonify(data), 200

# =====================
# WEBSOCKET EVENTS
# =====================

@socketio.on('connect')
def handle_connect():
    emit('connected', {'message': 'WebSocket connected!'})

# =====================
# RUN APP
# =====================

if __name__ == '__main__':
    create_tables()
    socketio.run(app, debug=True)