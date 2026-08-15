//  FILTER FORM SUBMIT ON SELECT CHANGE 
document.addEventListener('DOMContentLoaded', function () {
    var selects = document.querySelectorAll('.filter-form select');
    selects.forEach(function (sel) {
        sel.addEventListener('change', function () {
            sel.closest('form').submit();
        });
    });
});

//  CONFIRM STATUS CHANGE TO RESOLVED 
document.addEventListener('DOMContentLoaded', function () {
    var updateForm = document.querySelector('.update-form');
    if (!updateForm) return;
    updateForm.addEventListener('submit', function (e) {
        var statusSel = updateForm.querySelector('select[name="status"]');
        if (statusSel && statusSel.value === 'Resolved') {
            var ok = confirm('Mark this issue as Resolved? The resident will be notified and asked for feedback.');
            if (!ok) e.preventDefault();
        }
    });
});
