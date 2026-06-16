
function generateUUID() {
  try {
    // Works on HTTPS / localhost
    return crypto.randomUUID();
  } catch {
    // Fallback for HTTP (manual UUID generation)
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }
}

const SESSION_ID = (() => {
  const existing = sessionStorage.getItem('session_id');
  if (existing) return existing;
  const id = generateUUID(); // ✅ uses fallback if needed
  sessionStorage.setItem('session_id', id);
  return id;
})();

let eventSource = null;
let lastQuery = ''; // ✅ store for retry

async function startResearch() {
  const query = document.getElementById('queryInput').value.trim();

  // ✅ Validate query before sending
  if (!query) {
    showError('Please enter a research question.');
    return;
  }
  if (query.length < 5) {
    showError('Query is too short — please be more specific.');
    return;
  }

  lastQuery = query;
  hideError();
  resetUI();

  document.getElementById('searchBtn').disabled = true;
  document.getElementById('searchBtn').innerHTML = '<span class="spinner"></span>';
  document.getElementById('activityPanel').style.display = 'block';

  if (eventSource) eventSource.close();

  try {
    const res = await fetch('/research', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, session_id: SESSION_ID }),
    });

    // ✅ Handle HTTP errors from server
    if (!res.ok) {
      const data = await res.json();
      showError(data.error || `Server error (${res.status})`);
      resetButton();
      return;
    }
  } catch (err) {
    // ✅ Handle network errors (server down etc.)
    showError('Cannot connect to server. Is the backend running?');
    resetButton();
    return;
  }

  // Open SSE stream
  eventSource = new EventSource(`/stream/${SESSION_ID}`);

  // ✅ Timeout — show message if no response in 90s
  const timeout = setTimeout(() => {
    if (eventSource) {
      eventSource.close();
      addActivity('error', '⏱ Research is taking too long — please try again.');
      showError('Request timed out. Try a simpler question.');
      resetButton();
    }
  }, 90000);

  eventSource.onmessage = (e) => {
    try {
      const event = JSON.parse(e.data);
      handleEvent(event, timeout);
    } catch (err) {
      showError('Received malformed response from server.');
      resetButton();
      clearTimeout(timeout);
      eventSource.close();
    }
  };

  eventSource.onerror = () => {
    clearTimeout(timeout);
    // ✅ Only show error if we haven't completed successfully
    if (document.getElementById('searchBtn').disabled) {
      showError('Connection lost. Please try again.');
      addActivity('error', '❌ Connection error');
      resetButton();
    }
    eventSource.close();
  };
}

function handleEvent(event, timeout) {
  if (event.type === 'status') {
    addActivity('status', event.message);
  } else if (event.type === 'tool_start') {
    addActivity('tool_start', `🔧 ${event.tool} → "${event.input}"`);
  } else if (event.type === 'tool_end') {
    addActivity('tool_end', '✓ Tool completed');
  } else if (event.type === 'report') {
    showReport(event.message);
  } else if (event.type === 'done') {
    clearTimeout(timeout);
    addActivity('status', '✅ Research complete');
    resetButton();
    updateMemoryBadge();
    eventSource.close();
  } else if (event.type === 'error') {
    clearTimeout(timeout);
    // ✅ Show error in both activity feed and banner
    addActivity('error', `❌ ${event.message}`);
    showError(event.message);
    resetButton();
    eventSource.close();
  }
}

function showError(message) {
  const banner = document.getElementById('errorBanner');
  document.getElementById('errorMessage').textContent = message;
  banner.style.display = 'block';
}

function hideError() {
  document.getElementById('errorBanner').style.display = 'none';
}

// ✅ Retry last query with one click
function retry() {
  if (!lastQuery) return;
  document.getElementById('queryInput').value = lastQuery;
  hideError();
  startResearch();
}

function resetUI() {
  document.getElementById('activity').innerHTML = '';
  document.getElementById('report').innerHTML = '';
  document.getElementById('report').style.display = 'none';
  document.getElementById('reportPanel').style.display = 'none';
}

function addActivity(type, message) {
  const feed = document.getElementById('activity');

  // ✅ Remove empty state if present
  const empty = feed.querySelector('.empty-state');
  if (empty) empty.remove();

  const item = document.createElement('div');
  item.className = `activity-item ${type}`;
  item.innerHTML = `<span class="dot"></span><span>${message}</span>`;
  feed.appendChild(item);
  feed.scrollTop = feed.scrollHeight;
}

function showReport(text) {
  document.getElementById('reportPanel').style.display = 'block';
  const reportEl = document.getElementById('report');
  reportEl.style.display = 'block';
  reportEl.innerHTML = text
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/\[(.+?)\]\((https?:\/\/.+?)\)/g, '<a href="$2" target="_blank">$1</a>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/\n/g, '<br>');
}

async function clearMemory() {
  await fetch('/clear', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: SESSION_ID }),
  });
  resetUI();
  hideError();
  document.getElementById('activityPanel').style.display = 'none';
  document.getElementById('memoryBadge').textContent = 'Memory cleared';
}

async function showMemory() {
  try {
    const res = await fetch('/memory');
    const data = await res.json();
    document.getElementById('memoryBadge').textContent = `💾 ${data.chunks} chunks stored in vector memory`;
  } catch {
    document.getElementById('memoryBadge').textContent = 'Could not fetch memory status';
  }
}

async function updateMemoryBadge() {
  try {
    const res = await fetch('/memory');
    const data = await res.json();
    document.getElementById('memoryBadge').textContent = `💾 ${data.chunks} chunks stored in vector memory`;
  } catch {
    // silent fail
  }
}

function copyReport() {
  const reportEl = document.getElementById('report');
  const text = reportEl.innerText; // plain text, no HTML tags

  navigator.clipboard
    .writeText(text)
    .then(() => {
      const btn = document.getElementById('copyBtn');
      btn.textContent = '✅ Copied!';
      btn.classList.add('copied');
      setTimeout(() => {
        btn.textContent = '📋 Copy';
        btn.classList.remove('copied');
      }, 2000);
    })
    .catch(() => {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
    });
}

document.getElementById('queryInput').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') startResearch();
});

function resetButton() {
  const btn = document.getElementById('searchBtn');
  btn.disabled = false;
  btn.innerHTML = 'Research';
}