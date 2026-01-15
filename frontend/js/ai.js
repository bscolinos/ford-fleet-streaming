/**
 * Ford Fleet Management Demo - AI Chat Module
 */

const AIChat = {
    isOpen: false,
    isLoading: false,

    /**
     * Initialize AI chat panel
     */
    init() {
        this.setupEventListeners();
    },

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Toggle button
        const toggleBtn = document.getElementById('ai-toggle-btn');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggle());
        }

        // Close button
        const closeBtn = document.getElementById('btn-toggle-ai');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }

        // Send button
        const sendBtn = document.getElementById('btn-send-ai');
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }

        // Input enter key
        const input = document.getElementById('ai-input');
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        // Quick action buttons
        document.querySelectorAll('.ai-quick-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.dataset.action;
                this.handleQuickAction(action);
            });
        });
    },

    /**
     * Toggle panel open/closed
     */
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    },

    /**
     * Open the AI panel
     */
    open() {
        const panel = document.getElementById('ai-panel');
        if (panel) {
            panel.classList.add('open');
            this.isOpen = true;
            
            // Focus input
            setTimeout(() => {
                const input = document.getElementById('ai-input');
                if (input) input.focus();
            }, 300);
        }
    },

    /**
     * Close the AI panel
     */
    close() {
        const panel = document.getElementById('ai-panel');
        if (panel) {
            panel.classList.remove('open');
            this.isOpen = false;
        }
    },

    /**
     * Send a message
     */
    async sendMessage() {
        const input = document.getElementById('ai-input');
        if (!input || !input.value.trim() || this.isLoading) return;

        const message = input.value.trim();
        input.value = '';

        // Add user message to chat
        this.addMessage(message, 'user');

        // Send to API
        await this.getInsights(message);
    },

    /**
     * Handle quick action buttons
     */
    async handleQuickAction(action) {
        if (this.isLoading) return;

        const actions = {
            'summarize': 'Please summarize the recent driver notes from my fleet.',
            'issues': 'What are the top issues affecting my fleet right now?',
            'performance': 'Can you analyze the overall performance of my fleet?'
        };

        const message = actions[action];
        if (!message) return;

        // Add user message
        this.addMessage(message, 'user');

        if (action === 'summarize') {
            await this.summarizeNotes();
        } else {
            await this.getInsights(message);
        }
    },

    /**
     * Add a message to the chat
     */
    addMessage(content, role) {
        const messages = document.getElementById('ai-messages');
        if (!messages) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `ai-message ${role}`;
        messageDiv.innerHTML = `<p>${this.formatContent(content)}</p>`;

        messages.appendChild(messageDiv);
        messages.scrollTop = messages.scrollHeight;
    },

    /**
     * Format content for display
     */
    formatContent(content) {
        // Basic markdown-like formatting
        return content
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
    },

    /**
     * Show loading indicator
     */
    showLoading() {
        this.isLoading = true;
        const messages = document.getElementById('ai-messages');
        if (!messages) return;

        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'ai-message assistant loading';
        loadingDiv.id = 'ai-loading';
        loadingDiv.innerHTML = '<p>Thinking...</p>';

        messages.appendChild(loadingDiv);
        messages.scrollTop = messages.scrollHeight;
    },

    /**
     * Hide loading indicator
     */
    hideLoading() {
        this.isLoading = false;
        const loading = document.getElementById('ai-loading');
        if (loading) loading.remove();
    },

    /**
     * Get AI insights
     */
    async getInsights(question) {
        this.showLoading();

        try {
            const response = await Auth.fetch('/ai/insights', {
                method: 'POST',
                body: JSON.stringify({ question })
            });

            const data = await response.json();
            this.hideLoading();
            this.addMessage(data.answer, 'assistant');

        } catch (error) {
            this.hideLoading();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
            console.error('AI insights error:', error);
        }
    },

    /**
     * Summarize driver notes
     */
    async summarizeNotes() {
        this.showLoading();

        try {
            const response = await Auth.fetch('/ai/summarize', {
                method: 'POST',
                body: JSON.stringify({})
            });

            const data = await response.json();
            this.hideLoading();

            let message = data.summary;
            if (data.notes_count > 0) {
                message = `Based on ${data.notes_count} driver notes:\n\n${message}`;
            }
            this.addMessage(message, 'assistant');

        } catch (error) {
            this.hideLoading();
            this.addMessage('Sorry, I encountered an error summarizing notes. Please try again.', 'assistant');
            console.error('AI summarize error:', error);
        }
    }
};

