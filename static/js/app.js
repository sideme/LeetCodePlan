let currentDay = 1;
let statistics = {};
let startDate = null;
let todayDate = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadCurrentDay();
    initDayGrid();
    loadStatistics();
});

// Load current day from server
async function loadCurrentDay() {
    try {
        const response = await fetch('/api/current-day');
        const data = await response.json();
        currentDay = data.current_day;
        startDate = data.start_date;
        todayDate = data.today;
        loadDay(currentDay);
    } catch (error) {
        console.error('Failed to load current day:', error);
        // Fallback to local calculation
        loadTodayFallback();
    }
}

// Fallback to local calculation
function loadTodayFallback() {
    const today = new Date();
    const startDateLocal = localStorage.getItem('startDate');
    if (!startDateLocal) {
        localStorage.setItem('startDate', today.toISOString().split('T')[0]);
    }
    
    const daysSinceStart = Math.floor((today - new Date(startDateLocal || today)) / (1000 * 60 * 60 * 24)) + 1;
    currentDay = Math.min(Math.max(1, daysSinceStart), 30);
    loadDay(currentDay);
}

// Initialize day grid with calendar dates
function initDayGrid() {
    const dayGrid = document.getElementById('day-grid');
    dayGrid.innerHTML = ''; // Clear existing
    
    // Wait for startDate to be loaded
    if (!startDate) {
        setTimeout(initDayGrid, 100);
        return;
    }
    
    const start = new Date(startDate);
    const today = new Date();
    
    for (let i = 1; i <= 30; i++) {
        const dayBtn = document.createElement('button');
        const dayDate = new Date(start);
        dayDate.setDate(start.getDate() + i - 1);
        
        // Format: Day X (MM/DD)
        const month = dayDate.getMonth() + 1;
        const date = dayDate.getDate();
        
        // Create structured content
        dayBtn.className = 'day-btn';
        dayBtn.innerHTML = `
            <span class="day-number">${i}</span>
            <span class="day-date">${month}/${date}</span>
        `;
        dayBtn.title = `Day ${i} - ${dayDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
        
        // Highlight today
        if (dayDate.toDateString() === today.toDateString()) {
            dayBtn.classList.add('today');
        }
        
        // Highlight current day
        if (i === currentDay) {
            dayBtn.classList.add('active');
        }
        
        // Check if day is completed (all questions done)
        checkDayCompletion(i).then(completed => {
            if (completed) {
                dayBtn.classList.add('completed');
            }
        });
        
        dayBtn.onclick = () => loadDay(i);
        dayGrid.appendChild(dayBtn);
    }
}

// Check if a day is completed
async function checkDayCompletion(day) {
    try {
        const response = await fetch(`/api/plan/${day}`);
        const data = await response.json();
        return data.statistics.completed === data.statistics.total && data.statistics.total > 0;
    } catch (error) {
        return false;
    }
}

// Load today's study plan
function loadToday() {
    loadDay(currentDay);
}

// Load study plan for specified day
async function loadDay(day) {
    currentDay = day;
    
    // Update button status
    document.querySelectorAll('.day-btn').forEach((btn) => {
        const dayNumber = parseInt(btn.querySelector('.day-number')?.textContent);
        btn.classList.remove('active');
        if (dayNumber === day) {
            btn.classList.add('active');
        }
    });
    
    try {
        const response = await fetch(`/api/plan/${day}`);
        const data = await response.json();
        displayPlan(data);
    } catch (error) {
        console.error('Failed to load plan:', error);
        alert('Failed to load study plan, please refresh the page');
    }
}

// Display study plan
function displayPlan(data) {
    const content = document.getElementById('plan-content');
    
    // Calculate date for this day
    let dayDateStr = '';
    if (startDate) {
        const start = new Date(startDate);
        const dayDate = new Date(start);
        dayDate.setDate(start.getDate() + data.day - 1);
        dayDateStr = dayDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    }
    
    let html = `
        <div class="day-header">
            <h2>Day ${data.day}${dayDateStr ? ` - ${dayDateStr}` : ''}</h2>
            <div class="day-description">${data.plan_info?.description || 'Start Learning'}</div>
            <div style="margin-top: 15px; color: #666;">
                Completed: ${data.statistics.completed}/${data.statistics.total} problems
                ${data.statistics.wrong > 0 ? ` | Wrong: ${data.statistics.wrong} problems` : ''}
                ${data.statistics.from_previous > 0 ? ` | <span style="color: #f39c12;">⚠️ ${data.statistics.from_previous} incomplete from previous day</span>` : ''}
                ${data.statistics.for_review > 0 ? ` | <span style="color: #27ae60;">📚 ${data.statistics.for_review} for review</span>` : ''}
                ${data.statistics.deferred > 0 ? ` | <span style="color: #9e9e9e;">⏰ ${data.statistics.deferred} deferred</span>` : ''}
            </div>
        </div>
    `;
    
    // Morning session
    if (data.sessions.morning && data.sessions.morning.length > 0) {
        html += `
            <div class="session">
                <div class="session-header">
                    <div>
                        <div class="session-title morning">🔴 Golden Hour - Tackle New & Difficult Problems</div>
                        <div class="session-info">⏰ 3 hours | 25-30 minutes per problem</div>
                    </div>
                </div>
                <div class="question-list">
                    ${data.sessions.morning.map(q => renderQuestion(q)).join('')}
                </div>
            </div>
        `;
    }
    
    // Afternoon session
    if (data.sessions.afternoon && data.sessions.afternoon.length > 0) {
        html += `
            <div class="session">
                <div class="session-header">
                    <div>
                        <div class="session-title afternoon">🟡 Silver Hour - Practice & Variations</div>
                        <div class="session-info">⏰ 2-3 hours | Complete within 20 minutes per problem</div>
                    </div>
                </div>
                <div class="question-list">
                    ${data.sessions.afternoon.map(q => renderQuestion(q)).join('')}
                </div>
            </div>
        `;
    }
    
    // Evening session
    if (data.sessions.evening && data.sessions.evening.length > 0) {
        html += `
            <div class="session">
                <div class="session-header">
                    <div>
                        <div class="session-title evening">🟢 Bronze Hour - Review & Feynman Technique</div>
                        <div class="session-info">⏰ 1-1.5 hours | Review based on Ebbinghaus forgetting curve | Whiteboard coding, explain your approach</div>
                    </div>
                </div>
                <div class="question-list">
                    ${data.sessions.evening.map(q => renderQuestion(q)).join('')}
                </div>
            </div>
        `;
    }
    
    content.innerHTML = html;
    updateHeaderStats();
    updateDayCompletionStatus(data.day);
}

// Update completion status for a specific day
function updateDayCompletionStatus(day) {
    const dayButtons = document.querySelectorAll('.day-btn');
    dayButtons.forEach(btn => {
        const dayNumber = parseInt(btn.querySelector('.day-number')?.textContent);
        if (dayNumber === day) {
            checkDayCompletion(day).then(completed => {
                if (completed) {
                    btn.classList.add('completed');
                } else {
                    btn.classList.remove('completed');
                }
            });
        }
    });
}

// Render question card
function renderQuestion(q) {
    const completed = q.completed || false;
    const isWrong = completed && q.is_correct === false;
    const cardClass = completed ? (isWrong ? 'wrong' : 'completed') : '';
    const fromPrevious = q.from_previous_day || false;
    const forReview = q.for_review || false;
    
    // Build review badge text
    let reviewBadge = '';
    if (forReview) {
        if (completed && isCorrect !== false) {
            reviewBadge = '<span style="color: #4caf50; font-weight: bold; margin-right: 8px;">✓ Review Completed</span>';
        } else {
            if (q.review_interval) {
                reviewBadge = `<span style="color: #27ae60; font-weight: bold; margin-right: 8px;">📚 Review (${q.review_interval} day${q.review_interval > 1 ? 's' : ''} ago)</span>`;
            } else {
                reviewBadge = '<span style="color: #27ae60; font-weight: bold; margin-right: 8px;">📚 For Review</span>';
            }
        }
        if (q.is_correct === 0 && !completed) {
            reviewBadge += '<span style="color: #f44336; margin-left: 8px;">⚠️ Previously Wrong</span>';
        }
    }
    
    const hasNote = q.note && q.note.trim().length > 0;
    
    return `
        <div class="question-card ${cardClass} ${fromPrevious ? 'from-previous' : ''} ${forReview ? 'for-review' : ''}">
            <div class="question-info">
                <div class="question-title">
                    ${fromPrevious ? '<span style="color: #f39c12; font-weight: bold; margin-right: 8px;">⚠️ From Previous Day</span>' : ''}
                    ${reviewBadge}
                    <a href="https://leetcode.com/problems/${q.title.toLowerCase().replace(/\s+/g, '-')}/" 
                       target="_blank" style="text-decoration: none; color: inherit;">
                        ${q.title}
                    </a>
                    <span style="color: #999; margin-left: 10px;">#${q.leetcode_id}</span>
                    <button class="note-btn" onclick="toggleNote(${q.id})" title="Add/View Notes">
                        ${hasNote ? '📝' : '📄'}
                    </button>
                </div>
                <div class="question-meta">
                    <span class="difficulty ${q.difficulty.toLowerCase()}">${q.difficulty}</span>
                    <span>Category: ${q.category}</span>
                    ${forReview && q.completed_date ? `<span style="color: #666; margin-left: 10px;">Completed: ${q.completed_date}</span>` : ''}
                </div>
            </div>
            <div class="question-note" id="note-${q.id}" style="display: none;">
                <div class="note-header">
                    <strong>💡 Your Notes:</strong>
                    <button class="note-close-btn" onclick="toggleNote(${q.id})">×</button>
                </div>
                <textarea class="note-textarea" id="note-text-${q.id}" placeholder="Write your solution approach, key insights, or reminders here...">${q.note || ''}</textarea>
                <div class="note-actions">
                    <button class="action-btn btn-complete" onclick="saveNote(${q.id})">Save Note</button>
                </div>
                ${hasNote ? `<div class="note-preview">${q.note.replace(/\n/g, '<br>')}</div>` : ''}
            </div>
            <div class="question-actions">
                ${completed
                    ? `<button class="action-btn btn-undo" onclick="markIncomplete(${q.id})">Undo</button>`
                    : `<button class="action-btn btn-complete" onclick="markComplete(${q.id}, true)">${forReview ? 'Review Complete' : 'Complete'}</button>
                       <button class="action-btn btn-wrong" onclick="markComplete(${q.id}, false)">Wrong</button>
                       <button class="action-btn btn-defer" onclick="deferQuestion(${q.id})" title="Mark as 'Do Later'">⏰ Later</button>`
                }
            </div>
        </div>
    `;
}

// Mark as complete
async function markComplete(questionId, isCorrect) {
    try {
        const response = await fetch('/api/progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question_id: questionId,
                is_correct: isCorrect
            })
        });
        
        if (response.ok) {
            // Find the question card element by searching for the button that was clicked
            let questionCard = null;
            const allCards = document.querySelectorAll('.question-card');
            for (const card of allCards) {
                const actionsDiv = card.querySelector('.question-actions');
                if (actionsDiv) {
                    const buttons = actionsDiv.querySelectorAll('button');
                    for (const btn of buttons) {
                        if (btn.getAttribute('onclick') && btn.getAttribute('onclick').includes(`markComplete(${questionId}`)) {
                            questionCard = card;
                            break;
                        }
                    }
                }
                if (questionCard) break;
            }
            
            // Check if this is a review question
            const isReviewQuestion = questionCard && questionCard.classList.contains('for-review');
            
            if (isReviewQuestion && questionCard) {
                // For review questions, just update the UI without reloading
                updateQuestionCardStatus(questionCard, questionId, isCorrect);
            } else {
                // For regular questions, reload the day plan
                loadDay(currentDay);
            }
            
            loadStatistics();
            // Update completion status for current day
            updateDayCompletionStatus(currentDay);
        } else {
            alert('Update failed, please try again');
        }
    } catch (error) {
        console.error('Failed to mark complete:', error);
        alert('Operation failed, please try again');
    }
}

// Update question card status without reloading
function updateQuestionCardStatus(cardElement, questionId, isCorrect) {
    if (!cardElement) return;
    
    // Update card class
    cardElement.classList.remove('wrong', 'completed');
    if (isCorrect) {
        cardElement.classList.add('completed');
    } else {
        cardElement.classList.add('wrong');
    }
    
    // Update buttons - show Undo button for completed review questions
    const actionsDiv = cardElement.querySelector('.question-actions');
    if (actionsDiv) {
        actionsDiv.innerHTML = `
            <button class="action-btn btn-undo" onclick="markIncomplete(${questionId})">Undo</button>
        `;
    }
    
    // Update review badge to show completed status
    const titleDiv = cardElement.querySelector('.question-title');
    if (titleDiv && isCorrect) {
        // Add a checkmark or completed indicator
        const existingBadge = titleDiv.querySelector('.review-completed-badge');
        if (!existingBadge) {
            const completedBadge = document.createElement('span');
            completedBadge.className = 'review-completed-badge';
            completedBadge.style.cssText = 'color: #4caf50; font-weight: bold; margin-left: 8px;';
            completedBadge.textContent = '✓ Review Completed';
            titleDiv.appendChild(completedBadge);
        }
    }
}

// Mark as incomplete
async function markIncomplete(questionId) {
    try {
        const response = await fetch('/api/progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question_id: questionId,
                is_correct: null  // Indicates undo
            })
        });
        
        if (response.ok) {
            // Find the question card element
            let questionCard = null;
            const allCards = document.querySelectorAll('.question-card');
            for (const card of allCards) {
                const actionsDiv = card.querySelector('.question-actions');
                if (actionsDiv) {
                    const buttons = actionsDiv.querySelectorAll('button');
                    for (const btn of buttons) {
                        if (btn.getAttribute('onclick') && btn.getAttribute('onclick').includes(`markIncomplete(${questionId}`)) {
                            questionCard = card;
                            break;
                        }
                    }
                }
                if (questionCard) break;
            }
            
            // Check if this is a review question
            const isReviewQuestion = questionCard && questionCard.classList.contains('for-review');
            
            if (isReviewQuestion && questionCard) {
                // For review questions, restore the original buttons
                restoreQuestionCardButtons(questionCard, questionId);
            } else {
                // For regular questions, reload the day plan
                loadDay(currentDay);
            }
            
            loadStatistics();
            // Update completion status for current day
            updateDayCompletionStatus(currentDay);
        }
    } catch (error) {
        console.error('Failed to undo:', error);
    }
}

// Restore question card buttons after undo
function restoreQuestionCardButtons(cardElement, questionId) {
    if (!cardElement) return;
    
    // Remove completed class
    cardElement.classList.remove('wrong', 'completed');
    
    // Restore original buttons
    const actionsDiv = cardElement.querySelector('.question-actions');
    if (actionsDiv) {
        const isReview = cardElement.classList.contains('for-review');
        actionsDiv.innerHTML = `
            <button class="action-btn btn-complete" onclick="markComplete(${questionId}, true)">${isReview ? 'Review Complete' : 'Complete'}</button>
            <button class="action-btn btn-wrong" onclick="markComplete(${questionId}, false)">Wrong</button>
            <button class="action-btn btn-defer" onclick="deferQuestion(${questionId})" title="Mark as 'Do Later'">⏰ Later</button>
        `;
    }
    
    // Remove completed badge
    const titleDiv = cardElement.querySelector('.question-title');
    if (titleDiv) {
        const completedBadge = titleDiv.querySelector('.review-completed-badge');
        if (completedBadge) {
            completedBadge.remove();
        }
    }
}

// Defer question (mark as "do later")
async function deferQuestion(questionId) {
    try {
        const response = await fetch('/api/defer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question_id: questionId
            })
        });
        
        if (response.ok) {
            loadDay(currentDay);
            loadStatistics();
            alert('Question marked as "Do Later". It will be hidden from today\'s plan.');
        } else {
            alert('Failed to mark as "Do Later", please try again');
        }
    } catch (error) {
        console.error('Failed to defer question:', error);
        alert('Operation failed, please try again');
    }
}

// Load statistics
async function loadStatistics() {
    try {
        const response = await fetch('/api/statistics');
        statistics = await response.json();
        updateHeaderStats();
    } catch (error) {
        console.error('Failed to load statistics:', error);
    }
}

// Update header statistics
function updateHeaderStats() {
    if (statistics.total_questions) {
        const completed = statistics.total_completed || 0;
        const total = statistics.total_questions;
        
        document.getElementById('total-progress').textContent = `${completed}/${total}`;
        document.getElementById('streak-days').textContent = `${statistics.streak_days || 0} days`;
        
        if (statistics.total_correct && statistics.total_completed) {
            const accuracy = Math.round((statistics.total_correct / statistics.total_completed) * 100);
            document.getElementById('accuracy').textContent = `${accuracy}%`;
        } else {
            document.getElementById('accuracy').textContent = '0%';
        }
    }
}

// Show statistics
async function showStatistics() {
    await loadStatistics();
    const modal = document.getElementById('statistics-modal');
    const content = document.getElementById('statistics-content');
    
    let html = '<div class="statistics-grid">';
    
    html += `
        <div class="stat-box">
            <h3>Total Completed</h3>
            <div class="number">${statistics.total_completed || 0}</div>
        </div>
        <div class="stat-box">
            <h3>Correct</h3>
            <div class="number" style="color: #4caf50;">${statistics.total_correct || 0}</div>
        </div>
        <div class="stat-box">
            <h3>Wrong</h3>
            <div class="number" style="color: #f44336;">${statistics.total_wrong || 0}</div>
        </div>
        <div class="stat-box">
            <h3>Streak</h3>
            <div class="number">${statistics.streak_days || 0} days</div>
        </div>
    `;
    
    if (statistics.by_category) {
        html += '</div><h3 style="margin-top: 30px;">By Category</h3><ul style="list-style: none; padding: 0;">';
        for (const [category, count] of Object.entries(statistics.by_category)) {
            html += `<li style="padding: 10px; margin: 5px 0; background: #f8f9fa; border-radius: 5px;">
                ${category}: <strong>${count}</strong> problems
            </li>`;
        }
        html += '</ul>';
    }
    
    if (statistics.by_difficulty) {
        html += '<h3 style="margin-top: 30px;">By Difficulty</h3><ul style="list-style: none; padding: 0;">';
        for (const [difficulty, count] of Object.entries(statistics.by_difficulty)) {
            html += `<li style="padding: 10px; margin: 5px 0; background: #f8f9fa; border-radius: 5px;">
                ${difficulty}: <strong>${count}</strong> problems
            </li>`;
        }
        html += '</ul>';
    }
    
    content.innerHTML = html;
    modal.style.display = 'block';
}

// Show review list
async function showReview() {
    try {
        const response = await fetch('/api/review');
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Failed to load review list:', response.status, errorText);
            alert('Failed to load review list. Please try again.');
            return;
        }
        
        const reviewQuestions = await response.json();
        const modal = document.getElementById('review-modal');
        const content = document.getElementById('review-content');
        
        if (!Array.isArray(reviewQuestions)) {
            console.error('Invalid response format:', reviewQuestions);
            alert('Invalid response format. Please try again.');
            return;
        }
        
        if (reviewQuestions.length === 0) {
            content.innerHTML = '<p style="text-align: center; padding: 40px; color: #666;">✅ No questions to review today, keep it up!</p>';
        } else {
            let html = '<div class="review-list">';
            reviewQuestions.forEach(q => {
                html += `
                    <div class="review-item">
                        <div style="font-weight: bold; margin-bottom: 5px;">
                            <a href="https://leetcode.com/problems/${q.title.toLowerCase().replace(/\s+/g, '-')}/" 
                               target="_blank" style="text-decoration: none; color: #667eea;">
                                ${q.title}
                            </a>
                            <span class="difficulty ${q.difficulty.toLowerCase()}" style="margin-left: 10px;">${q.difficulty}</span>
                        </div>
                        <div style="color: #666; font-size: 0.9em;">
                            Category: ${q.category} | Completed: ${q.completed_date}
                            ${q.is_correct === 0 ? ' | <span style="color: #f44336;">⚠️ Previously Wrong</span>' : ''}
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            content.innerHTML = html;
        }
        
        modal.style.display = 'block';
    } catch (error) {
        console.error('Failed to load review list:', error);
        alert('Failed to load review list: ' + error.message);
    }
}

// Close modal
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Show deferred questions
async function showDeferred() {
    try {
        const response = await fetch('/api/deferred');
        const deferredQuestions = await response.json();
        const modal = document.getElementById('deferred-modal');
        const content = document.getElementById('deferred-content');
        
        if (deferredQuestions.length === 0) {
            content.innerHTML = '<p style="text-align: center; padding: 40px; color: #666;">✅ No questions marked as "Do Later"</p>';
        } else {
            let html = '<div class="review-list">';
            deferredQuestions.forEach(q => {
                html += `
                    <div class="review-item">
                        <div style="font-weight: bold; margin-bottom: 5px;">
                            <a href="https://leetcode.com/problems/${q.title.toLowerCase().replace(/\s+/g, '-')}/" 
                               target="_blank" style="text-decoration: none; color: #667eea;">
                                ${q.title}
                            </a>
                            <span class="difficulty ${q.difficulty.toLowerCase()}" style="margin-left: 10px;">${q.difficulty}</span>
                        </div>
                        <div style="color: #666; font-size: 0.9em; margin-bottom: 10px;">
                            Category: ${q.category} | Day ${q.day_number}
                            ${q.deferred_date ? ` | Deferred: ${q.deferred_date}` : ''}
                            ${q.completed ? ` | <span style="color: #4caf50;">Completed</span>` : ''}
                        </div>
                        <div>
                            <button class="action-btn btn-complete" onclick="undeferQuestion(${q.id})" style="margin-right: 10px;">Restore</button>
                            ${!q.completed ? `<button class="action-btn btn-complete" onclick="undeferAndComplete(${q.id}, true)">Restore & Complete</button>` : ''}
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            content.innerHTML = html;
        }
        
        modal.style.display = 'block';
    } catch (error) {
        console.error('Failed to load deferred list:', error);
        alert('Failed to load "Do Later" list');
    }
}

// Undefer question (restore to plan)
async function undeferQuestion(questionId) {
    try {
        const response = await fetch('/api/undefer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question_id: questionId
            })
        });
        
        if (response.ok) {
            showDeferred(); // Refresh the list
            loadDay(currentDay); // Refresh current day plan
            alert('Question restored to your plan');
        } else {
            alert('Failed to restore question, please try again');
        }
    } catch (error) {
        console.error('Failed to undefer question:', error);
        alert('Operation failed, please try again');
    }
}

// Undefer and mark as complete
async function undeferAndComplete(questionId, isCorrect) {
    try {
        // First undefer
        const undeferResponse = await fetch('/api/undefer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question_id: questionId
            })
        });
        
        if (undeferResponse.ok) {
            // Then mark as complete
            await markComplete(questionId, isCorrect);
            showDeferred(); // Refresh the list
        }
    } catch (error) {
        console.error('Failed to undefer and complete:', error);
        alert('Operation failed, please try again');
    }
}

// Toggle note editor
function toggleNote(questionId) {
    const noteDiv = document.getElementById(`note-${questionId}`);
    if (noteDiv) {
        const isVisible = noteDiv.style.display !== 'none';
        noteDiv.style.display = isVisible ? 'none' : 'block';
        
        // If opening, focus on textarea
        if (!isVisible) {
            setTimeout(() => {
                const textarea = document.getElementById(`note-text-${questionId}`);
                if (textarea) {
                    textarea.focus();
                }
            }, 100);
        }
    }
}

// Save note
async function saveNote(questionId) {
    const textarea = document.getElementById(`note-text-${questionId}`);
    if (!textarea) return;
    
    const note = textarea.value;
    
    try {
        const response = await fetch(`/api/note/${questionId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ note: note })
        });
        
        if (response.ok) {
            // Update the note preview
            const noteDiv = document.getElementById(`note-${questionId}`);
            const previewDiv = noteDiv.querySelector('.note-preview');
            if (note.trim()) {
                if (previewDiv) {
                    previewDiv.innerHTML = note.replace(/\n/g, '<br>');
                } else {
                    const preview = document.createElement('div');
                    preview.className = 'note-preview';
                    preview.innerHTML = note.replace(/\n/g, '<br>');
                    noteDiv.querySelector('.note-actions').after(preview);
                }
            } else {
                if (previewDiv) {
                    previewDiv.remove();
                }
            }
            
            // Update note button icon
            const noteBtn = noteDiv.parentElement.querySelector('.note-btn');
            if (noteBtn) {
                noteBtn.textContent = note.trim() ? '📝' : '📄';
            }
            
            // Show success message briefly
            const saveBtn = noteDiv.querySelector('.note-actions button');
            const originalText = saveBtn.textContent;
            saveBtn.textContent = '✓ Saved!';
            saveBtn.style.background = '#4caf50';
            setTimeout(() => {
                saveBtn.textContent = originalText;
                saveBtn.style.background = '';
            }, 1500);
        } else {
            alert('Failed to save note, please try again');
        }
    } catch (error) {
        console.error('Failed to save note:', error);
        alert('Failed to save note, please try again');
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}
