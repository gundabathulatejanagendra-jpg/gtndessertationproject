//  AUTO DISMISS ALERTS 
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(function () { alert.remove(); }, 500);
        }, 4500);
    });
});

//  NOTIFICATION BADGE POLL (resident only) 
function updateNotifBadge() {
    const badge = document.getElementById('notif-count');
    if (!badge) return;
    fetch('/api/unread-count')
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (data.count > 0) {
                badge.textContent = data.count;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        })
        .catch(function () {});
}

document.addEventListener('DOMContentLoaded', function () {
    updateNotifBadge();
    setInterval(updateNotifBadge, 30000);
});
