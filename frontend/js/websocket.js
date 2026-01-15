/**
 * Ford Fleet Management Demo - WebSocket Module
 */

const RealtimeSocket = {
    socket: null,
    reconnectAttempts: 0,
    maxReconnectAttempts: 5,
    reconnectDelay: 2000,
    listeners: [],
    isConnecting: false,

    /**
     * Connect to WebSocket server
     */
    connect() {
        if (this.socket?.readyState === WebSocket.OPEN || this.isConnecting) {
            return;
        }

        if (!Auth.token) {
            console.warn('Cannot connect to WebSocket: not authenticated');
            return;
        }

        this.isConnecting = true;
        this.updateStatus('connecting');

        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsHost = Auth.apiBase 
            ? Auth.apiBase.replace(/^https?:/, wsProtocol)
            : `${wsProtocol}//${window.location.host}`;
        const wsUrl = `${wsHost}/realtime/stream?token=${Auth.token}`;

        try {
            this.socket = new WebSocket(wsUrl);

            this.socket.onopen = () => {
                console.log('WebSocket connected');
                this.isConnecting = false;
                this.reconnectAttempts = 0;
                this.updateStatus('connected');
            };

            this.socket.onmessage = (event) => {
                // Ignore ping/pong messages
                if (event.data === 'pong' || event.data === 'ping') {
                    return;
                }
                try {
                    const data = JSON.parse(event.data);
                    this.notifyListeners(data);
                } catch (e) {
                    console.error('Failed to parse WebSocket message:', e);
                }
            };

            this.socket.onclose = (event) => {
                this.isConnecting = false;
                console.log('WebSocket closed:', event.code, event.reason);
                this.updateStatus('disconnected');
                
                if (event.code !== 1000 && event.code !== 4001 && event.code !== 4002) {
                    this.attemptReconnect();
                }
            };

            this.socket.onerror = (error) => {
                this.isConnecting = false;
                console.error('WebSocket error:', error);
                this.updateStatus('disconnected');
            };

        } catch (error) {
            this.isConnecting = false;
            console.error('Failed to create WebSocket:', error);
            this.updateStatus('disconnected');
        }
    },

    /**
     * Disconnect from WebSocket
     */
    disconnect() {
        if (this.socket) {
            this.socket.close(1000, 'User logout');
            this.socket = null;
        }
        this.reconnectAttempts = 0;
        this.updateStatus('disconnected');
    },

    /**
     * Attempt to reconnect
     */
    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.log('Max reconnect attempts reached');
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
        
        console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
        
        setTimeout(() => {
            if (Auth.isAuthenticated()) {
                this.connect();
            }
        }, delay);
    },

    /**
     * Add message listener
     */
    addListener(callback) {
        this.listeners.push(callback);
        return () => {
            this.listeners = this.listeners.filter(l => l !== callback);
        };
    },

    /**
     * Notify all listeners
     */
    notifyListeners(data) {
        this.listeners.forEach(callback => {
            try {
                callback(data);
            } catch (e) {
                console.error('Listener error:', e);
            }
        });
    },

    /**
     * Update connection status UI
     */
    updateStatus(status) {
        const statusEl = document.getElementById('connection-status');
        if (!statusEl) return;

        statusEl.className = 'connection-status ' + status;
        
        const textEl = statusEl.querySelector('.status-text');
        if (textEl) {
            const statusTexts = {
                'connecting': 'Connecting...',
                'connected': 'Live',
                'disconnected': 'Disconnected'
            };
            textEl.textContent = statusTexts[status] || status;
        }
    },

    /**
     * Send ping to keep connection alive
     */
    ping() {
        if (this.socket?.readyState === WebSocket.OPEN) {
            this.socket.send('ping');
        }
    }
};

// Send periodic pings
setInterval(() => {
    RealtimeSocket.ping();
}, 30000);

