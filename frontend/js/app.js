/**
 * Ford Fleet Management Demo - Main Application
 * Demo mode: No login, role switching via dropdown
 */

const App = {
    /**
     * Initialize the application
     */
    async init() {
        // Initialize auth (auto-login with default user)
        await Auth.init();

        // Setup event listeners
        this.setupEventListeners();

        // Initialize dashboard components
        await Dashboard.init();
        AIChat.init();
        RealtimeSocket.connect();
    },

    /**
     * Setup global event listeners
     */
    setupEventListeners() {
        // Vehicle search
        const searchInput = document.getElementById('vehicle-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleVehicleSearch(e.target.value));
        }
    },

    /**
     * Handle vehicle search
     */
    handleVehicleSearch(query) {
        const tbody = document.getElementById('vehicles-tbody');
        if (!tbody) return;

        const rows = tbody.querySelectorAll('tr');
        const lowerQuery = query.toLowerCase();

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(lowerQuery) ? '' : 'none';
        });
    }
};

// Start the application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
