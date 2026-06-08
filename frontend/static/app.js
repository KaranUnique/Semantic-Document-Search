const BACKEND_URL = 'http://127.0.0.1:8000';

// ── STATE ─────────────────────────────────────────────────────────────────────
const state = {
  activePage: 'home',
  chatHistory: [],       // shared between home and chat page
  pendingFiles: [],
};

// ── NAVIGATION ────────────────────────────────────────────────────────────────
function navigate(page) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

  const pageEl = document.getElementById(`page-${page}`);
  if (pageEl) pageEl.classList.add('active');

  document.querySelectorAll(`.nav-btn[data-page="${page}"]`).forEach(b => b.classList.add('active'));
  state.activePage = page;

  if (page === 'home')    { loadDocuments(); renderHomeChatHistory(); }
  if (page === 'summary') loadSummaryDocs();
}

document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', () => navigate(btn.dataset.page));
});

// ── HELPER: format file size ──────────────────────────────────────────────────
function formatSize(bytes) {
  if (bytes >= 1048576) return (bytes / 1048576).toFixed(1) + ' MB';
  if (bytes >= 1024)    return Math.round(bytes / 1024) + ' KB';
  return bytes + ' B';
}

// ── HELPER: file icon ─────────────────────────────────────────────────────────
function fileIcon(ext) {
  const e = ext.toLowerCase();
  if (e.includes('.pdf'))  return { cls: 'ficon-pdf',  icon: '📄' };
  if (e.includes('.docx')) return { cls: 'ficon-docx', icon: '📝' };
  if (e.includes('.pptx')) return { cls: 'ficon-pptx', icon: '📊' };
  if (e.includes('.md'))   return { cls: 'ficon-md',   icon: '📋' };
  return { cls: 'ficon-txt', icon: '📃' };
}

// ── HELPER: status message ────────────────────────────────────────────────────
function showStatus(containerId, msg, type = 'info') {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = `<div class="status-msg status-${type}">${msg}</div>`;
}

// ── LOAD DOCUMENTS ────────────────────────────────────────────────────────────
async function loadDocuments() {
  const tbody = document.getElementById('doc-table-body');
  try {
    const res = await fetch(`${BACKEND_URL}/documents`);
    if (!res.ok) throw new Error('Failed to load documents');
    const docs = await res.json();

    if (!docs.length) {
      tbody.innerHTML = `<tr><td colspan="4" class="empty-cell">No documents yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = docs.map(doc => {
      const { cls, icon } = fileIcon(doc.file_type || '');
      const added = doc.uploaded_at ? doc.uploaded_at.slice(0, 10) : '—';
      return `
        <tr>
          <td>
            <div class="fname-cell">
              <div class="ficon ${cls}">${icon}</div>
              <span>${doc.name}</span>
            </div>
          </td>
          <td><span class="badge badge-indexed">Indexed</span></td>
          <td style="color:var(--t2);font-size:13px;">${added}</td>
          <td style="color:var(--t2);font-size:13px;">${formatSize(doc.size_bytes || 0)}</td>
        </tr>`;
    }).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="4" class="empty-cell">Error loading documents.</td></tr>`;
  }
}

// ── FILE UPLOAD ───────────────────────────────────────────────────────────────
const dropzone   = document.getElementById('dropzone');
const fileInput  = document.getElementById('file-input');
const uploadBtn  = document.getElementById('upload-btn');
const readyMsg   = document.getElementById('file-ready-msg');

dropzone.addEventListener('click', (e) => {
  if (e.target === uploadBtn || uploadBtn.contains(e.target)) return;
  fileInput.click();
});

dropzone.addEventListener('dragover', e => { e.preventDefault(); dropzone.classList.add('drag-over'); });
dropzone.addEventListener('dragleave', ()  => dropzone.classList.remove('drag-over'));
dropzone.addEventListener('drop', e => {
  e.preventDefault();
  dropzone.classList.remove('drag-over');
  handleFiles(Array.from(e.dataTransfer.files));
});

fileInput.addEventListener('change', () => handleFiles(Array.from(fileInput.files)));

function handleFiles(files) {
  const valid = files.filter(f => f.size / 1048576 <= 10);
  const skipped = files.length - valid.length;
  state.pendingFiles = valid;

  if (skipped) showStatus('upload-status', `${skipped} file(s) exceed 10 MB and were skipped.`, 'error');

  if (valid.length) {
    const names = valid.map(f => f.name).join(', ');
    readyMsg.textContent = valid.length === 1
      ? `Ready: ${names}`
      : `${valid.length} files ready: ${names}`;
    readyMsg.classList.remove('hidden');
    uploadBtn.classList.remove('hidden');
  } else {
    readyMsg.classList.add('hidden');
    uploadBtn.classList.add('hidden');
  }
}

uploadBtn.addEventListener('click', async (e) => {
  e.stopPropagation(); // prevent bubbling to dropzone
  if (!state.pendingFiles.length) return;
  uploadBtn.disabled = true;
  uploadBtn.innerHTML = '<span class="spinner"></span>Processing…';
  document.getElementById('upload-status').innerHTML = '';

  const formData = new FormData();
  state.pendingFiles.forEach(f => formData.append('files', f));

  try {
    const res = await fetch(`${BACKEND_URL}/documents/upload`, { method: 'POST', body: formData });
    if (!res.ok) {
      let detail = 'Upload failed';
      try { detail = (await res.json()).detail || detail; } catch (_) {}
      throw new Error(detail);
    }
    const results = await res.json();
    showStatus('upload-status', `✓ Processed ${results.length} document(s).`, 'success');
    state.pendingFiles = [];
    readyMsg.classList.add('hidden');
    uploadBtn.classList.add('hidden');
    fileInput.value = '';
    loadDocuments();
  } catch (err) {
    const msg = err.message.includes('Failed to fetch')
      ? 'Cannot reach backend. Is it running at http://127.0.0.1:8000?'
      : err.message;
    showStatus('upload-status', `Upload failed: ${msg}`, 'error');
  } finally {
    uploadBtn.disabled = false;
    uploadBtn.textContent = 'Process & Upload';
  }
});

// ── CHAT HELPERS ──────────────────────────────────────────────────────────────
function buildChatBubbles(history) {
  return history.map(msg => {
    if (msg.role === 'assistant') {
      let html = `
        <div class="chat-row ai">
          <div class="chat-av-ai">🎙</div>
          <div>
            <div class="chat-bubble ai-bubble">${escapeHtml(msg.content)}</div>
            <div class="chat-ts">Just now</div>
          </div>
        </div>`;
      if (msg.citations && msg.citations.length) {
        const chips = msg.citations.map(c =>
          `<span class="c-chip">
            <span class="c-idx">${c.index}</span>
            ${escapeHtml(c.source)} p.${c.page}
            <span class="c-score">${c.relevance_score}%</span>
          </span>`
        ).join('');
        html += `<div class="citations-row">${chips}</div>`;
      }
      return html;
    } else {
      return `
        <div class="chat-row user">
          <div class="chat-av-user">MT</div>
          <div>
            <div class="chat-bubble user-bubble">${escapeHtml(msg.content)}</div>
          </div>
        </div>`;
    }
  }).join('');
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function scrollToBottom(el) {
  el.scrollTop = el.scrollHeight;
}

// ── HOME CHAT ─────────────────────────────────────────────────────────────────
function renderHomeChatHistory() {
  const container = document.getElementById('home-chat-messages');
  if (!state.chatHistory.length) {
    container.innerHTML = `
      <div class="chat-row ai">
        <div class="chat-av-ai">🎙</div>
        <div>
          <div class="chat-bubble ai-bubble">Hello! I'm ready to answer questions about your knowledge base. Upload documents on the left to get started.</div>
          <div class="chat-ts">Just now</div>
        </div>
      </div>`;
  } else {
    container.innerHTML = buildChatBubbles(state.chatHistory);
  }
  scrollToBottom(container);
}

async function sendChatMessage(inputId, containerId) {
  const input = document.getElementById(inputId);
  const query = input.value.trim();
  if (!query) return;
  input.value = '';

  state.chatHistory.push({ role: 'user', content: query });

  // Reflect in both views
  renderHomeChatHistory();
  renderFullChatHistory();

  try {
    const formData = new FormData();
    formData.append('query', query);

    const res = await fetch(`${BACKEND_URL}/chat`, { method: 'POST', body: formData });
    if (!res.ok) throw new Error('Chat request failed');

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let fullText = '';
    let citations = [];
    let firstChunk = true;

    // Add a placeholder assistant message
    state.chatHistory.push({ role: 'assistant', content: '…', citations: [] });
    const msgIdx = state.chatHistory.length - 1;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });

      if (firstChunk && chunk.includes('[SOURCES_METADATA]:')) {
        const lines = chunk.split('\n');
        const metaLine = lines[0].replace('[SOURCES_METADATA]:', '').trim();
        try { citations = JSON.parse(metaLine); } catch (_) {}
        fullText += lines.slice(1).join('\n');
        firstChunk = false;
      } else {
        fullText += chunk;
        firstChunk = false;
      }

      state.chatHistory[msgIdx] = { role: 'assistant', content: fullText, citations };
      renderHomeChatHistory();
      renderFullChatHistory();
    }
  } catch (err) {
    state.chatHistory.push({ role: 'assistant', content: `Error: ${err.message}`, citations: [] });
    renderHomeChatHistory();
    renderFullChatHistory();
  }
}

document.getElementById('home-send-btn').addEventListener('click', () =>
  sendChatMessage('home-chat-input', 'home-chat-messages'));
document.getElementById('home-chat-input').addEventListener('keydown', e => {
  if (e.key === 'Enter') sendChatMessage('home-chat-input', 'home-chat-messages');
});

// ── FULL CHAT PAGE ─────────────────────────────────────────────────────────────
function renderFullChatHistory() {
  const container = document.getElementById('chat-messages');
  if (!state.chatHistory.length) {
    container.innerHTML = `
      <div class="chat-row ai">
        <div class="chat-av-ai">🎙</div>
        <div>
          <div class="chat-bubble ai-bubble">Hello! I'm ready to answer questions about your knowledge base. Upload documents first, then ask me anything.</div>
          <div class="chat-ts">Just now</div>
        </div>
      </div>`;
  } else {
    container.innerHTML = buildChatBubbles(state.chatHistory);
  }
  scrollToBottom(container);
}

document.getElementById('chat-send-btn').addEventListener('click', () =>
  sendChatMessage('chat-input', 'chat-messages'));
document.getElementById('chat-input').addEventListener('keydown', e => {
  if (e.key === 'Enter') sendChatMessage('chat-input', 'chat-messages');
});

document.getElementById('clear-chat-btn').addEventListener('click', () => {
  state.chatHistory = [];
  renderFullChatHistory();
  renderHomeChatHistory();
});

// ── SEMANTIC SEARCH ────────────────────────────────────────────────────────────
document.getElementById('search-btn').addEventListener('click', doSearch);
document.getElementById('search-input').addEventListener('keydown', e => {
  if (e.key === 'Enter') doSearch();
});

async function doSearch() {
  const query = document.getElementById('search-input').value.trim();
  const topK  = document.getElementById('search-top-k').value;
  const out   = document.getElementById('search-results');

  if (!query) {
    out.innerHTML = `<div class="status-msg status-error">Enter a search term first.</div>`;
    return;
  }

  out.innerHTML = `<div class="status-msg status-info"><span class="spinner"></span>Searching…</div>`;

  try {
    const formData = new FormData();
    formData.append('query', query);
    formData.append('top_k', topK);

    const res = await fetch(`${BACKEND_URL}/rag/semantic-search`, { method: 'POST', body: formData });
    if (!res.ok) throw new Error('Search failed');
    const results = await res.json();

    if (!results.length) {
      out.innerHTML = `<div class="panel" style="padding:40px;text-align:center;color:var(--t3);font-size:13.5px;">No matching passages found.</div>`;
      return;
    }

    const countHtml = `<p style="font-size:13px;color:var(--t3);margin-bottom:12px;">
      <span style="color:var(--t1);font-weight:600;">${results.length}</span> passages found</p>`;

    const cardsHtml = results.map((r, idx) => {
      const ext = (r.file_type || '').toLowerCase();
      let typeLabel, typeBg, typeColor;
      if (ext.includes('.pdf'))       { typeLabel='PDF';  typeBg='#FEE2E2'; typeColor='#991B1B'; }
      else if (ext.includes('.docx')) { typeLabel='DOCX'; typeBg='#DBEAFE'; typeColor='#1E40AF'; }
      else if (ext.includes('.pptx')) { typeLabel='PPTX'; typeBg='#FFEDD5'; typeColor='#9A3412'; }
      else { typeLabel = ext.replace('.','').toUpperCase() || 'TXT'; typeBg='#F1F5F9'; typeColor='#475569'; }

      return `
        <div class="search-result">
          <div class="sr-header">
            <div class="sr-left">
              <span class="sr-idx">${idx+1}</span>
              <span class="sr-name">${escapeHtml(r.source)}</span>
              <span class="sr-type" style="background:${typeBg};color:${typeColor};">${typeLabel}</span>
              <span class="sr-page">p. ${r.page}</span>
            </div>
            <span class="sr-score">${r.relevance_score}% match</span>
          </div>
          <div class="sr-text">${escapeHtml(r.text)}</div>
        </div>`;
    }).join('');

    out.innerHTML = countHtml + cardsHtml;
  } catch (err) {
    out.innerHTML = `<div class="status-msg status-error">Search failed: ${err.message}</div>`;
  }
}

// ── SUMMARIES ──────────────────────────────────────────────────────────────────
async function loadSummaryDocs() {
  const sel = document.getElementById('summary-doc-select');
  try {
    const res = await fetch(`${BACKEND_URL}/documents`);
    const docs = await res.json();
    if (!docs.length) {
      sel.innerHTML = `<option value="">No documents uploaded yet</option>`;
      return;
    }
    sel.innerHTML = docs.map(d => `<option value="${d.name}">${escapeHtml(d.name)}</option>`).join('');
  } catch {
    sel.innerHTML = `<option value="">Failed to load documents</option>`;
  }
}

document.getElementById('summary-btn').addEventListener('click', async () => {
  const docName = document.getElementById('summary-doc-select').value;
  const out = document.getElementById('summary-output');
  if (!docName) return;

  out.innerHTML = `<div class="status-msg status-info"><span class="spinner"></span>Generating summary for <strong>${escapeHtml(docName)}</strong>…</div>`;

  try {
    const res = await fetch(`${BACKEND_URL}/rag/summarize/${encodeURIComponent(docName)}`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to generate summary');

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let fullSummary = '';

    out.innerHTML = `<div class="summary-content" id="summary-text"></div>`;
    const summaryEl = document.getElementById('summary-text');

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      fullSummary += decoder.decode(value, { stream: true });
      summaryEl.textContent = fullSummary;
    }

    // Download button
    out.innerHTML += `
      <div style="display:flex;gap:10px;margin-top:12px;align-items:center;">
        <div class="status-msg status-success" style="margin:0;">Summary generated.</div>
        <button class="btn-primary" onclick="downloadSummary('${escapeHtml(docName)}')">Download (.md)</button>
      </div>`;
    out._summaryText = fullSummary;
    out._docName = docName;
  } catch (err) {
    out.innerHTML = `<div class="status-msg status-error">Summary failed: ${err.message}</div>`;
  }
});

function downloadSummary(docName) {
  const out = document.getElementById('summary-output');
  const text = out._summaryText || '';
  const blob = new Blob([text], { type: 'text/markdown' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = docName.replace(/\.[^.]+$/, '') + '_summary.md';
  a.click();
  URL.revokeObjectURL(a.href);
}

// ── INIT ──────────────────────────────────────────────────────────────────────
navigate('home');

// ── MOBILE SIDEBAR TOGGLE ─────────────────────────────────────────────────────
const hamburger = document.getElementById('hamburger');
const sidebar   = document.querySelector('.sidebar');
const overlay   = document.getElementById('sidebar-overlay');

function openSidebar() {
  sidebar.classList.add('open');
  overlay.classList.add('visible');
  hamburger.classList.add('open');
}
function closeSidebar() {
  sidebar.classList.remove('open');
  overlay.classList.remove('visible');
  hamburger.classList.remove('open');
}

hamburger.addEventListener('click', () =>
  sidebar.classList.contains('open') ? closeSidebar() : openSidebar()
);
overlay.addEventListener('click', closeSidebar);

// Close sidebar on nav click (mobile)
document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    if (window.innerWidth <= 900) closeSidebar();
  });
});

// ── WELCOME MODAL ─────────────────────────────────────────────────────────────
document.getElementById('modal-continue').addEventListener('click', () => {
  document.getElementById('welcome-backdrop').classList.add('hidden');
});
