(function() {
    'use strict';

    // Signal Bot Application
    window.SignalBot = {
        // Configuration
        config: {
            refreshInterval: 30000, // 30 seconds
            apiBaseUrl: '/api'
        },

        // State
        state: {
            isLoading: false,
            currentSignals: [],
            signalHistory: [],
            assets: [],
            selectedAsset: null
        },

        // Initialize the application
        init: function() {
            this.bindEvents();
            this.loadAssets();
            this.loadPerformanceMetrics();
            this.loadCurrentSignals();
            this.loadSignalHistory();
            this.startAutoRefresh();
        },

        // Bind event listeners
        bindEvents: function() {
            const self = this;
            
            // Generate signal button
            document.getElementById('generate-signal-btn').addEventListener('click', function() {
                self.generateSignal();
            });

            // Asset selection
            document.getElementById('asset-select').addEventListener('change', function() {
                self.state.selectedAsset = this.value;
                document.getElementById('generate-signal-btn').disabled = !this.value;
            });

            // Refresh signals button
            document.getElementById('refresh-signals').addEventListener('click', function() {
                self.loadCurrentSignals();
            });

            // Asset filter for history
            document.getElementById('asset-filter').addEventListener('change', function() {
                self.loadSignalHistory(this.value);
            });
        },

        // Load available assets
        loadAssets: function() {
            const self = this;
            
            fetch(`${this.config.apiBaseUrl}/assets`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        self.state.assets = data.assets;
                        self.populateAssetSelects();
                    }
                })
                .catch(error => {
                    console.error('Error loading assets:', error);
                });
        },

        // Populate asset select dropdowns
        populateAssetSelects: function() {
            const assetSelect = document.getElementById('asset-select');
            const assetFilter = document.getElementById('asset-filter');
            
            // Clear existing options (except first)
            assetSelect.innerHTML = '<option value="">Select an asset...</option>';
            assetFilter.innerHTML = '<option value="">All Assets</option>';
            
            this.state.assets.forEach(asset => {
                const option1 = new Option(asset, asset);
                const option2 = new Option(asset, asset);
                assetSelect.add(option1);
                assetFilter.add(option2);
            });
        },

        // Load performance metrics
        loadPerformanceMetrics: function() {
            fetch(`${this.config.apiBaseUrl}/performance`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.updatePerformanceDisplay(data.metrics);
                    } else {
                        this.showEmptyPerformanceMetrics();
                    }
                })
                .catch(error => {
                    console.error('Error loading performance metrics:', error);
                    this.showEmptyPerformanceMetrics();
                });
        },

        // Update performance metrics display
        updatePerformanceDisplay: function(metrics) {
            document.getElementById('total-signals').textContent = metrics.total_signals || 0;
            document.getElementById('win-rate').textContent = metrics.total_signals > 0 ? `${metrics.win_rate}%` : '-';
            document.getElementById('total-profit').textContent = metrics.total_signals > 0 ? `$${metrics.total_profit}` : '-';
        },

        // Show empty performance metrics
        showEmptyPerformanceMetrics: function() {
            document.getElementById('total-signals').textContent = '0';
            document.getElementById('win-rate').textContent = '-';
            document.getElementById('total-profit').textContent = '-';
        },

        // Load current signals
        loadCurrentSignals: function() {
            const self = this;
            
            fetch(`${this.config.apiBaseUrl}/signals/current`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        self.state.currentSignals = data.signals;
                        self.displayCurrentSignals();
                        document.getElementById('active-signals').textContent = data.signals.length;
                    } else {
                        self.showNoCurrentSignals();
                    }
                })
                .catch(error => {
                    console.error('Error loading current signals:', error);
                    self.showNoCurrentSignals();
                });
        },

        // Display current signals
        displayCurrentSignals: function() {
            const container = document.getElementById('current-signals-container');
            
            if (this.state.currentSignals.length === 0) {
                this.showNoCurrentSignals();
                return;
            }

            let html = '<div class="row">';
            
            this.state.currentSignals.forEach(signal => {
                const timeAgo = this.getTimeAgo(new Date(signal.created_at));
                const confidenceColor = this.getConfidenceColor(signal.confidence);
                const signalTypeColor = signal.signal_type === 'BUY' ? 'success' : 'danger';
                
                html += `
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="card border-${signalTypeColor}">
                            <div class="card-header bg-${signalTypeColor} text-white">
                                <div class="d-flex justify-content-between align-items-center">
                                    <strong>${signal.asset}</strong>
                                    <span class="badge bg-light text-dark">${signal.signal_type}</span>
                                </div>
                            </div>
                            <div class="card-body">
                                <div class="row text-center">
                                    <div class="col-6">
                                        <div class="text-muted small">Entry Price</div>
                                        <div class="fw-bold">${signal.entry_price}</div>
                                    </div>
                                    <div class="col-6">
                                        <div class="text-muted small">Expiry</div>
                                        <div class="fw-bold">${signal.expiry_time}m</div>
                                    </div>
                                </div>
                                <div class="mt-3">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <span class="text-muted small">Confidence</span>
                                        <span class="badge bg-${confidenceColor}">${signal.confidence}%</span>
                                    </div>
                                    <div class="progress mt-1" style="height: 6px;">
                                        <div class="progress-bar bg-${confidenceColor}" style="width: ${signal.confidence}%"></div>
                                    </div>
                                </div>
                                <div class="mt-2 text-muted small">
                                    <i class="fas fa-clock me-1"></i>${timeAgo}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            container.innerHTML = html;
        },

        // Show no current signals message
        showNoCurrentSignals: function() {
            const container = document.getElementById('current-signals-container');
            container.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-chart-line fa-3x mb-3 opacity-50"></i>
                    <p>No active trading signals.</p>
                    <p class="small">Generate a signal above to get started.</p>
                </div>
            `;
            document.getElementById('active-signals').textContent = '0';
        },

        // Load signal history
        loadSignalHistory: function(assetFilter = '') {
            const self = this;
            let url = `${this.config.apiBaseUrl}/signals/history`;
            
            if (assetFilter) {
                url += `?asset=${encodeURIComponent(assetFilter)}`;
            }
            
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        self.state.signalHistory = data.signals;
                        self.displaySignalHistory();
                    } else {
                        self.showNoSignalHistory();
                    }
                })
                .catch(error => {
                    console.error('Error loading signal history:', error);
                    self.showNoSignalHistory();
                });
        },

        // Display signal history
        displaySignalHistory: function() {
            const container = document.getElementById('signal-history-container');
            
            if (this.state.signalHistory.length === 0) {
                this.showNoSignalHistory();
                return;
            }

            let html = `
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Asset</th>
                                <th>Signal</th>
                                <th>Entry Price</th>
                                <th>Expiry</th>
                                <th>Confidence</th>
                                <th>Result</th>
                                <th>Time</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            this.state.signalHistory.forEach(signal => {
                const timeAgo = this.getTimeAgo(new Date(signal.created_at));
                const signalTypeColor = signal.signal_type === 'BUY' ? 'success' : 'danger';
                const resultColor = signal.result === 'WIN' ? 'success' : signal.result === 'LOSS' ? 'danger' : 'secondary';
                
                html += `
                    <tr>
                        <td><strong>${signal.asset}</strong></td>
                        <td><span class="badge bg-${signalTypeColor}">${signal.signal_type}</span></td>
                        <td>${signal.entry_price}</td>
                        <td>${signal.expiry_time}m</td>
                        <td>
                            <span class="badge bg-${this.getConfidenceColor(signal.confidence)}">${signal.confidence}%</span>
                        </td>
                        <td>
                            <span class="badge bg-${resultColor}">${signal.result || 'PENDING'}</span>
                        </td>
                        <td class="text-muted small">${timeAgo}</td>
                    </tr>
                `;
            });
            
            html += '</tbody></table></div>';
            container.innerHTML = html;
        },

        // Show no signal history message
        showNoSignalHistory: function() {
            const container = document.getElementById('signal-history-container');
            container.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-history fa-3x mb-3 opacity-50"></i>
                    <p>No signal history available.</p>
                    <p class="small">Signal history will appear here after generating your first signals.</p>
                </div>
            `;
        },

        // Generate new signal
        generateSignal: function() {
            if (!this.state.selectedAsset || this.state.isLoading) {
                return;
            }

            const self = this;
            const button = document.getElementById('generate-signal-btn');
            const status = document.getElementById('generation-status');
            
            self.state.isLoading = true;
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
            status.textContent = 'Analyzing market conditions...';
            
            fetch(`${this.config.apiBaseUrl}/signals/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    asset: this.state.selectedAsset
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    status.textContent = 'Signal generated successfully!';
                    status.className = 'text-success small';
                    self.loadCurrentSignals();
                    self.loadPerformanceMetrics();
                } else {
                    status.textContent = data.error || 'Unable to generate signal at this time';
                    status.className = 'text-warning small';
                }
            })
            .catch(error => {
                console.error('Error generating signal:', error);
                status.textContent = 'Error generating signal';
                status.className = 'text-danger small';
            })
            .finally(() => {
                self.state.isLoading = false;
                button.disabled = false;
                button.innerHTML = '<i class="fas fa-magic me-2"></i>Generate Signal';
                
                // Clear status after 5 seconds
                setTimeout(() => {
                    status.textContent = '';
                    status.className = 'text-muted small';
                }, 5000);
            });
        },

        // Start auto-refresh
        startAutoRefresh: function() {
            const self = this;
            setInterval(() => {
                self.loadCurrentSignals();
                self.loadPerformanceMetrics();
            }, this.config.refreshInterval);
        },

        // Helper functions
        getTimeAgo: function(date) {
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            
            if (diffMins < 1) return 'Just now';
            if (diffMins < 60) return `${diffMins}m ago`;
            
            const diffHours = Math.floor(diffMins / 60);
            if (diffHours < 24) return `${diffHours}h ago`;
            
            const diffDays = Math.floor(diffHours / 24);
            return `${diffDays}d ago`;
        },

        getConfidenceColor: function(confidence) {
            if (confidence >= 80) return 'success';
            if (confidence >= 60) return 'warning';
            return 'secondary';
        }
    };
})();
