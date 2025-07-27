// Chart.js Configuration
Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.color = '#333';

// Utility Functions
function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Chart Creation Functions
function createLineChart(ctx, data, labels, title) {
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                borderColor: '#1a237e',
                backgroundColor: 'rgba(26, 35, 126, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: title
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function createBarChart(ctx, data, labels, title) {
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                backgroundColor: '#1a237e',
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: title
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function createPieChart(ctx, data, labels, title) {
    return new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#1a237e',
                    '#ff4081',
                    '#ffc107',
                    '#4caf50',
                    '#2196f3',
                    '#9c27b0',
                    '#f44336',
                    '#00bcd4'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: title
                }
            }
        }
    });
}

// Search Autocomplete
function initializeSearchAutocomplete() {
    const searchInput = document.querySelector('input[type="search"]');
    if (!searchInput) return;

    let timeout = null;
    searchInput.addEventListener('input', function() {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            const query = this.value;
            if (query.length < 2) return;

            fetch(`/api/search?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    // Update search results
                    const resultsContainer = document.querySelector('.search-results');
                    if (!resultsContainer) return;

                    resultsContainer.innerHTML = '';
                    data.forEach(result => {
                        const div = document.createElement('div');
                        div.className = 'search-result-item fade-in';
                        div.innerHTML = `
                            <h5>${result.name}</h5>
                            <p>${result.type}</p>
                        `;
                        resultsContainer.appendChild(div);
                    });
                })
                .catch(error => console.error('Error:', error));
        }, 300);
    });
}

// Form Validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Dynamic Content Loading
function loadMoreContent(container, url, page = 1) {
    const loadMoreBtn = document.querySelector('.load-more');
    if (!loadMoreBtn) return;

    loadMoreBtn.addEventListener('click', () => {
        fetch(`${url}?page=${page + 1}`)
            .then(response => response.json())
            .then(data => {
                data.items.forEach(item => {
                    const element = createContentElement(item);
                    container.appendChild(element);
                });

                if (!data.has_more) {
                    loadMoreBtn.style.display = 'none';
                }
                page++;
            })
            .catch(error => console.error('Error:', error));
    });
}

// Chart instances
let teamPerformanceChart;
let matchOutcomesChart;
let topBatsmenChart;
let topBowlersChart;

// Initialize charts
function initializeCharts(data) {
    // Team Performance Chart
    teamPerformanceChart = new Chart(document.getElementById('teamPerformanceChart'), {
        type: 'bar',
        data: {
            labels: data.team_names,
            datasets: [{
                label: 'Wins',
                data: data.team_wins,
                backgroundColor: '#1a237e'
            }, {
                label: 'Losses',
                data: data.team_losses,
                backgroundColor: '#ff3d00'
            }]
        },
        options: {
            responsive: true,
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                }
            }
        }
    });

    // Match Outcomes Chart
    matchOutcomesChart = new Chart(document.getElementById('matchOutcomesChart'), {
        type: 'doughnut',
        data: {
            labels: ['Won by Batting', 'Won by Bowling', 'No Result'],
            datasets: [{
                data: data.match_outcomes,
                backgroundColor: ['#1a237e', '#ff3d00', '#ffd600']
            }]
        },
        options: {
            responsive: true,
            animation: {
                duration: 1000,
                animateRotate: true
            },
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });

    // Top Batsmen Chart
    topBatsmenChart = new Chart(document.getElementById('topBatsmenChart'), {
        type: 'horizontalBar',
        data: {
            labels: data.top_batsmen_names,
            datasets: [{
                label: 'Runs',
                data: data.top_batsmen_runs,
                backgroundColor: '#1a237e'
            }]
        },
        options: {
            responsive: true,
            animation: {
                duration: 1000
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    }
                },
                y: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });

    // Top Bowlers Chart
    topBowlersChart = new Chart(document.getElementById('topBowlersChart'), {
        type: 'horizontalBar',
        data: {
            labels: data.top_bowler_names,
            datasets: [{
                label: 'Wickets',
                data: data.top_bowler_wickets,
                backgroundColor: '#ff3d00'
            }]
        },
        options: {
            responsive: true,
            animation: {
                duration: 1000
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    }
                },
                y: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Update charts with new data
function updateCharts(year) {
    fetch(`/api/dashboard-data?year=${year}`)
        .then(response => response.json())
        .then(data => {
            // Update Team Performance Chart
            teamPerformanceChart.data.labels = data.team_stats.map(team => team.name);
            teamPerformanceChart.data.datasets[0].data = data.team_stats.map(team => team.wins);
            teamPerformanceChart.data.datasets[1].data = data.team_stats.map(team => team.losses);
            teamPerformanceChart.update();

            // Update Match Outcomes Chart
            matchOutcomesChart.data.datasets[0].data = [
                data.match_outcomes.batting_wins,
                data.match_outcomes.bowling_wins,
                data.match_outcomes.no_results
            ];
            matchOutcomesChart.update();

            // Update Top Batsmen Chart
            topBatsmenChart.data.labels = data.top_batsmen.map(player => player.name);
            topBatsmenChart.data.datasets[0].data = data.top_batsmen.map(player => player.runs);
            topBatsmenChart.update();

            // Update Top Bowlers Chart
            topBowlersChart.data.labels = data.top_bowlers.map(player => player.name);
            topBowlersChart.data.datasets[0].data = data.top_bowlers.map(player => player.wickets);
            topBowlersChart.update();
        });
}

// Initialize Components
document.addEventListener('DOMContentLoaded', () => {
    // Initialize search autocomplete
    initializeSearchAutocomplete();

    // Initialize form validation
    initializeFormValidation();

    // Initialize charts if they exist
    const chartElements = document.querySelectorAll('.chart-container');
    chartElements.forEach(element => {
        const ctx = element.getContext('2d');
        const chartType = element.dataset.chartType;
        const data = JSON.parse(element.dataset.chartData);
        const labels = JSON.parse(element.dataset.chartLabels);
        const title = element.dataset.chartTitle;

        switch (chartType) {
            case 'line':
                createLineChart(ctx, data, labels, title);
                break;
            case 'bar':
                createBarChart(ctx, data, labels, title);
                break;
            case 'pie':
                createPieChart(ctx, data, labels, title);
                break;
        }
    });

    // Add fade-in animation to elements
    const fadeElements = document.querySelectorAll('.fade-in');
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    });

    fadeElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
        observer.observe(element);
    });

    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle flash messages dismissal
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.classList.add('fade');
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 3000);
    });

    // Animate stat cards on scroll
    const statCards = document.querySelectorAll('.stat-card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
            }
        });
    });

    statCards.forEach(card => observer.observe(card));

    // Add hover effects to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', () => {
            button.style.transform = 'translateY(-2px)';
            button.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
        });
        button.addEventListener('mouseleave', () => {
            button.style.transform = 'translateY(0)';
            button.style.boxShadow = 'none';
        });
    });
}); 