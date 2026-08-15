function initCharts(catLabels, catData, statusLabels, statusData, weekLabels, weekData) {

    //  CATEGORY BAR CHART 
    var catCtx = document.getElementById('catChart');
    if (catCtx) {
        new Chart(catCtx, {
            type: 'bar',
            data: {
                labels: catLabels,
                datasets: [{
                    label: 'Issues',
                    data: catData,
                    backgroundColor: [
                        '#3b82f6', '#f59e0b', '#10b981', '#6366f1', '#ef4444'
                    ],
                    borderRadius: 6,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 },
                        grid: { color: '#f1f5f9' }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    //  STATUS DOUGHNUT CHART 
    var statusCtx = document.getElementById('statusChart');
    if (statusCtx) {
        new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: statusLabels,
                datasets: [{
                    data: statusData,
                    backgroundColor: [
                        '#3b82f6', '#f59e0b', '#06b6d4', '#10b981', '#94a3b8'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { font: { size: 11 }, padding: 14 }
                    }
                },
                cutout: '60%'
            }
        });
    }

    //  WEEKLY LINE CHART 
    var weekCtx = document.getElementById('weekChart');
    if (weekCtx) {
        new Chart(weekCtx, {
            type: 'line',
            data: {
                labels: weekLabels,
                datasets: [{
                    label: 'Issues Reported',
                    data: weekData,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37,99,235,0.08)',
                    borderWidth: 2.5,
                    pointBackgroundColor: '#2563eb',
                    pointRadius: 4,
                    tension: 0.35,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 },
                        grid: { color: '#f1f5f9' }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    }
}
