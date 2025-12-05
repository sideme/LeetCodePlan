#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test script - Verify system configuration
"""

import os
import json
import sqlite3

def test_questions_file():
    """Test questions file"""
    print("📋 Checking questions file...")
    if os.path.exists('questions.json'):
        with open('questions.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        total = sum(len(cat['questions']) for cat in data['categories'].values())
        print(f"   ✅ Questions file exists, {total} problems total")
        return True
    else:
        print("   ❌ Questions file does not exist")
        return False

def test_database():
    """Test database"""
    print("💾 Checking database...")
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, 'leetcode_plan.db')
    
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM questions')
        count = c.fetchone()[0]
        conn.close()
        print(f"   ✅ Database exists, {count} problems already loaded")
        return True
    else:
        print("   ⚠️  Database does not exist (will be created on first run)")
        return True

def test_dependencies():
    """Test dependencies"""
    print("📦 Checking dependencies...")
    try:
        import flask
        import flask_cors
        print("   ✅ Flask and flask-cors are installed")
        return True
    except ImportError as e:
        print(f"   ❌ Missing dependency: {e}")
        print("   💡 Run: pip install -r requirements.txt")
        return False

def main():
    print("=" * 60)
    print("🧪 LeetCode Study Plan System - Configuration Check")
    print("=" * 60)
    print()
    
    results = []
    results.append(test_questions_file())
    results.append(test_database())
    results.append(test_dependencies())
    
    print()
    print("=" * 60)
    if all(results):
        print("✅ All checks passed! System can start normally")
        print()
        print("🚀 Startup methods:")
        print("   1. Docker: ./start.sh")
        print("   2. Local: python app.py")
    else:
        print("⚠️  Some checks failed, please fix according to the prompts")
    print("=" * 60)

if __name__ == '__main__':
    main()
