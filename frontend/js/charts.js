/**
 * Ford Fleet Management Demo - Charts Module
 */

const Charts = {
    performanceChart: null,
    anomalyChart: null,
    
    // Chart.js default configuration
    defaults: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 500
        },
        plugins: {
            legend: {
                display: true,
                position: 'top',
                labels: {
                    color: '#8b949e',
                    font: {
                        family: "'DM Sans', sans-serif",
                        size: 11
                    },
                    usePointStyle: true,
                    padding: 20
                }
            },
            tooltip: {
                backgroundColor: '#151a23',
                titleColor: '#e6edf3',
                bodyColor: '#8b949e',
                borderColor: '#21262d',
                borderWidth: 1,
                cornerRadius: 8,
                padding: 12,
                titleFont: {
                    family: "'DM Sans', sans-serif",
                    weight: 600
                },
                bodyFont: {
                    family: "'JetBrains Mono', monospace",
                    size: 12
                }
            }
        },
        scales: {
            x: {
                grid: {
                    color: '#21262d',
                    drawBorder: false
                },
                ticks: {
                    color: '#6e7681',
                    font: {
                        family: "'DM Sans', sans-serif",
                        size: 11
                    }
                }
            },
            y: {
                grid: {
                    color: '#21262d',
                    drawBorder: false
                },
                ticks: {
                    color: '#6e7681',
                    font: {
                        family: "'JetBrains Mono', monospace",
                        size: 11
                    }
                }
            }
        }
    },

    /**
     * Initialize all charts
     */
    init() {
        Chart.defaults.font.family = "'DM Sans', sans-serif";
        Chart.defaults.color = '#8b949e';
        
        this.initPerformanceChart();
        this.initAnomalyChart();
    },

    /**
     * Initialize the fleet performance chart
     */
    initPerformanceChart() {
        const ctx = document.getElementById('performance-chart');
        if (!ctx) return;

        this.performanceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Avg Speed (mph)',
                        data: [],
                        borderColor: '#00bcd4',
                        backgroundColor: 'rgba(0, 188, 212, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 3,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Avg Fuel %',
                        data: [],
                        borderColor: '#9c27b0',
                        backgroundColor: 'rgba(156, 39, 176, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 3,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Avg Temp (F)',
                        data: [],
                        borderColor: '#ff9800',
                        backgroundColor: 'rgba(255, 152, 0, 0.1)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 3,
                        pointHoverRadius: 6,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                ...this.defaults,
                scales: {
                    ...this.defaults.scales,
                    y: {
                        ...this.defaults.scales.y,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Speed / Fuel',
                            color: '#6e7681'
                        }
                    },
                    y1: {
                        ...this.defaults.scales.y,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Temperature (F)',
                            color: '#6e7681'
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                }
            }
        });
    },

    /**
     * Initialize the anomaly trends chart
     */
    initAnomalyChart() {
        const ctx = document.getElementById('anomaly-chart');
        if (!ctx) return;

        this.anomalyChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Critical',
                        data: [],
                        backgroundColor: '#f44336',
                        borderRadius: 4
                    },
                    {
                        label: 'Warning',
                        data: [],
                        backgroundColor: '#ff9800',
                        borderRadius: 4
                    },
                    {
                        label: 'Info',
                        data: [],
                        backgroundColor: '#00bcd4',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                ...this.defaults,
                plugins: {
                    ...this.defaults.plugins,
                    legend: {
                        ...this.defaults.plugins.legend,
                        position: 'top'
                    }
                },
                scales: {
                    ...this.defaults.scales,
                    x: {
                        ...this.defaults.scales.x,
                        stacked: true
                    },
                    y: {
                        ...this.defaults.scales.y,
                        stacked: true,
                        beginAtZero: true
                    }
                }
            }
        });
    },

    /**
     * Update performance chart with new data
     */
    updatePerformanceChart(timeseries) {
        if (!this.performanceChart || !timeseries) return;

        const labels = timeseries.map(t => this.formatDate(t.period));
        const speeds = timeseries.map(t => t.avg_speed);
        const fuels = timeseries.map(t => t.avg_fuel);
        const temps = timeseries.map(t => t.avg_temp);

        this.performanceChart.data.labels = labels;
        this.performanceChart.data.datasets[0].data = speeds;
        this.performanceChart.data.datasets[1].data = fuels;
        this.performanceChart.data.datasets[2].data = temps;
        this.performanceChart.update('none');
    },

    /**
     * Update anomaly chart with new data
     */
    updateAnomalyChart(anomalies) {
        if (!this.anomalyChart || !anomalies) return;

        // Group anomalies by date and severity
        const grouped = {};
        anomalies.forEach(a => {
            const date = a.detected_at.split('T')[0];
            if (!grouped[date]) {
                grouped[date] = { critical: 0, warning: 0, info: 0 };
            }
            const severity = a.severity.toLowerCase();
            if (grouped[date][severity] !== undefined) {
                grouped[date][severity]++;
            }
        });

        const dates = Object.keys(grouped).sort();
        const critical = dates.map(d => grouped[d].critical);
        const warning = dates.map(d => grouped[d].warning);
        const info = dates.map(d => grouped[d].info);

        this.anomalyChart.data.labels = dates.map(d => this.formatDate(d));
        this.anomalyChart.data.datasets[0].data = critical;
        this.anomalyChart.data.datasets[1].data = warning;
        this.anomalyChart.data.datasets[2].data = info;
        this.anomalyChart.update('none');
    },

    /**
     * Format date for display
     */
    formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric' 
        });
    },

    /**
     * Destroy all charts
     */
    destroy() {
        if (this.performanceChart) {
            this.performanceChart.destroy();
            this.performanceChart = null;
        }
        if (this.anomalyChart) {
            this.anomalyChart.destroy();
            this.anomalyChart = null;
        }
    }
};

