# 📔 Soft Skills Journal

A web application that helps users track and improve their soft skills through daily and weekly journal entries, goal setting, and progress analytics.

## Features

✨ **Core Features:**
- **User Authentication** - Secure registration and login with password encryption (Bcrypt)
- **Daily Entries** - Write and track daily reflections with mood and skill tags
- **Weekly Summary** - Review weeks with numerical scoring (1-10 scale)
- **Goal Management** - Set and track personal development goals
- **Analytics Dashboard** - Visualize progress with stats and trends
- **User Profile** - View account information and activity statistics

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | Python + Flask | Server logic and routing |
| **Database** | SQLite | Data persistence |
| **Frontend** | HTML + Bootstrap | User interface |
| **Styling** | CSS + Bootstrap | Responsive design |
| **Security** | Bcrypt(Hashing) | Password encryption |

## Installation

### Prerequisites
- Python 3.x
- pip (Python package manager)

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd app
   ```

2. **Install dependencies**
   ```bash
   pip install flask flask-bcrypt
   ```

3. **Initialize database with test data**
   ```bash
   python flask_journal/insert_test_data.py
   ```

4. **Run the application**
   
   **Option A - Windows (Easiest):**
   ```bash
   run.bat
   ```
   Or double-click `run.bat` file in the app folder.
   
   **Option B - All Platforms:**
   ```bash
   python flask_journal/app.py
   ```

5. **Access the app**
   - Open your browser and go to `http://localhost:5000`
   - Login with test credentials:
     - Email: `test@example.com`
     - Password: `testpass123`

## Project Structure

```
app/
├── flask_journal/
│   ├── app.py                 # Main Flask application with all routes
│   ├── insert_test_data.py    # Database initialization script
│   ├── static/
│   │   └── style.css          # Custom styling
│   └── templates/
│       ├── base.html          # Base template (navigation, layout)
│       ├── login.html         # Login page
│       ├── register.html      # Registration page
│       ├── dashboard.html     # Analytics dashboard
│       ├── daily_entries.html # View all daily entries
│       ├── new_entry.html     # Create new daily entry
│       ├── edit_entry.html    # Edit daily entry
│       ├── weekly_entry.html  # Create weekly entry
│       ├── edit_weekly.html   # Edit weekly entry
│       ├── goals.html         # Goals management
│       └── profile.html       # User profile
├── database.db                # SQLite database (auto-created)
└── package.json               # Project metadata
```

## Database Schema

### Users Table
- `id` - Unique identifier
- `name` - User's full name
- `email` - Email address (unique)
- `password` - Encrypted password (Bcrypt)
- `created_at` - Registration timestamp

### Daily Entries Table
- `id` - Entry identifier
- `user_id` - User who wrote the entry
- `content` - Journal reflection text
- `mood` - Selected mood (Happy, Sad, Neutral, Excited, Calm)
- `skills` - Skills practiced (comma-separated)
- `created_at` - Creation timestamp

### Weekly Entries Table
- `id` - Entry identifier
- `user_id` - User who wrote the entry
- `summary` - Week summary text
- `score` - Weekly rating (1-10)
- `created_at` - Creation timestamp

### Goals Table
- `id` - Goal identifier
- `user_id` - User's goal
- `goal_text` - Goal description
- `created_at` - Creation timestamp

## Security Features

🔒 **Implementation:**
- **Password Encryption** - Uses Bcrypt for one-way password hashing
- **User Isolation** - Users can only access their own data
- **Session Management** - Login required for protected routes
- **Input Validation** - All form inputs validated before processing
- **SQL Injection Prevention** - Parameterized queries used throughout

## Usage Guide

### 1. Create an Account
- Click "Register" on the login page
- Enter name, email, and password
- Password must be at least 6 characters

### 2. Add Daily Entry
- Click "New Entry" from navigation
- Write your reflection
- Select mood and skills
- Click "Save"

### 3. Add Weekly Summary
- Click "Weekly Entry"
- Write week summary
- Rate week (1-10)
- Click "Save"

### 4. Set Goals
- Go to "Goals" section
- Click "Add Goal"
- Type goal and save

### 5. View Progress
- Visit "Dashboard" to see:
  - Total entries written
  - Average weekly score
  - Weekly statistics
  - Recent entries and scores

## How It Works

### User Flow Example

```
1. User registers → Password encrypted & stored
2. User logs in → Session created for user
3. User writes entry → Data validated & saved to database
4. Dashboard loads → Queries calculate statistics
5. User logs out → Session cleared
```

### Request/Response Cycle

```
Browser Request
    ↓
Flask (Validate + Process)
    ↓
SQLite Database
    ↓
Flask (Prepare HTML)
    ↓
Browser Response
```

## Learning Outcomes

This project demonstrates:

✓ Full-stack web development (frontend + backend + database)
✓ User authentication and password security
✓ Database design and relationships
✓ RESTful routing and CRUD operations
✓ Session management and user state
✓ Input validation and error handling
✓ Responsive web design
✓ Web application architecture

## Future Enhancements

Possible features for future versions:
- Advanced charts and analytics
- PDF export functionality
- Email reminders
- Mobile-optimized version
- Social sharing features
- Search and filtering
- Multi-language support

## License

This project was created for educational purposes.

## Shreyas Desai 

Created as a college project demonstrating full-stack web development skills.

---

## Problems Faced 
Handling backend flow and connectivity

