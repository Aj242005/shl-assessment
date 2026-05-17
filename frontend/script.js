const API_BASE_URL = 'https://shl-assessment.duckdns.org';

const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const healthStatus = document.getElementById('health-status');
const statusDot = document.querySelector('.status-dot');

let conversationHistory = [];

async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            healthStatus.textContent = 'Backend Online';
            statusDot.classList.add('online');
            statusDot.classList.remove('offline');
            return true;
        }
    } catch (error) {
        console.error('Health check failed:', error);
    }
    
    healthStatus.textContent = 'Backend Offline';
    statusDot.classList.add('offline');
    statusDot.classList.remove('online');
    return false;
}

checkHealth();
setInterval(checkHealth, 10000);

function appendMessage(role, content) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const paragraphs = content.split('\n').filter(p => p.trim() !== '');
    paragraphs.forEach(p => {
        const pEl = document.createElement('p');
        pEl.textContent = p;
        contentDiv.appendChild(pEl);
    });
    
    msgDiv.appendChild(contentDiv);
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendRecommendations(recs) {
    if (!recs || recs.length === 0) return;
    
    const gridDiv = document.createElement('div');
    gridDiv.className = 'recommendations-grid';
    
    recs.forEach(rec => {
        const card = document.createElement('div');
        card.className = 'rec-card';
        
        card.innerHTML = `
            <div class="rec-title">${rec.name}</div>
            <div class="rec-meta">
                <span class="test-type">${rec.test_type}</span>
                <a href="${rec.url}" target="_blank" class="rec-link">View Catalog ↗</a>
            </div>
        `;
        
        gridDiv.appendChild(card);
    });
    
    const lastMsg = chatMessages.lastElementChild;
    if (lastMsg && lastMsg.classList.contains('assistant')) {
        lastMsg.appendChild(gridDiv);
    } else {
        chatMessages.appendChild(gridDiv);
    }
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTyping() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.id = 'typing';
    typingDiv.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    userInput.disabled = true;
    sendButton.disabled = true;
}

function removeTyping() {
    const typingDiv = document.getElementById('typing');
    if (typingDiv) {
        typingDiv.remove();
    }
    
    userInput.disabled = false;
    sendButton.disabled = false;
    userInput.focus();
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const text = userInput.value.trim();
    if (!text) return;
    
    appendMessage('user', text);
    userInput.value = '';
    
    conversationHistory.push({ role: 'user', content: text });
    
    showTyping();
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ messages: conversationHistory })
        });
        
        removeTyping();
        
        if (!response.ok) {
            throw new Error(`API returned ${response.status}`);
        }
        
        const data = await response.json();
        
        appendMessage('assistant', data.reply);
        
        conversationHistory.push({ role: 'assistant', content: data.reply });
        
        if (data.recommendations && data.recommendations.length > 0) {
            appendRecommendations(data.recommendations);
        }
        
        if (data.end_of_conversation) {
            const endMsg = document.createElement('div');
            endMsg.style.textAlign = 'center';
            endMsg.style.color = 'var(--text-muted)';
            endMsg.style.fontSize = '0.8rem';
            endMsg.style.marginTop = '16px';
            endMsg.textContent = '— Conversation Ended —';
            chatMessages.appendChild(endMsg);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            conversationHistory = [];
        }
        
    } catch (error) {
        removeTyping();
        console.error('Chat error:', error);
        appendMessage('assistant', 'Sorry, I encountered an error communicating with the server. Please try again.');
    }
});
