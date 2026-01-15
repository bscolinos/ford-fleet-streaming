/**
 * Ford Fleet Management Demo - Dashboard Module
 */

const Dashboard = {
    map: null,
    vehicleMarkers: [],
    filters: {
        granularity: 'day',
        customerId: null,
        startTs: null,
        endTs: null
    },

    /**
     * Initialize dashboard
     */
    async init() {
        this.initFilters();
        this.initMap();
        Charts.init();

        // Load initial data
        await this.refresh();

        // Setup realtime updates
        RealtimeSocket.addListener((data) => this.handleRealtimeUpdate(data));

        // Auto-refresh vehicles every 3 seconds for live map updates
        this.refreshInterval = setInterval(() => {
            this.loadVehicles();
        }, 3000);
    },

    /**
     * Initialize filter controls
     */
    initFilters() {
        // Set default date range (last 7 days)
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - 7);

        const startInput = document.getElementById('start-date');
        const endInput = document.getElementById('end-date');
        
        if (startInput) {
            startInput.value = startDate.toISOString().split('T')[0];
            this.filters.startTs = startInput.value;
        }
        if (endInput) {
            endInput.value = endDate.toISOString().split('T')[0];
            this.filters.endTs = endInput.value;
        }

        // Granularity buttons
        document.querySelectorAll('.granularity-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.granularity-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.filters.granularity = btn.dataset.granularity;
                this.refresh();
            });
        });

        // Date inputs
        if (startInput) {
            startInput.addEventListener('change', () => {
                this.filters.startTs = startInput.value;
                this.refresh();
            });
        }
        if (endInput) {
            endInput.addEventListener('change', () => {
                this.filters.endTs = endInput.value;
                this.refresh();
            });
        }

        // Customer filter
        const customerFilter = document.getElementById('customer-filter');
        if (customerFilter) {
            customerFilter.addEventListener('change', () => {
                this.filters.customerId = customerFilter.value || null;
                this.refresh();
            });
        }

        // Refresh button
        const refreshBtn = document.getElementById('btn-refresh');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refresh());
        }
    },

    /**
     * Initialize the map
     */
    initMap() {
        const mapEl = document.getElementById('fleet-map');
        if (!mapEl) return;

        // Initialize Leaflet map
        this.map = L.map('fleet-map', {
            center: [39.8283, -98.5795],  // Center of US
            zoom: 4,
            zoomControl: true
        });

        // Add tile layer (OpenStreetMap)
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(this.map);

        // Fix map size after container is fully rendered
        setTimeout(() => {
            this.map.invalidateSize();
        }, 100);
    },

    /**
     * Refresh all dashboard data
     */
    async refresh() {
        try {
            await Promise.all([
                this.loadSummary(),
                this.loadVehicles(),
                this.loadAnomalies()
            ]);
        } catch (error) {
            console.error('Dashboard refresh failed:', error);
        }
    },

    /**
     * Load fleet summary
     */
    async loadSummary() {
        const params = new URLSearchParams();
        if (this.filters.customerId) params.set('customer_id', this.filters.customerId);
        if (this.filters.startTs) params.set('start_ts', this.filters.startTs + 'T00:00:00');
        if (this.filters.endTs) params.set('end_ts', this.filters.endTs + 'T23:59:59');
        params.set('granularity', this.filters.granularity);

        const response = await Auth.fetch(`/fleet/summary?${params}`);
        const data = await response.json();

        // Update KPI cards
        this.updateKPIs(data.summary);

        // Update charts
        Charts.updatePerformanceChart(data.timeseries);
    },

    /**
     * Update KPI cards
     */
    updateKPIs(summary) {
        const setKPI = (id, value) => {
            const el = document.getElementById(id);
            if (el) el.textContent = value;
        };

        setKPI('kpi-total-vehicles', summary.total_vehicles.toLocaleString());
        setKPI('kpi-active-vehicles', summary.active_vehicles.toLocaleString());
        setKPI('kpi-avg-speed', summary.avg_speed.toFixed(1));
        setKPI('kpi-avg-fuel', summary.avg_fuel_pct.toFixed(1));
        setKPI('kpi-anomalies', summary.unacknowledged_anomalies.toLocaleString());
    },

    /**
     * Load vehicles list
     */
    async loadVehicles() {
        const params = new URLSearchParams();
        if (this.filters.customerId) params.set('customer_id', this.filters.customerId);
        params.set('limit', '100');

        const response = await Auth.fetch(`/fleet/vehicles?${params}`);
        const data = await response.json();

        this.renderVehicleTable(data.vehicles);
        this.updateMapMarkers(data.vehicles);

        // Update vehicle count
        const countEl = document.getElementById('map-vehicle-count');
        if (countEl) {
            countEl.textContent = `${data.vehicles.length} vehicles`;
        }
    },

    /**
     * Render vehicle table
     */
    renderVehicleTable(vehicles) {
        const tbody = document.getElementById('vehicles-tbody');
        if (!tbody) return;

        if (!vehicles.length) {
            tbody.innerHTML = '<tr><td colspan="8" class="loading-placeholder">No vehicles found</td></tr>';
            return;
        }

        tbody.innerHTML = vehicles.map(v => `
            <tr>
                <td>
                    <div class="vehicle-info">
                        <span class="vehicle-id">${v.vehicle_id}</span>
                        <span class="vehicle-model">${v.make} ${v.model} ${v.year}</span>
                    </div>
                </td>
                <td>${v.driver_name || '-'}</td>
                <td>
                    <span class="status-badge ${this.getVehicleStatus(v)}">
                        ${this.getVehicleStatus(v)}
                    </span>
                </td>
                <td>${v.lat && v.lon ? `${v.lat.toFixed(4)}, ${v.lon.toFixed(4)}` : '-'}</td>
                <td class="metric-value">${v.speed !== null ? v.speed.toFixed(1) : '-'}</td>
                <td class="metric-value ${this.getFuelClass(v.fuel_pct)}">${v.fuel_pct !== null ? v.fuel_pct.toFixed(1) + '%' : '-'}</td>
                <td class="metric-value ${this.getTempClass(v.engine_temp)}">${v.engine_temp !== null ? v.engine_temp.toFixed(0) + 'F' : '-'}</td>
                <td>${this.formatTimestamp(v.last_seen_ts)}</td>
            </tr>
        `).join('');
    },

    /**
     * Get vehicle status based on last seen
     */
    getVehicleStatus(vehicle) {
        if (!vehicle.last_seen_ts) return 'offline';
        const lastSeen = new Date(vehicle.last_seen_ts);
        const diff = Date.now() - lastSeen.getTime();
        if (diff < 60000) return 'active';
        if (diff < 300000) return 'idle';
        return 'offline';
    },

    /**
     * Get fuel level CSS class
     */
    getFuelClass(fuel) {
        if (fuel === null) return '';
        if (fuel < 15) return 'critical';
        if (fuel < 30) return 'warning';
        return '';
    },

    /**
     * Get temperature CSS class
     */
    getTempClass(temp) {
        if (temp === null) return '';
        if (temp > 230) return 'critical';
        if (temp > 220) return 'warning';
        return '';
    },

    /**
     * Update map markers
     */
    updateMapMarkers(vehicles) {
        if (!this.map) return;

        // Clear existing markers
        this.vehicleMarkers.forEach(m => m.remove());
        this.vehicleMarkers = [];

        // Add new markers
        vehicles.forEach(v => {
            if (v.lat && v.lon) {
                const status = this.getVehicleStatus(v);
                const color = status === 'active' ? '#4caf50' : 
                             status === 'idle' ? '#ff9800' : '#6e7681';

                const icon = L.divIcon({
                    className: 'vehicle-marker',
                    html: `<div style="
                        width: 12px;
                        height: 12px;
                        background: ${color};
                        border: 2px solid white;
                        border-radius: 50%;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                    "></div>`,
                    iconSize: [12, 12],
                    iconAnchor: [6, 6]
                });

                const marker = L.marker([v.lat, v.lon], { icon })
                    .bindPopup(`
                        <strong>${v.make} ${v.model}</strong><br>
                        ${v.vehicle_id}<br>
                        Driver: ${v.driver_name || 'Unknown'}<br>
                        Speed: ${v.speed?.toFixed(1) || '-'} mph
                    `)
                    .addTo(this.map);

                this.vehicleMarkers.push(marker);
            }
        });

        // Fit bounds if we have markers
        if (this.vehicleMarkers.length > 0) {
            const group = L.featureGroup(this.vehicleMarkers);
            this.map.fitBounds(group.getBounds().pad(0.1));
        }
    },

    /**
     * Load anomalies
     */
    async loadAnomalies() {
        const params = new URLSearchParams();
        if (this.filters.customerId) params.set('customer_id', this.filters.customerId);
        if (this.filters.startTs) params.set('start_ts', this.filters.startTs + 'T00:00:00');
        if (this.filters.endTs) params.set('end_ts', this.filters.endTs + 'T23:59:59');
        params.set('limit', '100');

        const response = await Auth.fetch(`/fleet/anomalies?${params}`);
        const data = await response.json();

        this.renderAnomalyList(data.anomalies);
        Charts.updateAnomalyChart(data.anomalies);
    },

    /**
     * Render anomaly list
     */
    renderAnomalyList(anomalies) {
        const list = document.getElementById('anomaly-list');
        if (!list) return;

        const unacked = anomalies.filter(a => !a.acknowledged).slice(0, 10);

        if (!unacked.length) {
            list.innerHTML = '<div class="loading-placeholder">No recent anomalies</div>';
            return;
        }

        list.innerHTML = unacked.map(a => `
            <div class="anomaly-item" data-id="${a.anomaly_id}">
                <div class="severity-indicator ${a.severity}"></div>
                <div class="anomaly-content">
                    <div class="anomaly-type">${this.formatAnomalyType(a.anomaly_type)}</div>
                    <div class="anomaly-meta">
                        <span>${a.vehicle_id}</span>
                        <span>${this.formatTimestamp(a.detected_at)}</span>
                    </div>
                </div>
                <button class="btn-ack" onclick="Dashboard.acknowledgeAnomaly('${a.anomaly_id}')">
                    ACK
                </button>
            </div>
        `).join('');
    },

    /**
     * Format anomaly type for display
     */
    formatAnomalyType(type) {
        return type.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, c => c.toUpperCase());
    },

    /**
     * Format timestamp for display
     */
    formatTimestamp(ts) {
        if (!ts) return '-';
        const date = new Date(ts);
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    /**
     * Acknowledge an anomaly
     */
    async acknowledgeAnomaly(anomalyId) {
        try {
            const response = await Auth.fetch(`/fleet/anomalies/${anomalyId}/ack`, {
                method: 'POST'
            });

            if (response.ok) {
                // Remove from list
                const item = document.querySelector(`[data-id="${anomalyId}"]`);
                if (item) {
                    item.style.opacity = '0.5';
                    setTimeout(() => item.remove(), 300);
                }
                
                // Refresh anomaly count
                this.loadSummary();
            }
        } catch (error) {
            console.error('Failed to acknowledge anomaly:', error);
        }
    },

    /**
     * Handle realtime WebSocket updates
     */
    handleRealtimeUpdate(data) {
        if (data.type === 'stats_update') {
            const stats = data.data;
            
            // Update active vehicles count
            const activeEl = document.getElementById('kpi-active-vehicles');
            if (activeEl && stats.active_vehicles !== undefined) {
                activeEl.textContent = stats.active_vehicles.toLocaleString();
            }

            // Add new anomalies to the list if any
            if (stats.recent_anomalies && stats.recent_anomalies.length > 0) {
                this.loadAnomalies();  // Refresh the anomaly list
            }
        }
    },

    /**
     * Clean up
     */
    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        Charts.destroy();
        if (this.map) {
            this.map.remove();
            this.map = null;
        }
    }
};

