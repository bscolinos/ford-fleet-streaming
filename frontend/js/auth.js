/**
 * Ford Fleet Management Demo - Authentication Module
 * Demo mode: No login required, role switching via dropdown
 */

const Auth = {
    token: null,
    user: null,
    // Auto-detect: Docker (nginx on 8080) uses same-origin, local dev uses explicit port
    apiBase: window.location.port === '8080' ? '' : 'http://localhost:8080',

    // Demo user configurations
    demoUsers: {
        'territory_manager_1': {
            password: 'territory123',
            role: 'territory_manager',
            region_id: 'WEST',
            territory_id: 'WEST_1',
            display: 'Territory Manager (West-1)'
        },
        'regional_manager_1': {
            password: 'regional123',
            role: 'regional_manager',
            region_id: 'WEST',
            territory_id: null,
            display: 'Regional Manager (West)'
        },
        'demo_admin': {
            password: 'admin123',
            role: 'admin',
            region_id: null,
            territory_id: null,
            display: 'Admin (Full Access)'
        }
    },

    /**
     * Initialize with default user and setup role selector
     */
    async init() {
        // Get initial user from dropdown or default
        const roleSelect = document.getElementById('role-select');
        const initialUser = roleSelect ? roleSelect.value : 'territory_manager_1';

        // Login as initial user
        await this.switchUser(initialUser);

        // Setup role selector change handler
        if (roleSelect) {
            roleSelect.addEventListener('change', async (e) => {
                await this.switchUser(e.target.value);
            });
        }

        return true;
    },

    /**
     * Switch to a different demo user
     */
    async switchUser(username) {
        const userConfig = this.demoUsers[username];
        if (!userConfig) {
            console.error('Unknown user:', username);
            return false;
        }

        try {
            // Show loading state
            this.updateRLSIndicator('loading');

            // Login via API to get valid token
            const response = await fetch(`${this.apiBase}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: username,
                    password: userConfig.password
                })
            });

            if (!response.ok) {
                throw new Error('Login failed');
            }

            const data = await response.json();

            this.token = data.access_token;
            this.user = {
                username: data.username,
                role: data.role,
                region_id: data.region_id,
                territory_id: data.territory_id,
                display: userConfig.display
            };

            // Update RLS indicator
            this.updateRLSIndicator('active');

            // Trigger dashboard refresh
            if (window.Dashboard && window.Dashboard.refresh) {
                window.Dashboard.refresh();
            }

            console.log(`Switched to user: ${username} (${userConfig.role})`);
            return true;

        } catch (error) {
            console.error('Failed to switch user:', error);
            this.updateRLSIndicator('error');
            return false;
        }
    },

    /**
     * Update RLS indicator status
     */
    updateRLSIndicator(status) {
        const indicator = document.getElementById('rls-indicator');
        if (!indicator) return;

        const dot = indicator.querySelector('.rls-dot');
        const text = indicator.querySelector('.rls-text');

        indicator.className = 'rls-indicator ' + status;

        switch (status) {
            case 'loading':
                text.textContent = 'Switching role...';
                break;
            case 'active':
                text.textContent = 'Row-Level Security Active';
                break;
            case 'error':
                text.textContent = 'Connection Error';
                break;
        }
    },

    /**
     * Get authorization headers
     */
    getHeaders() {
        return {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
        };
    },

    /**
     * Make authenticated API request
     */
    async fetch(endpoint, options = {}) {
        const url = endpoint.startsWith('http') ? endpoint : `${this.apiBase}${endpoint}`;

        const response = await fetch(url, {
            ...options,
            headers: {
                ...this.getHeaders(),
                ...options.headers
            }
        });

        if (response.status === 401) {
            // Re-authenticate with current user
            const roleSelect = document.getElementById('role-select');
            if (roleSelect) {
                await this.switchUser(roleSelect.value);
            }
            throw new Error('Session expired - re-authenticating');
        }

        return response;
    },

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!this.token;
    },

    /**
     * Get role display name
     */
    getRoleDisplay() {
        return this.user?.display || this.user?.role || 'Unknown';
    },

    /**
     * Get role badge class
     */
    getRoleBadgeClass() {
        const classMap = {
            'territory_manager': 'territory',
            'regional_manager': 'regional',
            'admin': 'admin'
        };
        return classMap[this.user?.role] || '';
    },

    /**
     * Get current scope description for UI
     */
    getScopeDescription() {
        if (!this.user) return '';

        switch (this.user.role) {
            case 'admin':
                return 'Viewing all regions and territories';
            case 'regional_manager':
                return `Viewing ${this.user.region_id} region`;
            case 'territory_manager':
                return `Viewing ${this.user.territory_id} territory`;
            default:
                return '';
        }
    }
};
