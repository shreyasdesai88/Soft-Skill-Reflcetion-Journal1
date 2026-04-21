from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
import sqlite3
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
bcrypt = Bcrypt(app)

# Database configuration
DATABASE = 'database.db'

def get_db():
    """Create a database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

def init_db():
    """Initialize the database with tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Entries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            mood TEXT NOT NULL,
            skills TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    #  Weekly Entries Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            summary TEXT NOT NULL,
            score INTEGER NOT NULL CHECK(score >= 1 AND score <= 10),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create Goals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            goal_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def login_required(f):
    """Decorator to protect routes - user must be logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in, else to login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')
        
        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Insert user into database
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                (name, email, hashed_password)
            )
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered. Please use a different email.', 'danger')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('login.html')
        
        # Find user in database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        # Verify password
        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Log out the user"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor()

    # Daily data
    cursor.execute('''
        SELECT DATE(created_at) as date, COUNT(*) as count
        FROM entries
        WHERE user_id = ?
        GROUP BY DATE(created_at)
    ''', (session['user_id'],))
    daily_data = [dict(row) for row in cursor.fetchall()]

    # Weekly data
    cursor.execute('''
        SELECT DATE(created_at) as date, score
        FROM weekly_entries
        WHERE user_id = ?
    ''', (session['user_id'],))
    weekly_data = [dict(row) for row in cursor.fetchall()]

    # Monthly data
    cursor.execute('''
        SELECT strftime('%m', created_at) as month, COUNT(*) as count
        FROM entries
        WHERE user_id = ?
        GROUP BY month
    ''', (session['user_id'],))
    monthly_data = [dict(row) for row in cursor.fetchall()]

    # Weekly entries (cards)
    cursor.execute('''
        SELECT * FROM weekly_entries
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (session['user_id'],))
    weekly_entries = cursor.fetchall()  # no need to convert

    conn.close()

    return render_template(
        'dashboard.html',
        daily_data=daily_data,
        weekly_data=weekly_data,
        monthly_data=monthly_data,
        entries=weekly_entries
    )

@app.route('/new-entry', methods=['GET', 'POST'])
@login_required
def new_entry():
    """Create a new journal entry"""
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        mood = request.form.get('mood', '')
        skills = request.form.getlist('skills')  # Get multiple checkbox values
        
        if not content or not mood:
            flash('Please provide your reflection and select a mood.', 'warning')
            return render_template('new_entry.html')
        
        # Convert skills list to comma-separated string
        skills_str = ', '.join(skills) if skills else 'None'
        
        # Insert entry into database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO entries (user_id, content, mood, skills) VALUES (?, ?, ?, ?)',
            (session['user_id'], content, mood, skills_str)
        )
        conn.commit()
        conn.close()
        
        flash('Journal entry added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('new_entry.html')

@app.route('/weekly-entry', methods=['GET', 'POST'])
@login_required
def weekly_entry():
    if request.method == 'POST':
        summary = request.form.get('summary', '').strip()
        score = request.form.get('score', '')

        if not summary:
            flash('Please fill in the summary.', 'warning')
            return render_template('weekly_entry.html')
        
        if not score:
            flash('Please select a score.', 'warning')
            return render_template('weekly_entry.html')
        
        try:
            score_int = int(score)
            if score_int < 1 or score_int > 10:
                flash('Score must be between 1 and 10.', 'warning')
                return render_template('weekly_entry.html')
        except ValueError:
            flash('Invalid score value.', 'warning')
            return render_template('weekly_entry.html')

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                'INSERT INTO weekly_entries (user_id, summary, score) VALUES (?, ?, ?)',
                (session['user_id'], summary, score_int)
            )
            conn.commit()
            flash('Weekly entry added successfully!', 'success')
        except Exception as e:
            flash(f'Error saving entry: {str(e)}', 'danger')
        finally:
            conn.close()

        return redirect(url_for('dashboard'))

    return render_template('weekly_entry.html')

@app.route('/daily-entries')
@login_required
def daily_entries():
    """Display all daily entries for the logged-in user"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all daily entries for the user, ordered by most recent first
    cursor.execute('''
        SELECT * FROM entries
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (session['user_id'],))
    entries = cursor.fetchall()
    
    conn.close()
    
    return render_template('daily_entries.html', entries=entries)

@app.route('/edit-entry/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def edit_entry(entry_id):
    """Edit a daily entry"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Verify entry belongs to current user
    cursor.execute('SELECT * FROM entries WHERE id = ? AND user_id = ?', (entry_id, session['user_id']))
    entry = cursor.fetchone()
    
    if not entry:
        flash('Entry not found or you do not have permission to edit it.', 'danger')
        return redirect(url_for('daily_entries'))
    
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        mood = request.form.get('mood', '')
        skills = request.form.getlist('skills')
        
        if not content or not mood:
            flash('Please provide your reflection and select a mood.', 'warning')
            return render_template('edit_entry.html', entry=entry)
        
        skills_str = ', '.join(skills) if skills else 'None'
        
        cursor.execute(
            'UPDATE entries SET content = ?, mood = ?, skills = ? WHERE id = ?',
            (content, mood, skills_str, entry_id)
        )
        conn.commit()
        conn.close()
        
        flash('Journal entry updated successfully!', 'success')
        return redirect(url_for('daily_entries'))
    
    conn.close()
    return render_template('edit_entry.html', entry=entry)

@app.route('/delete-entry/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    """Delete a daily entry"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Verify entry belongs to current user
    cursor.execute('SELECT * FROM entries WHERE id = ? AND user_id = ?', (entry_id, session['user_id']))
    entry = cursor.fetchone()
    
    if not entry:
        flash('Entry not found or you do not have permission to delete it.', 'danger')
        return redirect(url_for('daily_entries'))
    
    cursor.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
    conn.commit()
    conn.close()
    
    flash('Journal entry deleted successfully!', 'success')
    return redirect(url_for('daily_entries'))

@app.route('/edit-weekly/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def edit_weekly(entry_id):
    """Edit a weekly entry"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Verify entry belongs to current user
    cursor.execute('SELECT * FROM weekly_entries WHERE id = ? AND user_id = ?', (entry_id, session['user_id']))
    entry = cursor.fetchone()
    
    if not entry:
        flash('Entry not found or you do not have permission to edit it.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        summary = request.form.get('summary', '').strip()
        score = request.form.get('score', '')
        
        if not summary:
            flash('Please fill in the summary.', 'warning')
            return render_template('edit_weekly.html', entry=entry)
        
        if not score:
            flash('Please select a score.', 'warning')
            return render_template('edit_weekly.html', entry=entry)
        
        try:
            score_int = int(score)
            if score_int < 1 or score_int > 10:
                flash('Score must be between 1 and 10.', 'warning')
                return render_template('edit_weekly.html', entry=entry)
        except ValueError:
            flash('Invalid score value.', 'warning')
            return render_template('edit_weekly.html', entry=entry)
        
        cursor.execute(
            'UPDATE weekly_entries SET summary = ?, score = ? WHERE id = ?',
            (summary, score_int, entry_id)
        )
        conn.commit()
        conn.close()
        
        flash('Weekly entry updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    conn.close()
    return render_template('edit_weekly.html', entry=entry)

@app.route('/delete-weekly/<int:entry_id>', methods=['POST'])
@login_required
def delete_weekly(entry_id):
    """Delete a weekly entry"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Verify entry belongs to current user
    cursor.execute('SELECT * FROM weekly_entries WHERE id = ? AND user_id = ?', (entry_id, session['user_id']))
    entry = cursor.fetchone()
    
    if not entry:
        flash('Entry not found or you do not have permission to delete it.', 'danger')
        return redirect(url_for('dashboard'))
    
    cursor.execute('DELETE FROM weekly_entries WHERE id = ?', (entry_id,))
    conn.commit()
    conn.close()
    
    flash('Weekly entry deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get user details
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    
    # Get entry count
    cursor.execute('SELECT COUNT(*) as count FROM entries WHERE user_id = ?', (session['user_id'],))
    entry_count = cursor.fetchone()['count']
    
    # Get goal count
    cursor.execute('SELECT COUNT(*) as count FROM goals WHERE user_id = ?', (session['user_id'],))
    goal_count = cursor.fetchone()['count']
    
    conn.close()
    
    return render_template('profile.html', user=user, entry_count=entry_count, goal_count=goal_count)

@app.route('/goals', methods=['GET', 'POST'])
@login_required
def goals():
    """Goals page - add and view goals"""
    if request.method == 'POST':
        goal_text = request.form.get('goal_text', '').strip()
        
        if not goal_text:
            flash('Please enter a goal.', 'warning')
            return redirect(url_for('goals'))
        
        # Insert goal into database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO goals (user_id, goal_text) VALUES (?, ?)',
            (session['user_id'], goal_text)
        )
        conn.commit()
        conn.close()
        
        flash('Goal added successfully!', 'success')
        return redirect(url_for('goals'))
    
    # Get all goals for the user
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM goals WHERE user_id = ? ORDER BY created_at DESC',
        (session['user_id'],)
    )
    user_goals = cursor.fetchall()
    conn.close()
    
    return render_template('goals.html', goals=user_goals)

if __name__ == '__main__':
    # Initialize database on first run
    init_db()
    
    # Create a sample test user for easy testing
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', ('test@example.com',))
    test_user = cursor.fetchone()
    
    if not test_user:
        hashed_pw = bcrypt.generate_password_hash('test123').decode('utf-8')
        cursor.execute(
            'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
            ('Test User', 'test@example.com', hashed_pw)
        )
        conn.commit()
        print("Sample test user created: test@example.com / test123")
    
    conn.close()
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5050)

