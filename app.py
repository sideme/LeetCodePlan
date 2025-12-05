#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LeetCode 30-Day Study Plan System - Flask Backend
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

app = Flask(__name__)
CORS(app)

# Ensure data directory exists
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

DATABASE = os.path.join(DATA_DIR, 'leetcode_plan.db')

# Database connection helper
def get_db_connection(timeout=10.0):
    """Get database connection with timeout"""
    conn = sqlite3.connect(DATABASE, timeout=timeout)
    conn.execute('PRAGMA journal_mode=WAL')  # Enable Write-Ahead Logging for better concurrency
    return conn

def init_db():
    """Initialize database"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Questions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            category TEXT NOT NULL,
            leetcode_id INTEGER,
            day_number INTEGER,
            session TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Progress table
    c.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            user_id TEXT DEFAULT 'default',
            completed_date DATE,
            is_correct BOOLEAN DEFAULT 1,
            time_spent INTEGER,
            notes TEXT,
            review_count INTEGER DEFAULT 0,
            last_review_date DATE,
            deferred BOOLEAN DEFAULT 0,
            deferred_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (question_id) REFERENCES questions (id)
        )
    ''')
    
    # Add deferred columns if they don't exist (for existing databases)
    try:
        c.execute('ALTER TABLE progress ADD COLUMN deferred BOOLEAN DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        c.execute('ALTER TABLE progress ADD COLUMN deferred_date DATE')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Daily plans table
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_number INTEGER NOT NULL UNIQUE,
            date DATE,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Statistics table
    c.execute('''
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT DEFAULT 'default',
            total_completed INTEGER DEFAULT 0,
            total_correct INTEGER DEFAULT 0,
            total_wrong INTEGER DEFAULT 0,
            streak_days INTEGER DEFAULT 0,
            last_study_date DATE,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User settings table (for start date)
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Initialize start date if not exists
    c.execute('SELECT setting_value FROM user_settings WHERE setting_key = ?', ('start_date',))
    if not c.fetchone():
        today = datetime.now().date().isoformat()
        c.execute('INSERT INTO user_settings (setting_key, setting_value) VALUES (?, ?)', 
                 ('start_date', today))
    
    conn.commit()
    conn.close()

def load_questions_data():
    """Load questions data"""
    with open('questions.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def update_categories():
    """Update category names from Chinese to English"""
    category_mapping = {
        '数组和哈希表': 'Arrays & Hash Tables',
        '双指针': 'Two Pointers',
        '滑动窗口': 'Sliding Window',
        '栈': 'Stack',
        '二分查找': 'Binary Search',
        '链表': 'Linked List',
        '树': 'Tree',
        '堆/优先队列': 'Heap / Priority Queue',
        '回溯': 'Backtracking',
        '图': 'Graph',
        '动态规划': 'Dynamic Programming',
        '贪心': 'Greedy',
        '区间': 'Intervals',
        '数学': 'Math',
        '位运算': 'Bit Manipulation',
        '其他': 'Other'
    }
    
    conn = get_db_connection()
    c = conn.cursor()
    
    for old_category, new_category in category_mapping.items():
        c.execute('''
            UPDATE questions 
            SET category = ? 
            WHERE category = ?
        ''', (new_category, old_category))
    
    conn.commit()
    conn.close()
    print(f"Updated {len(category_mapping)} category names to English")

def populate_questions():
    """Import questions data into database"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check if data already exists
    c.execute('SELECT COUNT(*) FROM questions')
    if c.fetchone()[0] > 0:
        # Update existing categories to English
        update_categories()
        conn.close()
        return
    
    data = load_questions_data()
    study_plan = create_30_day_plan()
    
    question_id_map = {}
    for category, cat_data in data['categories'].items():
        for q in cat_data['questions']:
            question_id_map[q['id']] = {
                'title': q['title'],
                'difficulty': q['difficulty'],
                'category': category
            }
    
    # Insert questions and assign to days
    for day_num, day_plan in study_plan.items():
        for session, questions in day_plan['sessions'].items():
            for q_info in questions:
                leetcode_id = q_info['id']
                q_data = question_id_map.get(leetcode_id, {})
                
                c.execute('''
                    INSERT OR IGNORE INTO questions 
                    (id, title, difficulty, category, leetcode_id, day_number, session, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    leetcode_id,
                    q_data.get('title', ''),
                    q_data.get('difficulty', 'Medium'),
                    q_data.get('category', 'Other'),
                    leetcode_id,
                    day_num,
                    session,
                    day_plan.get('description', '')
                ))
    
    conn.commit()
    conn.close()

def create_30_day_plan() -> Dict:
    """Create a scientific 30-day study plan"""
    plan = {}
    
    # Days 1-5: Basic Data Structures
    plan[1] = {
        'description': 'Basic Data Structures - Arrays & Hash Tables',
        'focus': 'Arrays & Hash Tables',
        'sessions': {
            'morning': [
                {'id': 1, 'title': 'Two Sum'},
                {'id': 217, 'title': 'Contains Duplicate'}
            ],
            'afternoon': [
                {'id': 49, 'title': 'Group Anagrams'},
                {'id': 238, 'title': 'Product of Array Except Self'},
                {'id': 347, 'title': 'Top K Frequent Elements'}
            ],
            'evening': []
        }
    }
    
    plan[2] = {
        'description': 'Arrays & Hash Tables Advanced',
        'focus': 'Arrays & Hash Tables',
        'sessions': {
            'morning': [
                {'id': 36, 'title': 'Valid Sudoku'},
                {'id': 128, 'title': 'Longest Consecutive Sequence'}
            ],
            'afternoon': [
                {'id': 271, 'title': 'Encode and Decode Strings'},
                {'id': 202, 'title': 'Happy Number'},
                {'id': 66, 'title': 'Plus One'}
            ],
            'evening': []
        }
    }
    
    plan[3] = {
        'description': 'Two Pointers Basics',
        'focus': 'Two Pointers',
        'sessions': {
            'morning': [
                {'id': 125, 'title': 'Valid Palindrome'},
                {'id': 11, 'title': 'Container With Most Water'}
            ],
            'afternoon': [
                {'id': 15, 'title': '3Sum'},
                {'id': 167, 'title': 'Two Sum II'},
                {'id': 121, 'title': 'Best Time to Buy and Sell Stock'}
            ],
            'evening': []
        }
    }
    
    plan[4] = {
        'description': 'Two Pointers Advanced',
        'focus': 'Two Pointers',
        'sessions': {
            'morning': [
                {'id': 42, 'title': 'Trapping Rain Water'}
            ],
            'afternoon': [
                {'id': 136, 'title': 'Single Number'},
                {'id': 191, 'title': 'Number of 1 Bits'},
                {'id': 190, 'title': 'Reverse Bits'},
                {'id': 268, 'title': 'Missing Number'}
            ],
            'evening': []
        }
    }
    
    plan[5] = {
        'description': 'Sliding Window Basics',
        'focus': 'Sliding Window',
        'sessions': {
            'morning': [
                {'id': 3, 'title': 'Longest Substring Without Repeating Characters'},
                {'id': 424, 'title': 'Longest Repeating Character Replacement'}
            ],
            'afternoon': [
                {'id': 567, 'title': 'Permutation in String'},
                {'id': 76, 'title': 'Minimum Window Substring'},
                {'id': 239, 'title': 'Sliding Window Maximum'}
            ],
            'evening': []
        }
    }
    
    # Days 6-10: Stack, Linked List
    plan[6] = {
        'description': 'Stack Basics',
        'focus': 'Stack',
        'sessions': {
            'morning': [
                {'id': 20, 'title': 'Valid Parentheses'},
                {'id': 155, 'title': 'Min Stack'}
            ],
            'afternoon': [
                {'id': 150, 'title': 'Evaluate Reverse Polish Notation'},
                {'id': 22, 'title': 'Generate Parentheses'},
                {'id': 739, 'title': 'Daily Temperatures'}
            ],
            'evening': []
        }
    }
    
    plan[7] = {
        'description': 'Stack Advanced',
        'focus': 'Stack',
        'sessions': {
            'morning': [
                {'id': 84, 'title': 'Largest Rectangle in Histogram'}
            ],
            'afternoon': [
                {'id': 853, 'title': 'Car Fleet'},
                {'id': 48, 'title': 'Rotate Image'},
                {'id': 54, 'title': 'Spiral Matrix'},
                {'id': 73, 'title': 'Set Matrix Zeroes'}
            ],
            'evening': []
        }
    }
    
    plan[8] = {
        'description': 'Linked List Basics',
        'focus': 'Linked List',
        'sessions': {
            'morning': [
                {'id': 206, 'title': 'Reverse Linked List'},
                {'id': 21, 'title': 'Merge Two Sorted Lists'}
            ],
            'afternoon': [
                {'id': 141, 'title': 'Linked List Cycle'},
                {'id': 19, 'title': 'Remove Nth Node From End'},
                {'id': 143, 'title': 'Reorder List'}
            ],
            'evening': []
        }
    }
    
    plan[9] = {
        'description': 'Linked List Advanced',
        'focus': 'Linked List',
        'sessions': {
            'morning': [
                {'id': 138, 'title': 'Copy List with Random Pointer'},
                {'id': 2, 'title': 'Add Two Numbers'}
            ],
            'afternoon': [
                {'id': 287, 'title': 'Find the Duplicate Number'},
                {'id': 146, 'title': 'LRU Cache'},
                {'id': 23, 'title': 'Merge k Sorted Lists'}
            ],
            'evening': []
        }
    }
    
    plan[10] = {
        'description': 'Linked List Advanced Topics',
        'focus': 'Linked List',
        'sessions': {
            'morning': [
                {'id': 25, 'title': 'Reverse Nodes in k-Group'}
            ],
            'afternoon': [
                {'id': 50, 'title': 'Pow(x, n)'},
                {'id': 43, 'title': 'Multiply Strings'},
                {'id': 371, 'title': 'Sum of Two Integers'},
                {'id': 7, 'title': 'Reverse Integer'}
            ],
            'evening': []
        }
    }
    
    # Days 11-15: Trees
    plan[11] = {
        'description': 'Tree Basics - Traversal',
        'focus': 'Tree',
        'sessions': {
            'morning': [
                {'id': 226, 'title': 'Invert Binary Tree'},
                {'id': 104, 'title': 'Maximum Depth of Binary Tree'}
            ],
            'afternoon': [
                {'id': 543, 'title': 'Diameter of Binary Tree'},
                {'id': 110, 'title': 'Balanced Binary Tree'},
                {'id': 100, 'title': 'Same Tree'}
            ],
            'evening': []
        }
    }
    
    plan[12] = {
        'description': 'Tree Advanced - BST',
        'focus': 'Tree',
        'sessions': {
            'morning': [
                {'id': 572, 'title': 'Subtree of Another Tree'},
                {'id': 235, 'title': 'Lowest Common Ancestor of a BST'}
            ],
            'afternoon': [
                {'id': 98, 'title': 'Validate Binary Search Tree'},
                {'id': 230, 'title': 'Kth Smallest Element in a BST'},
                {'id': 102, 'title': 'Binary Tree Level Order Traversal'}
            ],
            'evening': []
        }
    }
    
    plan[13] = {
        'description': 'Tree Advanced Topics',
        'focus': 'Tree',
        'sessions': {
            'morning': [
                {'id': 199, 'title': 'Binary Tree Right Side View'},
                {'id': 1448, 'title': 'Count Good Nodes in Binary Tree'}
            ],
            'afternoon': [
                {'id': 105, 'title': 'Construct Binary Tree from Preorder and Inorder'},
                {'id': 124, 'title': 'Binary Tree Maximum Path Sum'},
                {'id': 297, 'title': 'Serialize and Deserialize Binary Tree'}
            ],
            'evening': []
        }
    }
    
    plan[14] = {
        'description': 'Binary Search',
        'focus': 'Binary Search',
        'sessions': {
            'morning': [
                {'id': 704, 'title': 'Binary Search'},
                {'id': 74, 'title': 'Search a 2D Matrix'}
            ],
            'afternoon': [
                {'id': 875, 'title': 'Koko Eating Bananas'},
                {'id': 33, 'title': 'Search in Rotated Sorted Array'},
                {'id': 153, 'title': 'Find Minimum in Rotated Sorted Array'}
            ],
            'evening': []
        }
    }
    
    plan[15] = {
        'description': 'Heap & Priority Queue',
        'focus': 'Heap/Priority Queue',
        'sessions': {
            'morning': [
                {'id': 703, 'title': 'Kth Largest Element in a Stream'},
                {'id': 1046, 'title': 'Last Stone Weight'}
            ],
            'afternoon': [
                {'id': 973, 'title': 'K Closest Points to Origin'},
                {'id': 215, 'title': 'Kth Largest Element in an Array'},
                {'id': 621, 'title': 'Task Scheduler'}
            ],
            'evening': []
        }
    }
    
    # Days 16-20: Graph, Backtracking
    plan[16] = {
        'description': 'Graph Basics - DFS',
        'focus': 'Graph',
        'sessions': {
            'morning': [
                {'id': 200, 'title': 'Number of Islands'},
                {'id': 695, 'title': 'Max Area of Island'}
            ],
            'afternoon': [
                {'id': 130, 'title': 'Surrounded Regions'},
                {'id': 133, 'title': 'Clone Graph'},
                {'id': 417, 'title': 'Pacific Atlantic Water Flow'}
            ],
            'evening': []
        }
    }
    
    plan[17] = {
        'description': 'Graph Advanced - BFS',
        'focus': 'Graph',
        'sessions': {
            'morning': [
                {'id': 994, 'title': 'Rotting Oranges'}
            ],
            'afternoon': [
                {'id': 207, 'title': 'Course Schedule'},
                {'id': 210, 'title': 'Course Schedule II'},
                {'id': 684, 'title': 'Redundant Connection'},
                {'id': 323, 'title': 'Number of Connected Components'}
            ],
            'evening': []
        }
    }
    
    plan[18] = {
        'description': 'Backtracking Basics',
        'focus': 'Backtracking',
        'sessions': {
            'morning': [
                {'id': 78, 'title': 'Subsets'},
                {'id': 39, 'title': 'Combination Sum'}
            ],
            'afternoon': [
                {'id': 46, 'title': 'Permutations'},
                {'id': 90, 'title': 'Subsets II'},
                {'id': 40, 'title': 'Combination Sum II'}
            ],
            'evening': []
        }
    }
    
    plan[19] = {
        'description': 'Backtracking Advanced',
        'focus': 'Backtracking',
        'sessions': {
            'morning': [
                {'id': 79, 'title': 'Word Search'},
                {'id': 131, 'title': 'Palindrome Partitioning'}
            ],
            'afternoon': [
                {'id': 17, 'title': 'Letter Combinations of a Phone Number'},
                {'id': 51, 'title': 'N-Queens'},
                {'id': 208, 'title': 'Implement Trie'}
            ],
            'evening': []
        }
    }
    
    plan[20] = {
        'description': 'Trie & String Problems',
        'focus': 'Trie',
        'sessions': {
            'morning': [
                {'id': 211, 'title': 'Design Add and Search Words'},
                {'id': 212, 'title': 'Word Search II'}
            ],
            'afternoon': [
                {'id': 981, 'title': 'Time Based Key-Value Store'},
                {'id': 295, 'title': 'Find Median from Data Stream'},
                {'id': 380, 'title': 'Insert Delete GetRandom O(1)'}
            ],
            'evening': []
        }
    }
    
    # Days 21-25: Dynamic Programming
    plan[21] = {
        'description': 'Dynamic Programming Basics - 1D DP',
        'focus': 'Dynamic Programming',
        'sessions': {
            'morning': [
                {'id': 70, 'title': 'Climbing Stairs'},
                {'id': 746, 'title': 'Min Cost Climbing Stairs'}
            ],
            'afternoon': [
                {'id': 198, 'title': 'House Robber'},
                {'id': 213, 'title': 'House Robber II'},
                {'id': 91, 'title': 'Decode Ways'}
            ],
            'evening': []
        }
    }
    
    plan[22] = {
        'description': 'Dynamic Programming - String DP',
        'focus': 'Dynamic Programming',
        'sessions': {
            'morning': [
                {'id': 5, 'title': 'Longest Palindromic Substring'},
                {'id': 647, 'title': 'Palindromic Substrings'}
            ],
            'afternoon': [
                {'id': 139, 'title': 'Word Break'},
                {'id': 300, 'title': 'Longest Increasing Subsequence'},
                {'id': 152, 'title': 'Maximum Product Subarray'}
            ],
            'evening': []
        }
    }
    
    plan[23] = {
        'description': 'Dynamic Programming - Knapsack',
        'focus': 'Dynamic Programming',
        'sessions': {
            'morning': [
                {'id': 322, 'title': 'Coin Change'},
                {'id': 416, 'title': 'Partition Equal Subset Sum'}
            ],
            'afternoon': [
                {'id': 1143, 'title': 'Longest Common Subsequence'},
                {'id': 72, 'title': 'Edit Distance'},
                {'id': 115, 'title': 'Distinct Subsequences'}
            ],
            'evening': []
        }
    }
    
    plan[24] = {
        'description': 'Dynamic Programming Advanced',
        'focus': 'Dynamic Programming',
        'sessions': {
            'morning': [
                {'id': 312, 'title': 'Burst Balloons'},
                {'id': 10, 'title': 'Regular Expression Matching'}
            ],
            'afternoon': [
                {'id': 53, 'title': 'Maximum Subarray'},
                {'id': 55, 'title': 'Jump Game'},
                {'id': 45, 'title': 'Jump Game II'}
            ],
            'evening': []
        }
    }
    
    plan[25] = {
        'description': 'Greedy Algorithms',
        'focus': 'Greedy',
        'sessions': {
            'morning': [
                {'id': 134, 'title': 'Gas Station'},
                {'id': 763, 'title': 'Partition Labels'}
            ],
            'afternoon': [
                {'id': 846, 'title': 'Hand of Straights'},
                {'id': 678, 'title': 'Valid Parenthesis String'},
                {'id': 57, 'title': 'Insert Interval'}
            ],
            'evening': []
        }
    }
    
    # Days 26-30: Review & Advanced Topics
    plan[26] = {
        'description': 'Interval Problems',
        'focus': 'Intervals',
        'sessions': {
            'morning': [
                {'id': 56, 'title': 'Merge Intervals'},
                {'id': 435, 'title': 'Non-overlapping Intervals'}
            ],
            'afternoon': [
                {'id': 252, 'title': 'Meeting Rooms'},
                {'id': 253, 'title': 'Meeting Rooms II'},
                {'id': 2013, 'title': 'Detect Squares'}
            ],
            'evening': []
        }
    }
    
    plan[27] = {
        'description': 'Design Problems',
        'focus': 'Design',
        'sessions': {
            'morning': [
                {'id': 146, 'title': 'LRU Cache'},
                {'id': 460, 'title': 'LFU Cache'}
            ],
            'afternoon': [
                {'id': 528, 'title': 'Random Pick with Weight'},
                {'id': 432, 'title': 'All O one Data Structure'},
                {'id': 895, 'title': 'Maximum Frequency Stack'}
            ],
            'evening': []
        }
    }
    
    plan[28] = {
        'description': 'Advanced Design Problems',
        'focus': 'Design',
        'sessions': {
            'morning': [
                {'id': 588, 'title': 'Design In-Memory File System'},
                {'id': 642, 'title': 'Design Search Autocomplete System'}
            ],
            'afternoon': [
                {'id': 2115, 'title': 'Find All Possible Recipes'},
                {'id': 269, 'title': 'Alien Dictionary'},
                {'id': 444, 'title': 'Sequence Reconstruction'}
            ],
            'evening': []
        }
    }
    
    plan[29] = {
        'description': 'Comprehensive Review - High Frequency',
        'focus': 'Review',
        'sessions': {
            'morning': [
                {'id': 1, 'title': 'Two Sum'},
                {'id': 206, 'title': 'Reverse Linked List'},
                {'id': 3, 'title': 'Longest Substring Without Repeating Characters'}
            ],
            'afternoon': [
                {'id': 200, 'title': 'Number of Islands'},
                {'id': 70, 'title': 'Climbing Stairs'},
                {'id': 20, 'title': 'Valid Parentheses'}
            ],
            'evening': []
        }
    }
    
    plan[30] = {
        'description': 'Final Review - Fill the Gaps',
        'focus': 'Review',
        'sessions': {
            'morning': [
                {'id': 42, 'title': 'Trapping Rain Water'},
                {'id': 124, 'title': 'Binary Tree Maximum Path Sum'}
            ],
            'afternoon': [
                {'id': 23, 'title': 'Merge k Sorted Lists'},
                {'id': 76, 'title': 'Minimum Window Substring'},
                {'id': 312, 'title': 'Burst Balloons'}
            ],
            'evening': []
        }
    }
    
    return plan

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

def get_start_date():
    """Get the start date from database"""
    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute('SELECT setting_value FROM user_settings WHERE setting_key = ?', ('start_date',))
        result = c.fetchone()
        if result:
            return datetime.strptime(result[0], '%Y-%m-%d').date()
        else:
            today = datetime.now().date()
            # Save it
            c.execute('INSERT OR REPLACE INTO user_settings (setting_key, setting_value) VALUES (?, ?)',
                     ('start_date', today.isoformat()))
            conn.commit()
            return today
    finally:
        conn.close()

def get_current_day():
    """Calculate current day based on start date"""
    start_date = get_start_date()
    today = datetime.now().date()
    days_passed = (today - start_date).days + 1
    return min(max(1, days_passed), 30)

@app.route('/api/current-day', methods=['GET'])
def get_current_day_api():
    """Get current day number"""
    current_day = get_current_day()
    start_date = get_start_date()
    today = datetime.now().date()
    
    return jsonify({
        'current_day': current_day,
        'start_date': start_date.isoformat(),
        'today': today.isoformat(),
        'days_passed': (today - start_date).days
    })

@app.route('/api/plan/<int:day>', methods=['GET'])
def get_plan(day):
    """Get study plan for specified day"""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Get all questions for this day
    c.execute('''
        SELECT * FROM questions 
        WHERE day_number = ?
        ORDER BY 
            CASE session
                WHEN 'morning' THEN 1
                WHEN 'afternoon' THEN 2
                WHEN 'evening' THEN 3
                ELSE 4
            END
    ''', (day,))
    
    questions = [dict(row) for row in c.fetchall()]
    
    # Get deferred questions for this day (exclude them from normal display)
    deferred_question_ids = set()
    if questions:
        question_ids = [q['id'] for q in questions]
        placeholders = ','.join('?' * len(question_ids))
        c.execute(f'''
            SELECT question_id FROM progress 
            WHERE question_id IN ({placeholders}) AND deferred = 1
        ''', question_ids)
        deferred_question_ids = {row[0] for row in c.fetchall()}
    
    # Filter out deferred questions from the main list
    questions = [q for q in questions if q['id'] not in deferred_question_ids]
    
    # Get completion status and notes for this day's questions
    completed_ids = set()
    wrong_ids = set()
    question_notes = {}
    if questions:
        question_ids = [q['id'] for q in questions]
        placeholders = ','.join('?' * len(question_ids))
        c.execute(f'''
            SELECT question_id, is_correct, notes FROM progress 
            WHERE question_id IN ({placeholders})
        ''', question_ids)
        for row in c.fetchall():
            completed_ids.add(row[0])
            if not row[1]:
                wrong_ids.add(row[0])
            if row[2]:  # notes
                question_notes[row[0]] = row[2]
    
    # Get incomplete questions from previous day (if day > 1)
    incomplete_from_previous = []
    if day > 1:
        prev_day = day - 1
        c.execute('''
            SELECT * FROM questions 
            WHERE day_number = ?
        ''', (prev_day,))
        prev_questions = [dict(row) for row in c.fetchall()]
        
        if prev_questions:
            prev_question_ids = [q['id'] for q in prev_questions]
            placeholders = ','.join('?' * len(prev_question_ids))
            c.execute(f'''
                SELECT question_id FROM progress 
                WHERE question_id IN ({placeholders})
            ''', prev_question_ids)
            prev_completed = {row[0] for row in c.fetchall()}
            
            # Get incomplete questions from previous day (exclude deferred ones)
            for q in prev_questions:
                if q['id'] not in prev_completed and q['id'] not in deferred_question_ids:
                    q_dict = dict(q)
                    q_dict['completed'] = False
                    q_dict['is_correct'] = None
                    q_dict['from_previous_day'] = True
                    incomplete_from_previous.append(q_dict)
    
    # Get review questions based on Ebbinghaus forgetting curve
    review_questions_for_today = []
    review_intervals = [1, 3, 7, 14]
    today = datetime.now().date()
    
    # Calculate the actual date for this study day
    start_date = get_start_date()
    study_date = start_date + timedelta(days=day - 1)
    
    # Get questions that should be reviewed today based on forgetting curve (exclude deferred)
    today = datetime.now().date()
    for interval in review_intervals:
        target_completion_date = study_date - timedelta(days=interval)
        c.execute('''
            SELECT q.*, p.completed_date, p.is_correct, p.review_count, p.notes, p.last_review_date
            FROM questions q
            JOIN progress p ON q.id = p.question_id
            WHERE p.completed_date = ? AND (p.deferred IS NULL OR p.deferred = 0)
            ORDER BY p.is_correct ASC, p.review_count ASC
        ''', (target_completion_date,))
        
        for row in c.fetchall():
            q_dict = dict(row)
            # Check if this review was completed today
            last_review_date = row['last_review_date']
            if last_review_date:
                if isinstance(last_review_date, str):
                    last_review_date = datetime.strptime(last_review_date, '%Y-%m-%d').date()
                elif isinstance(last_review_date, datetime):
                    last_review_date = last_review_date.date()
                # If reviewed today, mark as completed
                q_dict['completed'] = (last_review_date == today)
            else:
                # Check if completed_date is today (first time completing review)
                completed_date = row['completed_date']
                if completed_date:
                    if isinstance(completed_date, str):
                        completed_date = datetime.strptime(completed_date, '%Y-%m-%d').date()
                    elif isinstance(completed_date, datetime):
                        completed_date = completed_date.date()
                    q_dict['completed'] = (completed_date == today)
                else:
                    q_dict['completed'] = False
            
            q_dict['is_correct'] = row['is_correct']
            q_dict['from_previous_day'] = False
            q_dict['for_review'] = True
            q_dict['review_interval'] = interval
            q_dict['note'] = row['notes'] if row['notes'] else ''
            review_questions_for_today.append(q_dict)
    
    # If no questions match exact intervals, get recently wrong questions (exclude deferred)
    if not review_questions_for_today:
        c.execute('''
            SELECT q.*, p.completed_date, p.is_correct, p.review_count, p.notes, p.last_review_date
            FROM questions q
            JOIN progress p ON q.id = p.question_id
            WHERE p.is_correct = 0
            AND p.completed_date < ?
            AND (p.deferred IS NULL OR p.deferred = 0)
            ORDER BY p.completed_date DESC, p.review_count ASC
            LIMIT 3
        ''', (study_date,))
        
        for row in c.fetchall():
            q_dict = dict(row)
            # Check if reviewed today
            last_review_date = row['last_review_date']
            if last_review_date:
                if isinstance(last_review_date, str):
                    last_review_date = datetime.strptime(last_review_date, '%Y-%m-%d').date()
                elif isinstance(last_review_date, datetime):
                    last_review_date = last_review_date.date()
                q_dict['completed'] = (last_review_date == today)
            else:
                completed_date = row['completed_date']
                if completed_date:
                    if isinstance(completed_date, str):
                        completed_date = datetime.strptime(completed_date, '%Y-%m-%d').date()
                    elif isinstance(completed_date, datetime):
                        completed_date = completed_date.date()
                    q_dict['completed'] = (completed_date == today)
                else:
                    q_dict['completed'] = False
            q_dict['is_correct'] = row['is_correct']
            q_dict['from_previous_day'] = False
            q_dict['for_review'] = True
            q_dict['review_interval'] = None
            q_dict['note'] = row['notes'] if row['notes'] else ''
            review_questions_for_today.append(q_dict)
    
    # If still no review questions, get recently completed ones (exclude deferred)
    if not review_questions_for_today:
        c.execute('''
            SELECT q.*, p.completed_date, p.is_correct, p.review_count, p.notes, p.last_review_date
            FROM questions q
            JOIN progress p ON q.id = p.question_id
            WHERE p.completed_date < ?
            AND (p.deferred IS NULL OR p.deferred = 0)
            ORDER BY p.completed_date DESC, p.review_count ASC
            LIMIT 3
        ''', (study_date,))
        
        for row in c.fetchall():
            q_dict = dict(row)
            # Check if reviewed today
            last_review_date = row['last_review_date']
            if last_review_date:
                if isinstance(last_review_date, str):
                    last_review_date = datetime.strptime(last_review_date, '%Y-%m-%d').date()
                elif isinstance(last_review_date, datetime):
                    last_review_date = last_review_date.date()
                q_dict['completed'] = (last_review_date == today)
            else:
                completed_date = row['completed_date']
                if completed_date:
                    if isinstance(completed_date, str):
                        completed_date = datetime.strptime(completed_date, '%Y-%m-%d').date()
                    elif isinstance(completed_date, datetime):
                        completed_date = completed_date.date()
                    q_dict['completed'] = (completed_date == today)
                else:
                    q_dict['completed'] = False
            q_dict['is_correct'] = row['is_correct']
            q_dict['from_previous_day'] = False
            q_dict['for_review'] = True
            q_dict['review_interval'] = None
            q_dict['note'] = row['notes'] if row['notes'] else ''
            review_questions_for_today.append(q_dict)
    
    # Remove duplicates (in case a question appears multiple times)
    seen_ids = set()
    unique_review_questions = []
    for q in review_questions_for_today:
        if q['id'] not in seen_ids:
            seen_ids.add(q['id'])
            unique_review_questions.append(q)
    review_questions_for_today = unique_review_questions[:3]  # Max 3 review questions
    
    # Get plan info for this day
    c.execute('SELECT * FROM daily_plans WHERE day_number = ?', (day,))
    plan_info = c.fetchone()
    
    # Organize data
    sessions = {
        'morning': [],
        'afternoon': [],
        'evening': []
    }
    
    # Add incomplete questions from previous day to morning session
    for q in incomplete_from_previous:
        # Get note if exists
        c.execute('SELECT notes FROM progress WHERE question_id = ?', (q['id'],))
        note_result = c.fetchone()
        q['note'] = note_result[0] if note_result and note_result[0] else ''
        q['from_previous_day'] = True
        sessions['morning'].append(q)
    
    # Add today's questions
    for q in questions:
        q_dict = dict(q)
        q_dict['completed'] = q['id'] in completed_ids
        q_dict['is_correct'] = q['id'] not in wrong_ids if q['id'] in completed_ids else None
        q_dict['from_previous_day'] = False
        q_dict['for_review'] = False
        q_dict['note'] = question_notes.get(q['id'], '')
        sessions[q['session']].append(q_dict)
    
    # Add review questions to evening session
    for q in review_questions_for_today:
        # Get note if exists
        c.execute('SELECT notes FROM progress WHERE question_id = ?', (q['id'],))
        note_result = c.fetchone()
        q['note'] = note_result[0] if note_result and note_result[0] else ''
        sessions['evening'].append(q)
    
    total_questions = len(questions) + len(incomplete_from_previous) + len(review_questions_for_today)
    total_completed = len(completed_ids)
    
    # Get count of deferred questions for this day
    deferred_count = len(deferred_question_ids)
    
    try:
        return jsonify({
            'day': day,
            'sessions': sessions,
            'plan_info': dict(plan_info) if plan_info else None,
            'statistics': {
                'total': total_questions,
                'completed': total_completed,
                'wrong': len(wrong_ids),
                'from_previous': len(incomplete_from_previous),
                'for_review': len(review_questions_for_today),
                'deferred': deferred_count
            }
        })
    finally:
        conn.close()

@app.route('/api/defer', methods=['POST'])
def defer_question():
    """Mark a question as deferred (do later)"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        question_id = data.get('question_id')
        if question_id is None:
            return jsonify({'success': False, 'error': 'question_id is required'}), 400
        
        conn = get_db_connection()
        try:
            c = conn.cursor()
            
            # Check if progress entry exists
            c.execute('SELECT id FROM progress WHERE question_id = ?', (question_id,))
            existing = c.fetchone()
            
            if existing:
                # Update existing entry
                c.execute('''
                    UPDATE progress 
                    SET deferred = 1, deferred_date = ?
                    WHERE question_id = ?
                ''', (datetime.now().date(), question_id))
            else:
                # Create new entry with deferred status
                c.execute('''
                    INSERT INTO progress (question_id, deferred, deferred_date)
                    VALUES (?, 1, ?)
                ''', (question_id, datetime.now().date()))
            
            conn.commit()
            return jsonify({'success': True})
        finally:
            conn.close()
    except Exception as e:
        print(f"Error deferring question: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/undefer', methods=['POST'])
def undefer_question():
    """Remove deferred status from a question"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        question_id = data.get('question_id')
        if question_id is None:
            return jsonify({'success': False, 'error': 'question_id is required'}), 400
        
        conn = get_db_connection()
        try:
            c = conn.cursor()
            c.execute('''
                UPDATE progress 
                SET deferred = 0, deferred_date = NULL
                WHERE question_id = ?
            ''', (question_id,))
            conn.commit()
            return jsonify({'success': True})
        finally:
            conn.close()
    except Exception as e:
        print(f"Error undeffering question: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/deferred', methods=['GET'])
def get_deferred_questions():
    """Get all deferred questions"""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    try:
        c.execute('''
            SELECT q.*, p.deferred_date, p.completed_date, p.is_correct
            FROM questions q
            JOIN progress p ON q.id = p.question_id
            WHERE p.deferred = 1
            ORDER BY p.deferred_date DESC, q.day_number ASC
        ''')
        
        deferred_questions = []
        for row in c.fetchall():
            q_dict = dict(row)
            q_dict['completed'] = row['completed_date'] is not None
            q_dict['is_correct'] = row['is_correct']
            deferred_questions.append(q_dict)
        
        return jsonify(deferred_questions)
    finally:
        conn.close()

@app.route('/api/note/<int:question_id>', methods=['GET'])
def get_note(question_id):
    """Get note for a question"""
    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute('SELECT notes FROM progress WHERE question_id = ?', (question_id,))
        result = c.fetchone()
        note = result[0] if result and result[0] else ''
        return jsonify({'note': note})
    finally:
        conn.close()

@app.route('/api/note/<int:question_id>', methods=['POST'])
def update_note(question_id):
    """Update note for a question"""
    try:
        data = request.json
        note = data.get('note', '')
        
        conn = get_db_connection()
        try:
            c = conn.cursor()
            
            # Check if progress entry exists
            c.execute('SELECT id FROM progress WHERE question_id = ?', (question_id,))
            existing = c.fetchone()
            
            if existing:
                c.execute('''
                    UPDATE progress 
                    SET notes = ?
                    WHERE question_id = ?
                ''', (note, question_id))
            else:
                # Create new entry with note
                c.execute('''
                    INSERT INTO progress (question_id, notes)
                    VALUES (?, ?)
                ''', (question_id, note))
            
            conn.commit()
            return jsonify({'success': True})
        finally:
            conn.close()
    except Exception as e:
        print(f"Error updating note: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/progress', methods=['POST'])
def update_progress():
    """Update study progress"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        question_id = data.get('question_id')
        is_correct = data.get('is_correct', True)
        time_spent = data.get('time_spent')
        notes = data.get('notes', '')
        
        if question_id is None:
            return jsonify({'success': False, 'error': 'question_id is required'}), 400
        
        # Handle undo (is_correct is null)
        if is_correct is None:
            # Delete the progress entry
            conn = get_db_connection()
            try:
                c = conn.cursor()
                c.execute('DELETE FROM progress WHERE question_id = ?', (question_id,))
                conn.commit()
                return jsonify({'success': True})
            finally:
                conn.close()
        
        conn = get_db_connection()
        try:
            c = conn.cursor()
            
            # Check if exists
            c.execute('SELECT id, review_count FROM progress WHERE question_id = ?', (question_id,))
            existing = c.fetchone()
            
            if existing:
                # If it's a review (already completed before), increment review_count
                current_review_count = existing[1] or 0
                # Check if this question was completed before today (indicating it's a review)
                c.execute('SELECT completed_date, deferred FROM progress WHERE question_id = ?', (question_id,))
                prev_data = c.fetchone()
                
                is_review = False
                if prev_data and prev_data[0]:
                    # Convert string date to date object if needed
                    prev_date = prev_data[0]
                    if isinstance(prev_date, str):
                        prev_date = datetime.strptime(prev_date, '%Y-%m-%d').date()
                    elif isinstance(prev_date, datetime):
                        prev_date = prev_date.date()
                    # Check if completed before today
                    is_review = prev_date < datetime.now().date()
                
                new_review_count = current_review_count + 1 if is_review else current_review_count
                
                # If marking as complete, remove deferred status
                c.execute('''
                    UPDATE progress 
                    SET completed_date = ?, is_correct = ?, time_spent = ?, notes = ?, 
                        review_count = ?, last_review_date = ?, deferred = 0, deferred_date = NULL
                    WHERE question_id = ?
                ''', (datetime.now().date(), is_correct, time_spent, notes, 
                      new_review_count, datetime.now().date() if is_review else None, question_id))
            else:
                c.execute('''
                    INSERT INTO progress (question_id, completed_date, is_correct, time_spent, notes, deferred)
                    VALUES (?, ?, ?, ?, ?, 0)
                ''', (question_id, datetime.now().date(), is_correct, time_spent, notes))
            
            conn.commit()
        finally:
            conn.close()
        
        # Update statistics in a separate connection
        try:
            update_statistics()
        except Exception as e:
            print(f"Warning: Failed to update statistics: {e}")
        
        return jsonify({'success': True})
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        return jsonify({'success': False, 'error': 'Database error, please try again'}), 500
    except Exception as e:
        print(f"Error updating progress: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get study statistics"""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Overall statistics
    c.execute('''
        SELECT 
            COUNT(*) as total_completed,
            SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as total_correct,
            SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) as total_wrong
        FROM progress
    ''')
    stats = dict(c.fetchone())
    
    # Statistics by category
    c.execute('''
        SELECT category, COUNT(*) as count
        FROM questions q
        JOIN progress p ON q.id = p.question_id
        GROUP BY category
        ORDER BY count DESC
    ''')
    stats['by_category'] = {row[0]: row[1] for row in c.fetchall()}
    
    # Statistics by difficulty
    c.execute('''
        SELECT difficulty, COUNT(*) as count
        FROM questions q
        JOIN progress p ON q.id = p.question_id
        GROUP BY difficulty
    ''')
    stats['by_difficulty'] = {row[0]: row[1] for row in c.fetchall()}
    
    # Streak days
    c.execute('''
        SELECT COUNT(DISTINCT completed_date) as streak
        FROM progress
        WHERE completed_date >= date('now', '-30 days')
    ''')
    stats['streak_days'] = c.fetchone()[0] or 0
    
    # Total questions
    c.execute('SELECT COUNT(*) FROM questions')
    stats['total_questions'] = c.fetchone()[0]
    
    try:
        return jsonify(stats)
    finally:
        conn.close()

@app.route('/api/review', methods=['GET'])
def get_review_list():
    """Get review list based on Ebbinghaus forgetting curve"""
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        review_intervals = [1, 3, 7, 14]
        today = datetime.now().date()
        
        review_questions = []
        for interval in review_intervals:
            target_date = today - timedelta(days=interval)
            c.execute('''
                SELECT q.*, p.completed_date, p.is_correct, p.review_count
                FROM questions q
                JOIN progress p ON q.id = p.question_id
                WHERE p.completed_date = ?
                ORDER BY p.is_correct ASC, p.review_count ASC
            ''', (target_date,))
            
            for row in c.fetchall():
                review_questions.append(dict(row))

        # If no questions match the exact Ebbinghaus intervals,
        # fall back to recently wrong questions, then recently completed ones.
        if not review_questions:
            # First, recently wrong questions (most important to review)
            c.execute('''
                SELECT q.*, p.completed_date, p.is_correct, p.review_count
                FROM questions q
                JOIN progress p ON q.id = p.question_id
                WHERE p.is_correct = 0
                ORDER BY p.completed_date DESC, p.review_count ASC
                LIMIT 10
            ''')
            review_questions = [dict(row) for row in c.fetchall()]

        if not review_questions:
            # If still empty, use most recently completed questions
            c.execute('''
                SELECT q.*, p.completed_date, p.is_correct, p.review_count
                FROM questions q
                JOIN progress p ON q.id = p.question_id
                ORDER BY p.completed_date DESC, p.review_count ASC
                LIMIT 10
            ''')
            review_questions = [dict(row) for row in c.fetchall()]

        # Return at most 10 questions
        return jsonify(review_questions[:10])
    except Exception as e:
        print(f"Error getting review list: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

def update_statistics():
    """Update statistics"""
    conn = get_db_connection()
    try:
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) FROM progress')
        total = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM progress WHERE is_correct = 1')
        correct = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM progress WHERE is_correct = 0')
        wrong = c.fetchone()[0]
        
        c.execute('''
            INSERT OR REPLACE INTO statistics (id, total_completed, total_correct, total_wrong, updated_at)
            VALUES (1, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (total, correct, wrong))
        
        conn.commit()
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
    populate_questions()
    print("=" * 60)
    print("🚀 LeetCode 30-Day Study Plan System Started!")
    print("=" * 60)
    print("📱 Access at: http://localhost:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
