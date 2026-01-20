/**
 * AI-Ready File Converter
 * Frontend JavaScript for file uploads, conversion, and downloads
 */

// State
const state = {
    files: new Map(),
    sessionId: null,
    isConverting: false
};

// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const queueSection = document.getElementById('queueSection');
const fileList = document.getElementById('fileList');
const resultsSection = document.getElementById('resultsSection');
const resultsList = document.getElementById('resultsList');
const convertBtn = document.getElementById('convertBtn');
const clearAllBtn = document.getElementById('clearAllBtn');
const downloadAllBtn = document.getElementById('downloadAllBtn');
const previewModal = document.getElementById('previewModal');
const modalBackdrop = document.getElementById('modalBackdrop');
const modalClose = document.getElementById('modalClose');
const previewTitle = document.getElementById('previewTitle');
const previewContent = document.getElementById('previewContent');
const previewDownloadBtn = document.getElementById('previewDownloadBtn');
const previewCopyBtn = document.getElementById('previewCopyBtn');

// File type icons
const FILE_ICONS = {
    pdf: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>`,
    docx: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>`,
    xlsx: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><rect x="8" y="12" width="8" height="6" rx="1"/></svg>`,
    pptx: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><circle cx="12" cy="15" r="3"/></svg>`,
    image: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>`,
    markdown: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><path d="M7 15v-4l2 2 2-2v4"/><path d="M15 13l2 2 2-2"/><line x1="17" y1="11" x2="17" y2="15"/></svg>`,
    default: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>`
};

// Theme Management
const themeToggle = document.getElementById('themeToggle');

function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'system';
    applyTheme(savedTheme);
    updateThemeButtons(savedTheme);
}

function applyTheme(theme) {
    const html = document.documentElement;
    
    if (theme === 'system') {
        // Use system preference
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        html.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    } else {
        html.setAttribute('data-theme', theme);
    }
}

function updateThemeButtons(activeTheme) {
    const buttons = themeToggle.querySelectorAll('.theme-btn');
    buttons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.theme === activeTheme);
    });
}

function handleThemeChange(e) {
    const btn = e.target.closest('.theme-btn');
    if (!btn) return;
    
    const theme = btn.dataset.theme;
    localStorage.setItem('theme', theme);
    applyTheme(theme);
    updateThemeButtons(theme);
}

// Listen for system theme changes
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    const savedTheme = localStorage.getItem('theme') || 'system';
    if (savedTheme === 'system') {
        applyTheme('system');
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', init);

async function init() {
    initTheme();
    setupEventListeners();
    await initSession();
}

function setupEventListeners() {
    // Theme toggle
    themeToggle.addEventListener('click', handleThemeChange);
    
    // Drop zone events
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);
    fileInput.addEventListener('change', handleFileSelect);
    
    // Button events
    convertBtn.addEventListener('click', handleConvert);
    clearAllBtn.addEventListener('click', handleClearAll);
    downloadAllBtn.addEventListener('click', handleDownloadAll);
    
    // Modal events
    modalBackdrop.addEventListener('click', closeModal);
    modalClose.addEventListener('click', closeModal);
    previewCopyBtn.addEventListener('click', handleCopyPreview);
    
    // Keyboard events
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });
}

async function initSession() {
    try {
        const response = await fetch('/api/session');
        const data = await response.json();
        state.sessionId = data.session_id;
        
        // Restore files if any
        if (data.files && data.files.length > 0) {
            data.files.forEach(file => {
                state.files.set(file.id, file);
            });
            updateUI();
        }
    } catch (error) {
        console.error('Failed to initialize session:', error);
    }
}

// Drag and drop handlers
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('dragover');
    
    // Convert FileList to Array to avoid live reference issues
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
        uploadFiles(files);
    }
}

function handleFileSelect(e) {
    // Convert FileList to Array before clearing the input
    // FileList is a live reference that gets emptied when input is cleared
    const files = Array.from(e.target.files);
    
    // Reset input so same file can be selected again
    fileInput.value = '';
    
    if (files.length > 0) {
        uploadFiles(files);
    }
}

// Constants
const MAX_BATCH_SIZE = 10 * 1024 * 1024; // 10MB total

async function uploadFiles(files) {
    // Calculate total size of all files
    let totalSize = 0;
    for (const file of files) {
        totalSize += file.size;
    }
    
    // Check if total exceeds limit
    if (totalSize > MAX_BATCH_SIZE) {
        showError(`Total file size (${formatFileSize(totalSize)}) exceeds the 10MB limit. Please select fewer or smaller files.`);
        return;
    }
    
    // Upload all files
    for (const file of files) {
        await uploadFile(file);
    }
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            showError(error.detail || 'Upload failed');
            return;
        }
        
        const data = await response.json();
        state.files.set(data.file.id, data.file);
        updateUI();
        
    } catch (error) {
        console.error('Upload error:', error);
        showError('Failed to upload file');
    }
}

function updateUI() {
    const hasFiles = state.files.size > 0;
    const hasConverted = Array.from(state.files.values()).some(f => f.status === 'converted');
    const convertedCount = Array.from(state.files.values()).filter(f => f.status === 'converted').length;
    
    // Show/hide sections
    queueSection.classList.toggle('visible', hasFiles);
    resultsSection.classList.toggle('visible', hasConverted);
    
    // Update file list
    renderFileList();
    
    // Update results list - show ZIP download for multiple files, individual for single
    if (hasConverted) {
        if (convertedCount > 1) {
            renderZipResult();
        } else {
            renderResultsList();
        }
    }
    
    // Update convert button
    const uploadedCount = Array.from(state.files.values()).filter(f => f.status === 'uploaded').length;
    convertBtn.disabled = uploadedCount === 0 || state.isConverting;
    convertBtn.querySelector('span').textContent = uploadedCount > 0 
        ? `Convert ${uploadedCount} File${uploadedCount !== 1 ? 's' : ''}`
        : 'Convert All';
    
    // Update output indicator in queue section
    updateOutputIndicator();
}

function renderFileList() {
    const files = Array.from(state.files.values()).filter(f => f.status !== 'converted');
    
    if (files.length === 0) {
        fileList.innerHTML = '<p class="empty-message">No files to convert</p>';
        return;
    }
    
    fileList.innerHTML = files.map(file => {
        const isReverse = isReverseConversion(file.extension);
        const formatToggleHtml = isReverse
            ? `<div class="format-toggle">
                    <button class="format-btn active" data-format="docx" disabled>
                        .docx
                    </button>
               </div>`
            : `<div class="format-toggle">
                    <button class="format-btn ${file.output_format === 'md' ? 'active' : ''}" 
                            data-format="md" 
                            onclick="setFormat('${file.id}', 'md')">
                        .md
                    </button>
                    <button class="format-btn ${file.output_format === 'json' ? 'active' : ''}" 
                            data-format="json"
                            onclick="setFormat('${file.id}', 'json')">
                        .json
                    </button>
               </div>`;
        
        return `
        <div class="file-item" data-id="${file.id}">
            <div class="file-icon">
                ${getFileIcon(file.extension)}
            </div>
            <div class="file-info">
                <div class="file-name">${escapeHtml(file.filename)}</div>
                <div class="file-meta">
                    <span class="file-size">${formatFileSize(file.size)}</span>
                    <span class="file-status">
                        <span class="status-dot ${file.status}"></span>
                        ${getStatusText(file.status)}
                    </span>
                </div>
            </div>
            <div class="file-actions">
                ${formatToggleHtml}
                <button class="btn-delete" onclick="deleteFile('${file.id}')" title="Remove file">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"/>
                        <line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                </button>
            </div>
        </div>
    `}).join('');
}

function renderResultsList() {
    const files = Array.from(state.files.values())
        .filter(f => f.status === 'converted')
        .sort((a, b) => {
            // Sort by converted_at descending (most recent first)
            const timeA = a.converted_at ? new Date(a.converted_at).getTime() : 0;
            const timeB = b.converted_at ? new Date(b.converted_at).getTime() : 0;
            return timeB - timeA;
        });
    
    // Hide the download all button for single file
    downloadAllBtn.style.display = 'none';
    
    resultsList.innerHTML = files.map(file => `
        <div class="result-item" data-id="${file.id}">
            <div class="result-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="20 6 9 17 4 12"/>
                </svg>
            </div>
            <div class="result-info">
                <div class="result-name">${escapeHtml(file.output_filename)}</div>
                <div class="result-meta">Converted from ${escapeHtml(file.filename)}</div>
            </div>
            <div class="result-actions">
                <button class="btn btn-ghost btn-small" onclick="previewFile('${file.id}')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                        <circle cx="12" cy="12" r="3"/>
                    </svg>
                    Preview
                </button>
                <button class="btn btn-secondary btn-small" onclick="downloadFile('${file.id}')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                        <polyline points="7 10 12 15 17 10"/>
                        <line x1="12" y1="15" x2="12" y2="3"/>
                    </svg>
                    Download
                </button>
            </div>
        </div>
    `).join('');
}

function renderZipResult() {
    const convertedFiles = Array.from(state.files.values()).filter(f => f.status === 'converted');
    const fileCount = convertedFiles.length;
    
    // Hide the header download button since we show a prominent one in the list
    downloadAllBtn.style.display = 'none';
    
    resultsList.innerHTML = `
        <div class="result-item result-item-zip">
            <div class="result-icon zip-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="7 10 12 15 17 10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
            </div>
            <div class="result-info">
                <div class="result-name">converted_files.zip</div>
                <div class="result-meta">${fileCount} file${fileCount !== 1 ? 's' : ''} converted and bundled</div>
            </div>
            <div class="result-actions">
                <button class="btn btn-primary" onclick="handleDownloadAll()">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                        <polyline points="7 10 12 15 17 10"/>
                        <line x1="12" y1="15" x2="12" y2="3"/>
                    </svg>
                    Download ZIP
                </button>
            </div>
        </div>
        <div class="zip-contents">
            <div class="zip-contents-header">
                <span>Contents:</span>
            </div>
            ${convertedFiles.map(file => `
                <div class="zip-content-item">
                    <span class="zip-content-name">${escapeHtml(file.output_filename)}</span>
                    <div class="zip-content-actions">
                        <button class="btn btn-ghost btn-small" onclick="previewFile('${file.id}')">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                                <circle cx="12" cy="12" r="3"/>
                            </svg>
                            Preview
                        </button>
                        <button class="btn btn-ghost btn-small" onclick="downloadFile('${file.id}')">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                                <polyline points="7 10 12 15 17 10"/>
                                <line x1="12" y1="15" x2="12" y2="3"/>
                            </svg>
                            Download
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function updateOutputIndicator() {
    const uploadedFiles = Array.from(state.files.values()).filter(f => f.status === 'uploaded');
    const outputIndicator = document.getElementById('outputIndicator');
    
    if (!outputIndicator) return;
    
    if (uploadedFiles.length > 1) {
        outputIndicator.classList.add('visible');
        outputIndicator.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            <span>Output: ZIP bundle (${uploadedFiles.length} files)</span>
        `;
    } else {
        outputIndicator.classList.remove('visible');
    }
}

function getFileIcon(extension) {
    const ext = extension.toLowerCase().replace('.', '');
    if (['pdf'].includes(ext)) return FILE_ICONS.pdf;
    if (['doc', 'docx'].includes(ext)) return FILE_ICONS.docx;
    if (['xls', 'xlsx', 'csv'].includes(ext)) return FILE_ICONS.xlsx;
    if (['ppt', 'pptx'].includes(ext)) return FILE_ICONS.pptx;
    if (['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'tif', 'webp'].includes(ext)) return FILE_ICONS.image;
    if (['md', 'markdown'].includes(ext)) return FILE_ICONS.markdown;
    return FILE_ICONS.default;
}

function isReverseConversion(extension) {
    const ext = extension.toLowerCase().replace('.', '');
    return ['md', 'markdown'].includes(ext);
}

function getStatusText(status) {
    const statusMap = {
        'uploaded': 'Ready',
        'converting': 'Converting...',
        'converted': 'Done',
        'error': 'Error'
    };
    return statusMap[status] || status;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Global functions (called from onclick)
window.setFormat = async function(fileId, format) {
    try {
        const response = await fetch(`/api/set-format/${fileId}?format=${format}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const file = state.files.get(fileId);
            if (file) {
                file.output_format = format;
                updateUI();
            }
        }
    } catch (error) {
        console.error('Failed to set format:', error);
    }
};

window.deleteFile = async function(fileId) {
    try {
        const response = await fetch(`/api/file/${fileId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            state.files.delete(fileId);
            updateUI();
        }
    } catch (error) {
        console.error('Failed to delete file:', error);
    }
};

window.downloadFile = function(fileId) {
    window.location.href = `/api/download/${fileId}`;
};

window.previewFile = async function(fileId) {
    try {
        const response = await fetch(`/api/preview/${fileId}`);
        const data = await response.json();
        
        previewTitle.textContent = data.filename;
        previewContent.textContent = data.preview;
        previewDownloadBtn.onclick = () => downloadFile(fileId);
        
        previewModal.classList.add('visible');
    } catch (error) {
        console.error('Failed to preview file:', error);
        showError('Failed to load preview');
    }
};

async function handleConvert() {
    if (state.isConverting) return;
    
    state.isConverting = true;
    convertBtn.classList.add('loading');
    convertBtn.disabled = true;
    
    // Mark all uploaded files as converting
    state.files.forEach(file => {
        if (file.status === 'uploaded') {
            file.status = 'converting';
        }
    });
    updateUI();
    
    try {
        const response = await fetch('/api/convert', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        // Update file statuses from results
        data.results.forEach(result => {
            const file = state.files.get(result.id);
            if (file) {
                file.status = result.status === 'error' ? 'error' : 'converted';
                file.output_filename = result.output_filename;
                file.converted_at = result.converted_at;
                if (result.error) {
                    file.error = result.error;
                }
            }
        });
        
    } catch (error) {
        console.error('Conversion error:', error);
        showError('Conversion failed');
        
        // Reset status on error
        state.files.forEach(file => {
            if (file.status === 'converting') {
                file.status = 'uploaded';
            }
        });
    }
    
    state.isConverting = false;
    convertBtn.classList.remove('loading');
    updateUI();
}

async function handleClearAll() {
    try {
        const response = await fetch('/api/clear', {
            method: 'DELETE'
        });
        
        if (response.ok) {
            state.files.clear();
            updateUI();
        }
    } catch (error) {
        console.error('Failed to clear files:', error);
    }
}

function handleDownloadAll() {
    window.location.href = '/api/download-all';
}

// Make handleDownloadAll globally accessible
window.handleDownloadAll = handleDownloadAll;

function closeModal() {
    previewModal.classList.remove('visible');
}

async function handleCopyPreview() {
    const content = previewContent.textContent;
    const copyBtnSpan = previewCopyBtn.querySelector('span');
    const originalText = copyBtnSpan.textContent;
    
    try {
        await navigator.clipboard.writeText(content);
        copyBtnSpan.textContent = 'Copied!';
        previewCopyBtn.classList.add('copied');
        
        setTimeout(() => {
            copyBtnSpan.textContent = originalText;
            previewCopyBtn.classList.remove('copied');
        }, 2000);
    } catch (error) {
        console.error('Failed to copy:', error);
        showError('Failed to copy to clipboard');
    }
}

function showError(message) {
    // Simple error display - could be enhanced with a toast notification
    alert(message);
}
