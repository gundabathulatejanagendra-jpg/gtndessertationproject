//  PHOTO PREVIEW 
function previewPhoto(input) {
    var preview = document.getElementById('photoPreview');
    var img = document.getElementById('previewImg');
    var uploadArea = document.getElementById('uploadArea');

    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            img.src = e.target.result;
            preview.style.display = 'block';
            uploadArea.style.display = 'none';
        };
        reader.readAsDataURL(input.files[0]);
    }
}

function clearPhoto() {
    var preview = document.getElementById('photoPreview');
    var uploadArea = document.getElementById('uploadArea');
    var input = document.getElementById('photoInput');
    preview.style.display = 'none';
    uploadArea.style.display = 'block';
    input.value = '';
}

//  DRAG AND DROP 
document.addEventListener('DOMContentLoaded', function () {
    var uploadArea = document.getElementById('uploadArea');
    if (!uploadArea) return;

    uploadArea.addEventListener('dragover', function (e) {
        e.preventDefault();
        uploadArea.style.borderColor = '#2563eb';
        uploadArea.style.background = '#eff6ff';
    });

    uploadArea.addEventListener('dragleave', function () {
        uploadArea.style.borderColor = '#cbd5e1';
        uploadArea.style.background = '#f8fafc';
    });

    uploadArea.addEventListener('drop', function (e) {
        e.preventDefault();
        uploadArea.style.borderColor = '#cbd5e1';
        uploadArea.style.background = '#f8fafc';
        var files = e.dataTransfer.files;
        if (files.length > 0) {
            var input = document.getElementById('photoInput');
            input.files = files;
            previewPhoto(input);
        }
    });
});
