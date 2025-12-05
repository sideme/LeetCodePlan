# LeetCode 30-Day Study Plan System

A comprehensive web-based LeetCode study plan system that helps you systematically complete 150 high-frequency interview questions (NeetCode 150) and reach interview level in 30 days.

## ✨ Features

- 🌐 **Modern Web Interface**: Beautiful, responsive UI accessible from any device
- 📊 **SQLite Database**: Persistent data storage with automatic initialization
- 🐳 **Docker Support**: One-click deployment with Docker Compose
- 📅 **Scientific 30-Day Plan**: Progressive learning path covering all major algorithm topics
- ✅ **Progress Tracking**: Real-time completion status, accuracy rate, and streak tracking
- 🔄 **Smart Review System**: Automatic review reminders based on Ebbinghaus forgetting curve
- 📝 **Note Taking**: Add personal notes and solution approaches for each problem
- 📈 **Comprehensive Statistics**: Detailed analytics by category, difficulty, and completion status
- 🎯 **Daily Tasks**: Automatically carries over incomplete tasks to the next day
- 📚 **Review Integration**: Review questions automatically integrated into daily evening sessions

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose (for Docker method)
- Python 3.7+ (for local method)

### Method 1: Docker (Recommended)

1. **Start the system**
   ```bash
   ./start.sh
   ```
   
   The script will:
   - Check Docker status
   - Stop any existing containers
   - Build and start the application
   - Find an available port (starting from 5001)

2. **Access the system**
   
   Open your browser and visit: **http://localhost:5001**
   
   ⚠️ **Note**: The default port is 5001 (not 5000) to avoid conflicts with macOS ControlCenter.
   
   To check the actual port and system status:
   ```bash
   ./check-status.sh
   ```

3. **Stop the system**
   ```bash
   ./stop.sh
   ```

### Method 2: Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**
   ```bash
   python app.py
   ```
   
   Or use the provided script:
   ```bash
   ./run-local.sh
   ```

3. **Access the system**
   
   Open your browser and visit: **http://localhost:5000**

## 📚 30-Day Study Plan Overview

The system follows a scientifically designed 30-day curriculum:

### Days 1-5: Basic Data Structures
- **Days 1-2**: Arrays & Hash Tables
- **Days 3-4**: Two Pointers
- **Day 5**: Sliding Window

### Days 6-10: Stack & Linked List
- **Days 6-7**: Stack
- **Days 8-10**: Linked List

### Days 11-15: Trees & Search
- **Days 11-13**: Trees (DFS, BFS, BST)
- **Day 14**: Binary Search
- **Day 15**: Heap & Priority Queue

### Days 16-20: Graph & Backtracking
- **Days 16-17**: Graph (DFS, BFS, Topological Sort)
- **Days 18-19**: Backtracking
- **Day 20**: Trie & String Problems

### Days 21-25: Dynamic Programming & Greedy
- **Days 21-23**: Dynamic Programming (1D, 2D, Knapsack)
- **Day 24**: Advanced Dynamic Programming
- **Day 25**: Greedy Algorithms

### Days 26-30: Comprehensive Review
- **Day 26**: Interval Problems
- **Days 27-28**: Design Problems
- **Days 29-30**: Comprehensive Review & Hard Problems

## 🎯 Study Methodology

### Three-Session Daily Structure

Each day is divided into three focused learning sessions:

1. **🔴 Golden Hour (Morning - 3 hours)**
   - Tackle the most difficult problems of the day
   - 25-30 minutes of deep thinking per problem
   - Watch video explanations when stuck (NeetCode recommended)
   - Organize problem-solving templates

2. **🟡 Silver Hour (Afternoon - 2-3 hours)**
   - Practice medium-difficulty variations
   - Complete within 20 minutes per problem
   - Think about connections with morning problems

3. **🟢 Bronze Hour (Evening - 1-1.5 hours)**
   - Review problems based on Ebbinghaus forgetting curve
   - Whiteboard coding (without IDE autocomplete)
   - Explain your approach (Feynman Technique)

### Review System

The system automatically schedules reviews based on the Ebbinghaus forgetting curve:
- **1 day later**: First review
- **3 days later**: Second review
- **7 days later**: Third review
- **14 days later**: Fourth review

Problems you got wrong are prioritized in the review queue.

## 📖 User Guide

### Viewing Your Study Plan

1. The left sidebar displays 30 day buttons with actual dates
2. Click any day to view that day's study plan
3. Each plan shows three sessions: morning, afternoon, and evening
4. Incomplete tasks from previous days automatically appear in the morning session
5. Review questions automatically appear in the evening session

### Marking Progress

1. After completing a problem, click the **"Complete"** button
2. If you got it wrong, click the **"Wrong"** button
3. For review questions, click **"Review Complete"** after reviewing
4. The system automatically updates statistics and progress

### Taking Notes

1. Click the note icon (📝 or 📄) next to any problem title
2. Write your solution approach, key insights, or reminders
3. Click **"Save Note"** to save
4. Notes are preserved for future reference during reviews

### Viewing Statistics

1. Click the **"Statistics"** button in the sidebar
2. View comprehensive statistics including:
   - Total progress (completed/total)
   - Accuracy rate
   - Distribution by category
   - Distribution by difficulty
   - Streak days

### Review Management

1. Click the **"Review"** button to view all problems needing review
2. Review questions are automatically integrated into daily evening sessions
3. Completed review questions stay visible with a "✓ Review Completed" badge

### Deferring Problems

1. Click the **"⏰ Later"** button to mark a problem as "Do Later"
2. Deferred problems are hidden from the daily plan
3. Click **"Do Later"** in the sidebar to view and restore deferred problems

## 🗂️ Project Structure

```
LeetCodePlan/
├── app.py                 # Flask backend application
├── questions.json         # Question data (NeetCode 150)
├── templates/             # HTML templates
│   └── index.html         # Main UI template
├── static/               # Static resources
│   ├── css/
│   │   └── style.css     # Stylesheet
│   └── js/
│       └── app.js        # Frontend JavaScript
├── data/                 # Data directory (auto-created)
│   └── leetcode_plan.db  # SQLite database
├── Dockerfile            # Docker image configuration
├── docker-compose.yml    # Docker Compose configuration
├── requirements.txt      # Python dependencies
├── start.sh             # Start script (Docker)
├── stop.sh              # Stop script (Docker)
├── run-local.sh         # Local run script
├── check-status.sh      # Status check script
├── test_setup.py        # Setup verification script
└── README.md            # This file
```

## 🔧 Configuration

### Database

The system uses SQLite database stored in `data/leetcode_plan.db`.

On first startup, it automatically:
1. Creates database table structure
2. Imports 150 question data from `questions.json`
3. Assigns questions to the 30-day study plan
4. Sets up user settings (start date)

### Port Configuration

- **Docker**: Default port is 5001 (configurable in `docker-compose.yml`)
- **Local**: Default port is 5000 (configurable in `app.py`)

The `start.sh` script automatically finds an available port if 5001 is in use.

### Study Start Date

The system automatically sets the start date to the first day you access it. All daily plans are calculated based on this start date.

## 📊 Features in Detail

### Progress Tracking

- ✅ Completion status for each problem
- ✅ Correct/Wrong tracking
- ✅ Review count and last review date
- ✅ Time spent (optional)
- ✅ Personal notes per problem

### Statistics

- Total completed problems
- Accuracy rate
- Consecutive study days (streak)
- Distribution by category
- Distribution by difficulty
- Daily completion status

### Review System

- Automatic review scheduling based on Ebbinghaus forgetting curve
- Priority for previously wrong problems
- Review questions integrated into daily evening sessions
- Review completion tracking

## 🐛 Troubleshooting

### Docker Issues

**Problem**: Container won't start

**Solutions**:
1. Check Docker is running: `docker info`
2. Check logs: `docker-compose logs -f`
3. Try rebuilding: `docker-compose down && docker-compose up -d --build`
4. Check port availability: `./check-status.sh`

**Problem**: Port already in use

**Solutions**:
1. The `start.sh` script automatically finds an available port
2. Or manually edit `docker-compose.yml` to change the port mapping

**Problem**: Permission denied

**Solutions**:
1. Don't use `sudo` with Docker commands
2. Add your user to the docker group (Linux): `sudo usermod -aG docker $USER`

### Database Issues

**Problem**: Database not initializing

**Solutions**:
1. Delete and recreate: `rm -rf data/leetcode_plan.db && docker-compose restart`
2. Check data directory permissions: `chmod -R 755 data/`

**Problem**: Database locked errors

**Solutions**:
- The system uses WAL mode and connection pooling to prevent locking
- If issues persist, restart the container

### Application Issues

**Problem**: Cannot access http://localhost:5001

**Solutions**:
1. Check container status: `docker-compose ps`
2. Check system status: `./check-status.sh`
3. Try alternative URL: `http://127.0.0.1:5001`
4. Clear browser cache
5. Check firewall settings

**Problem**: Questions not loading

**Solutions**:
1. Verify `questions.json` exists
2. Check database initialization: `docker-compose logs`
3. Reset database: `rm -rf data/leetcode_plan.db && docker-compose restart`

### Alternative: Run Without Docker

If Docker continues to cause issues:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Access at http://localhost:5000
```

## 🔄 Maintenance

### Reset Progress

To reset all progress and start fresh:

```bash
rm -rf data/leetcode_plan.db
docker-compose restart
```

### Backup Data

To backup your study progress:

```bash
cp data/leetcode_plan.db data/leetcode_plan.db.backup
```

### View Logs

```bash
# View all logs
docker-compose logs -f

# View last 50 lines
docker-compose logs --tail=50
```

## 📝 Development

### Local Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`
4. Access at: http://localhost:5000

### API Endpoints

- `GET /` - Main application page
- `GET /api/plan/<day>` - Get study plan for specified day
- `POST /api/progress` - Update study progress
- `GET /api/statistics` - Get study statistics
- `GET /api/review` - Get review list
- `GET /api/deferred` - Get deferred questions
- `POST /api/defer` - Mark question as deferred
- `POST /api/undefer` - Remove deferred status
- `GET /api/note/<question_id>` - Get note for a question
- `POST /api/note/<question_id>` - Update note for a question
- `GET /api/current-day` - Get current study day

### Database Schema

- **questions**: Stores all 150 problems with metadata
- **progress**: Tracks completion status, notes, and review history
- **daily_plans**: Stores daily plan metadata
- **statistics**: Aggregated statistics
- **user_settings**: User preferences (start date, etc.)

## 🎓 Learning Goals

- Complete **150 problems** in **30 days**
- **5 new problems** + **2-3 review problems** per day
- Total practice: **150 new problems** + **60-90 review problems** = **210-240** high-quality problems
- Master all major algorithm categories
- Build problem-solving templates
- Develop interview-ready coding skills

## 📄 License

MIT License

## 🙏 Acknowledgments

- Question list based on [NeetCode 150](https://neetcode.io/)
- UI design follows modern web application best practices
- Review system based on Ebbinghaus forgetting curve research

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

**Keep it up! Stick to the plan for 30 days, and you'll definitely reach interview level!** 🚀
