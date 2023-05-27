var dragDropBox = document.getElementById('drag-drop-box');

dragDropBox.addEventListener('dragenter', function(e) {
    e.preventDefault();
    dragDropBox.classList.add('drag-drop-active');
});

dragDropBox.addEventListener('dragover', function(e) {
    e.preventDefault();
    dragDropBox.classList.add('drag-drop-active');
});

dragDropBox.addEventListener('dragleave', function(e) {
    e.preventDefault();
    dragDropBox.classList.remove('drag-drop-active');
});

dragDropBox.addEventListener('drop', function(e) {
    e.preventDefault();
    dragDropBox.classList.remove('drag-drop-active');
    var fileInput = document.getElementById('helm-package');
    fileInput.files = e.dataTransfer.files;
});
