// RAG Demo Web App - Client-side JavaScript

class RAGApp {
    constructor() {
        this.conversationHistory = [];
        this.sampleDocs = [];
        this.currentConversationId = null;
        this.init();
    }

    async init() {
        await this.loadConfig();
        this.loadConversationFromLocalStorage();
        this.setupEventListeners();
        this.updateStatus();
        this.renderConversation();
    }

    // ========================================================================
    // CONVERSATION PERSISTENCE (LocalStorage + Backend)
    // ========================================================================

    loadConversationFromLocalStorage() {
        // Load conversation from localStorage on page load.
        try {
            const saved = localStorage.getItem('ragConversation');
            if (saved) {
                this.conversationHistory = JSON.parse(saved);
            }
        } catch (error) {
            console.error('Failed to load conversation from localStorage:', error);
        }
    }

    saveConversationToLocalStorage() {
        // Save conversation to localStorage for persistence.
        try {
            localStorage.setItem('ragConversation', JSON.stringify(this.conversationHistory));
        } catch (error) {
            console.error('Failed to save conversation to localStorage:', error);
        }
    }

    async saveConversationToServer(name = null) {
        // Save current conversation to server.
        if (this.conversationHistory.length === 0) {
            this.showError('queryError', 'No conversation to save');
            setTimeout(() => this.hideMessage('queryError'), 3000);
            return;
        }

        try {
            const response = await fetch('/api/conversations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    messages: this.conversationHistory,
                    name: name
                })
            });

            const data = await response.json();
            if (data.success) {
                this.currentConversationId = data.id;
                alert(`Conversation saved as: ${data.id}`);
            } else {
                this.showError('queryError', data.error);
            }
        } catch (error) {
            this.showError('queryError', 'Failed to save conversation: ' + error.message);
        }
    }

    async loadSavedConversations() {
        // Load and display list of saved conversations.
        const modal = document.getElementById('conversationsModal');
        const list = document.getElementById('conversationsModalList');

        modal.style.display = 'block';
        list.innerHTML = '<div style="text-align: center; color: #94a3b8; padding: 40px;">Loading...</div>';

        try {
            const response = await fetch('/api/conversations');
            const data = await response.json();

            if (data.success) {
                if (data.conversations.length === 0) {
                    list.innerHTML = '<div style="text-align: center; color: #94a3b8; padding: 40px;">No saved conversations yet</div>';
                } else {
                    list.innerHTML = data.conversations.map(conv =>
                        `<div class="conversation-item">
                            <div class="conversation-info">
                                <div class="conversation-title">${conv.id}</div>
                                <div class="conversation-meta">${conv.message_count} messages • ${new Date(conv.created_at).toLocaleString()}</div>
                            </div>
                            <div class="conversation-actions">
                                <button class="secondary" onclick="app.loadConversationById('${conv.id}')">Load</button>
                                <button class="secondary" onclick="app.exportConversationById('${conv.id}')">Export</button>
                                <button class="secondary danger" onclick="app.deleteConversationById('${conv.id}')">Delete</button>
                            </div>
                         </div>`
                    ).join('');
                }
            }
        } catch (error) {
            list.innerHTML = '<div style="color: #991b1b; padding: 40px;">Failed to load conversations</div>';
        }
    }

    async loadConversationById(conversationId) {
        // Load a specific conversation from server.
        try {
            const response = await fetch(`/api/conversations/${conversationId}`);
            const data = await response.json();

            if (data.success) {
                this.conversationHistory = data.conversation.messages;
                this.currentConversationId = conversationId;
                this.renderConversation();
                this.saveConversationToLocalStorage();
                this.closeConversationsModal();
                this.showSuccess('addSuccess', `Loaded conversation: ${conversationId}`);
                setTimeout(() => this.hideMessage('addSuccess'), 3000);
            }
        } catch (error) {
            alert('Failed to load conversation: ' + error.message);
        }
    }

    async deleteConversationById(conversationId) {
        // Delete a conversation from server.
        if (!confirm(`Delete conversation "${conversationId}"?`)) return;

        try {
            const response = await fetch(`/api/conversations/${conversationId}`, {
                method: 'DELETE'
            });

            const data = await response.json();
            if (data.success) {
                this.loadSavedConversations();
            }
        } catch (error) {
            alert('Failed to delete conversation: ' + error.message);
        }
    }

    async exportConversationById(conversationId) {
        // Export a specific conversation as JSON.
        try {
            const response = await fetch(`/api/conversations/${conversationId}`);
            const data = await response.json();

            if (data.success) {
                const blob = new Blob([JSON.stringify(data.conversation, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `conversation-${conversationId}.json`;
                a.click();
                URL.revokeObjectURL(url);
            }
        } catch (error) {
            alert('Failed to export conversation: ' + error.message);
        }
    }

    async exportAllConversations() {
        // Export all conversations as single JSON file.
        try {
            const response = await fetch('/api/conversations/export');
            const data = await response.json();

            if (data.success) {
                const blob = new Blob([JSON.stringify(data.data, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `all-conversations-${Date.now()}.json`;
                a.click();
                URL.revokeObjectURL(url);
            }
        } catch (error) {
            alert('Failed to export conversations: ' + error.message);
        }
    }

    async importConversations() {
        // Import conversations from JSON file.
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'application/json';

        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            try {
                const text = await file.text();
                const data = JSON.parse(text);

                const response = await fetch('/api/conversations/import', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                if (result.success) {
                    alert(result.message);
                    this.loadSavedConversations();
                }
            } catch (error) {
                alert('Failed to import conversations: ' + error.message);
            }
        };

        input.click();
    }

    closeConversationsModal() {
        document.getElementById('conversationsModal').style.display = 'none';
    }

    // Config Management
    async loadConfig() {
        try {
            const response = await fetch('/api/config');
            const data = await response.json();
            if (data.success) {
                this.sampleDocs = data.config.sample_documents || [];
                this.renderSampleDocs();
            }
        } catch (error) {
            console.error('Failed to load config:', error);
        }
    }

    renderSampleDocs() {
        const container = document.getElementById('sampleDocsList');
        const countBadge = document.getElementById('sampleCount');

        countBadge.textContent = `${this.sampleDocs.length} sample${this.sampleDocs.length !== 1 ? 's' : ''}`;

        if (this.sampleDocs.length === 0) {
            container.innerHTML = '<p style="color: #94a3b8; text-align: center; padding: 20px;">No sample documents configured</p>';
            return;
        }

        container.innerHTML = this.sampleDocs.map((doc, i) => `
            <div class="doc-list-item">
                <input type="text" value="${this.escapeHtml(doc)}"
                       onchange="app.updateSampleDoc(${i}, this.value)"
                       placeholder="Sample document ${i + 1}">
                <button class="secondary danger" onclick="app.removeSampleDoc(${i})">✕</button>
            </div>
        `).join('');
    }

    addSampleDoc() {
        this.sampleDocs.push('New sample document');
        this.renderSampleDocs();
    }

    updateSampleDoc(index, value) {
        this.sampleDocs[index] = value;
    }

    removeSampleDoc(index) {
        this.sampleDocs.splice(index, 1);
        this.renderSampleDocs();
    }

    async saveConfig() {
        this.showLoading('configLoading', true);
        this.hideMessage('configError');
        this.hideMessage('configSuccess');

        try {
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ config: { sample_documents: this.sampleDocs } })
            });

            const data = await response.json();
            if (data.success) {
                this.showSuccess('configSuccess', 'Configuration saved to config.json');
            } else {
                this.showError('configError', data.error);
            }
        } catch (error) {
            this.showError('configError', 'Failed to save config: ' + error.message);
        } finally {
            this.showLoading('configLoading', false);
        }
    }

    async reloadSamples() {
        this.showLoading('configLoading', true);
        this.hideMessage('configError');
        this.hideMessage('configSuccess');

        try {
            const response = await fetch('/api/reload', { method: 'POST' });
            const data = await response.json();

            if (data.success) {
                this.showSuccess('configSuccess', data.message);
                this.updateStatus();
                this.conversationHistory = [];
                this.renderConversation();
            } else {
                this.showError('configError', data.error);
            }
        } catch (error) {
            this.showError('configError', 'Failed to reload: ' + error.message);
        } finally {
            this.showLoading('configLoading', false);
        }
    }

    // Document Management
    async addDocument() {
        const text = document.getElementById('documentInput').value.trim();
        if (!text) {
            this.showError('addError', 'Please enter some text');
            return;
        }

        this.showLoading('addLoading', true);
        this.hideMessage('addError');
        this.hideMessage('addSuccess');

        try {
            const response = await fetch('/api/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            const data = await response.json();

            if (data.success) {
                document.getElementById('documentInput').value = '';
                this.showSuccess('addSuccess', 'Document added successfully!');
                this.updateStatus(data.total_docs);
                setTimeout(() => this.hideMessage('addSuccess'), 3000);
            } else {
                this.showError('addError', data.error);
            }
        } catch (error) {
            this.showError('addError', 'Failed to add document: ' + error.message);
        } finally {
            this.showLoading('addLoading', false);
        }
    }

    async loadDocuments() {
        const modal = document.getElementById('docsModal');
        const list = document.getElementById('docsModalList');

        modal.style.display = 'block';
        list.innerHTML = '<div style="text-align: center; color: #94a3b8; padding: 40px;">Loading...</div>';

        try {
            const response = await fetch('/api/documents');
            const data = await response.json();

            if (data.success) {
                if (data.documents.length === 0) {
                    list.innerHTML = '<div style="text-align: center; color: #94a3b8; padding: 40px;">No documents yet</div>';
                } else {
                    list.innerHTML = data.documents.map((doc, i) =>
                        `<div class="modal-doc-item">
                            <div class="doc-number">${i + 1}</div>
                            <div class="doc-text">${this.escapeHtml(doc)}</div>
                            <button class="secondary danger" onclick="app.deleteDocument(${i})">Delete</button>
                         </div>`
                    ).join('');
                }
            }
        } catch (error) {
            list.innerHTML = '<div style="color: #991b1b; padding: 40px;">Failed to load documents</div>';
        }
    }

    async deleteDocument(index) {
        if (!confirm('Delete this document?')) return;

        try {
            const response = await fetch('/api/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ index })
            });

            const data = await response.json();
            if (data.success) {
                this.loadDocuments();
                this.updateStatus();
            }
        } catch (error) {
            alert('Failed to delete document');
        }
    }

    async clearKnowledgeBase() {
        if (!confirm('Clear all documents from the knowledge base?')) return;

        try {
            const response = await fetch('/api/clear', { method: 'POST' });
            const data = await response.json();

            if (data.success) {
                this.updateStatus(0);
                this.conversationHistory = [];
                this.renderConversation();
                this.showSuccess('addSuccess', 'Knowledge base cleared');
                this.closeModal();
                setTimeout(() => this.hideMessage('addSuccess'), 3000);
            }
        } catch (error) {
            this.showError('addError', 'Failed to clear: ' + error.message);
        }
    }

    // Chat Interface
    async askQuestion() {
        const input = document.getElementById('questionInput');
        const question = input.value.trim();

        if (!question) {
            this.showError('queryError', 'Please enter a question');
            return;
        }

        // Add user message to chat
        this.addMessageToChat('user', question);
        input.value = '';

        this.showLoading('queryLoading', true);
        this.hideMessage('queryError');

        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question })
            });

            const data = await response.json();

            if (data.success) {
                // Add AI response to chat
                this.addMessageToChat('assistant', data.answer, data.sources || []);
                this.updateStatus(data.total_docs);
            } else {
                this.showError('queryError', data.error);
            }
        } catch (error) {
            this.showError('queryError', 'Failed to get answer: ' + error.message);
        } finally {
            this.showLoading('queryLoading', false);
        }
    }

    addMessageToChat(role, content, sources = []) {
        this.conversationHistory.push({ role, content, sources, timestamp: Date.now() });
        this.renderConversation();
        this.saveConversationToLocalStorage();
    }

    renderConversation() {
        const container = document.getElementById('conversationHistory');

        if (this.conversationHistory.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 60px 20px; color: #94a3b8;">
                    <div style="font-size: 3rem; margin-bottom: 20px;">💬</div>
                    <div style="font-size: 1.2rem; font-weight: 600; margin-bottom: 10px;">No conversation yet</div>
                    <div>Ask a question to get started!</div>
                </div>
            `;
            return;
        }

        container.innerHTML = this.conversationHistory.map(msg => {
            if (msg.role === 'user') {
                return `
                    <div class="message user-message">
                        <div class="message-icon">👤</div>
                        <div class="message-content">
                            <div class="message-text">${this.escapeHtml(msg.content)}</div>
                        </div>
                    </div>
                `;
            } else {
                const sourcesHtml = msg.sources && msg.sources.length > 0 ? `
                    <div class="sources">
                        <div class="sources-label">📚 Sources:</div>
                        ${msg.sources.map((src, i) => `
                            <div class="source-item">${i + 1}. ${this.escapeHtml(src)}</div>
                        `).join('')}
                    </div>
                ` : '';

                return `
                    <div class="message assistant-message">
                        <div class="message-icon">🤖</div>
                        <div class="message-content">
                            <div class="message-text">${this.escapeHtml(msg.content)}</div>
                            ${sourcesHtml}
                        </div>
                    </div>
                `;
            }
        }).join('');

        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
    }

    clearConversation() {
        if (this.conversationHistory.length === 0) return;
        if (!confirm('Clear conversation history?')) return;

        this.conversationHistory = [];
        this.currentConversationId = null;
        this.renderConversation();
        localStorage.removeItem('ragConversation');
    }

    // Export/Import
    async exportKnowledgeBase() {
        try {
            const response = await fetch('/api/documents');
            const data = await response.json();

            if (data.success) {
                const exportData = {
                    documents: data.documents,
                    exported_at: new Date().toISOString(),
                    version: '1.0'
                };

                const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `knowledge-base-${Date.now()}.json`;
                a.click();
                URL.revokeObjectURL(url);
            }
        } catch (error) {
            alert('Failed to export: ' + error.message);
        }
    }

    importKnowledgeBase() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'application/json';

        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            try {
                const text = await file.text();
                const data = JSON.parse(text);

                if (!data.documents || !Array.isArray(data.documents)) {
                    alert('Invalid file format');
                    return;
                }

                if (!confirm(`Import ${data.documents.length} documents?`)) return;

                for (const doc of data.documents) {
                    await fetch('/api/add', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: doc })
                    });
                }

                this.showSuccess('addSuccess', `Imported ${data.documents.length} documents`);
                this.updateStatus();
                setTimeout(() => this.hideMessage('addSuccess'), 3000);

            } catch (error) {
                alert('Failed to import: ' + error.message);
            }
        };

        input.click();
    }

    // UI Helpers
    setupEventListeners() {
        // Keyboard shortcuts
        document.getElementById('documentInput').addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') this.addDocument();
        });

        document.getElementById('questionInput').addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') this.askQuestion();
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.askQuestion();
            }
        });

        // Close modal on outside click
        window.onclick = (e) => {
            const modal = document.getElementById('docsModal');
            if (e.target === modal) {
                this.closeModal();
            }
        };
    }

    closeModal() {
        document.getElementById('docsModal').style.display = 'none';
    }

    showLoading(id, show) {
        document.getElementById(id).classList.toggle('show', show);
    }

    showError(id, message) {
        const el = document.getElementById(id);
        el.textContent = message;
        el.classList.add('show');
    }

    showSuccess(id, message) {
        const el = document.getElementById(id);
        el.textContent = message;
        el.classList.add('show');
    }

    hideMessage(id) {
        document.getElementById(id).classList.remove('show');
    }

    async updateStatus(count) {
        if (count === undefined) {
            try {
                const response = await fetch('/api/documents');
                const data = await response.json();
                count = data.total;
            } catch {
                return;
            }
        }
        document.getElementById('docCount').textContent = `${count} document${count !== 1 ? 's' : ''}`;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize app
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new RAGApp();
});
