document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(el) {
        return new bootstrap.Tooltip(el);
    });

    const sidebar = document.getElementById('sidebarMenu');
    if (sidebar) {
        const toggler = document.querySelector('.navbar-toggler');
        if (toggler) {
            toggler.addEventListener('click', function() {
                sidebar.classList.toggle('show');
            });

            document.addEventListener('click', function(e) {
                if (window.innerWidth < 768 &&
                    !sidebar.contains(e.target) &&
                    !toggler.contains(e.target)) {
                    sidebar.classList.remove('show');
                }
            });
        }
    }

    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    const selectFileBtn = document.getElementById('selectFileBtn');

    if (uploadZone && fileInput) {
        uploadZone.addEventListener('click', function(e) {
            if (e.target !== selectFileBtn && !selectFileBtn.contains(e.target)) {
                fileInput.click();
            }
        });

        if (selectFileBtn) {
            selectFileBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                fileInput.click();
            });
        }

        fileInput.addEventListener('change', function(e) {
            handleFileSelect(this.files[0]);
        });

        uploadZone.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('drag-over');
        });

        uploadZone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
        });

        uploadZone.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                handleFileSelect(e.dataTransfer.files[0]);
            }
        });
    }

    function handleFileSelect(file) {
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');

        if (file) {
            if (file.type !== 'application/pdf') {
                alert('Solo se permiten archivos PDF.');
                fileInput.value = '';
                fileInfo.classList.add('d-none');
                return;
            }

            if (file.size > 5 * 1024 * 1024) {
                alert('El archivo supera el tamaño máximo de 5MB.');
                fileInput.value = '';
                fileInfo.classList.add('d-none');
                return;
            }

            fileName.textContent = file.name;
            fileSize.textContent = formatFileSize(file.size);
            fileInfo.classList.remove('d-none');
        }
    }

    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    const selectElements = document.querySelectorAll('.form-select');
    selectElements.forEach(function(el) {
        if (el.id && !el.classList.contains('select2-initialized')) {
            try {
                $(el).select2({
                    theme: 'bootstrap-5',
                    width: '100%',
                    dropdownParent: $(el).closest('.card, form, body')
                });
                el.classList.add('select2-initialized');
            } catch(e) {}
        }
    });

    document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const buttons = this.querySelectorAll('button[type="submit"], input[type="submit"]');
            buttons.forEach(function(btn) {
                if (!btn.dataset.allowMultiple) {
                    btn.disabled = true;
                    setTimeout(function() {
                        btn.disabled = false;
                    }, 3000);
                }
            });
        });
    });
});
