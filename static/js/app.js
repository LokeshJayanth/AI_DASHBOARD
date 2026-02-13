// Utility Functions
const showAlert = (message, type = 'success') => {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);

    setTimeout(() => alertDiv.remove(), 5000);
};

const showSpinner = (container) => {
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    container.appendChild(spinner);
    return spinner;
};

// File Upload Handler
const initFileUpload = () => {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');

    if (!uploadArea || !fileInput) return;

    // Click to select file
    uploadArea.addEventListener('click', () => fileInput.click());

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragging');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragging');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragging');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            updateFileInfo(files[0]);
        }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            updateFileInfo(e.target.files[0]);
        }
    });

    // Form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleFileUpload);
    }
};

const updateFileInfo = (file) => {
    const uploadArea = document.getElementById('uploadArea');
    const fileSize = (file.size / 1024 / 1024).toFixed(2);
    uploadArea.innerHTML = `
        <div style="color: var(--success-color);">
            <h3>📄 ${file.name}</h3>
            <p>Size: ${fileSize} MB</p>
            <p style="color: var(--text-secondary); font-size: 0.9rem;">Click submit to upload</p>
        </div>
    `;
};

const handleFileUpload = async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;

    submitBtn.disabled = true;
    submitBtn.textContent = 'Uploading...';

    try {
        const response = await fetch('/upload/file', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            showAlert('File uploaded and cleaned successfully!', 'success');
            e.target.reset();
            document.getElementById('uploadArea').innerHTML = `
                <h3>📁 Drop your file here</h3>
                <p style="color: var(--text-secondary);">or click to browse</p>
            `;

            // Redirect to dashboard after short delay
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1500);
        } else {
            showAlert(data.error || 'Upload failed', 'error');
        }
    } catch (error) {
        showAlert('An error occurred during upload', 'error');
        console.error('Upload error:', error);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
};

// Dataset Management
const loadDatasets = async () => {
    const container = document.getElementById('datasetsContainer');
    if (!container) return;

    const spinner = showSpinner(container);

    try {
        const response = await fetch('/dataset/');
        const data = await response.json();

        spinner.remove();

        if (data.success && data.datasets.length > 0) {
            container.innerHTML = data.datasets.map(dataset => {
                const statusColor = dataset.status === 'completed' ? 'var(--success-color)' :
                    dataset.status === 'failed' ? 'var(--error-color)' : 'var(--warning-color)';
                return `
                <div class="card" id="dataset-${dataset.id}">
                    <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
                        <span>${dataset.name}</span>
                        <button onclick="deleteDataset(${dataset.id})"
                                style="background: none; border: none; color: var(--error-color); cursor: pointer; font-size: 1.5rem; padding: 0; margin: 0; line-height: 1;"
                                title="Delete dataset">
                            🗑️
                        </button>
                    </div>
                    <div class="card-body">
                        <p>${dataset.description || 'No description'}</p>
                        <p style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.5rem;">
                            <strong>Type:</strong> ${dataset.file_type} | <strong>Size:</strong> ${(dataset.file_size / 1024).toFixed(2)} KB
                        </p>
                        ${dataset.row_count !== undefined ? `
                        <p style="color: var(--text-secondary); font-size: 0.9rem;">
                            <strong>Rows:</strong> ${dataset.row_count} | <strong>Columns:</strong> ${dataset.column_count}
                        </p>` : ''}
                        <p style="color: ${statusColor}; font-size: 0.85rem; margin-top: 0.5rem;">
                            Status: ${dataset.status.toUpperCase()}
                        </p>
                        <p style="color: var(--text-secondary); font-size: 0.85rem;">
                            Uploaded: ${new Date(dataset.created_at).toLocaleString()}
                        </p>
                        ${dataset.table_name ? `
                        <p style="color: var(--text-secondary); font-size: 0.8rem;">
                            Table: ${dataset.table_name}
                        </p>` : ''}
                        <div style="margin-top: 1rem;">
                            <button class="btn btn-secondary" onclick="viewDataset(${dataset.id})">
                                View Data
                            </button>
                        </div>
                    </div>
                </div>
                `;
            }).join('');
        } else {
            container.innerHTML = `
                <div class="card" style="text-align: center;">
                    <p style="color: var(--text-secondary);">No datasets uploaded yet</p>
                    <a href="/upload/" class="btn btn-primary" style="margin-top: 1rem;">Upload Dataset</a>
                </div>
            `;
        }
    } catch (error) {
        spinner.remove();
        container.innerHTML = `
            <div class="alert alert-error">Failed to load datasets</div>
        `;
        console.error('Error loading datasets:', error);
    }
};

const viewDataset = async (datasetId) => {
    // Create modal
    const modal = document.createElement('div');
    modal.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.8); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 2rem;';
    modal.innerHTML = `
        <div style="background: var(--card-bg); border-radius: 1rem; max-width: 90vw; max-height: 90vh; overflow: auto; position: relative; border: 1px solid var(--border-color); padding: 2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; position: sticky; top: 0; background: var(--card-bg); z-index: 10; padding-bottom: 1rem; border-bottom: 2px solid var(--primary-color);">
                <h2 style="color: var(--primary-color); margin: 0;">Dataset Preview</h2>
                <button id="closeModalBtn" style="background: none; border: none; color: var(--text-primary); font-size: 2rem; cursor: pointer; line-height: 1; padding: 0;">&times;</button>
            </div>
            <div class="spinner-container" style="text-align: center; padding: 3rem;">
                <div class="spinner"></div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);

    // Add close button functionality
    const closeBtn = modal.querySelector('#closeModalBtn');
    closeBtn.addEventListener('click', () => {
        modal.remove();
    });

    // Close on background click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });

    try {
        const response = await fetch(`/dataset/${datasetId}`);
        const data = await response.json();

        if (data.success && data.dataset.preview && data.dataset.preview.length > 0) {
            modal.querySelector('.spinner').remove();

            const preview = data.dataset.preview;
            const columns = Object.keys(preview[0]).filter(col => col !== 'id' && col !== 'uploaded_at');

            let tableHTML = '<div style="overflow-x: auto; margin-top: 1rem;">';

            // Add statistics
            if (data.dataset.statistics) {
                const stats = data.dataset.statistics;
                tableHTML += `
                    <div style="margin-bottom: 1rem; padding: 1rem; background: rgba(56, 189, 248, 0.1); border-radius: 0.5rem; border: 1px solid rgba(56, 189, 248, 0.3);">
                        <p style="color: var(--primary-color); margin: 0.5rem 0;"><strong>📊 Total Rows:</strong> ${stats.total_rows}</p>
                        <p style="color: var(--primary-color); margin: 0.5rem 0;"><strong>📋 Total Columns:</strong> ${stats.column_count}</p>
                    </div>
                `;
            }

            // Build table
            tableHTML += '<table style="width: 100%; border-collapse: collapse; background: var(--card-bg); border-radius: 0.5rem; overflow: hidden;">';
            tableHTML += '<thead><tr style="background: rgba(56, 189, 248, 0.2);">';
            columns.forEach(col => {
                tableHTML += `<th style="padding: 1rem; text-align: left; color: var(--primary-color); border-bottom: 2px solid var(--primary-color);">${col}</th>`;
            });
            tableHTML += '</tr></thead><tbody>';

            preview.forEach((row, idx) => {
                const bgColor = idx % 2 === 0 ? 'rgba(255, 255, 255, 0.02)' : 'transparent';
                tableHTML += `<tr style="background: ${bgColor};">`;
                columns.forEach(col => {
                    const value = row[col] !== null && row[col] !== undefined && row[col] !== '' ? row[col] : '<span style="color: var(--text-secondary); font-style: italic;">NULL</span>';
                    tableHTML += `<td style="padding: 0.75rem; border-bottom: 1px solid var(--border-color); color: var(--text-primary);">${value}</td>`;
                });
                tableHTML += '</tr>';
            });

            tableHTML += '</tbody></table></div>';

            modal.querySelector('div > div').insertAdjacentHTML('beforeend', tableHTML);
        } else {
            modal.remove();
            showAlert('No data available or dataset not yet processed', 'warning');
        }
    } catch (error) {
        modal.remove();
        showAlert('An error occurred: ' + error.message, 'error');
        console.error('Preview error:', error);
    }
};

// Prompt Submission
const initPrompt = () => {
    const promptForm = document.getElementById('promptForm');
    if (!promptForm) return;

    promptForm.addEventListener('submit', handlePromptSubmit);
};

const handlePromptSubmit = async (e) => {
    e.preventDefault();

    const promptText = document.getElementById('promptInput').value;
    const datasetId = document.getElementById('datasetSelect')?.value || null;
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const responseCont = document.getElementById('promptResponse');

    submitBtn.disabled = true;
    submitBtn.textContent = 'Processing...';
    responseCont.innerHTML = '<div class="spinner"></div>';

    try {
        const response = await fetch('/prompt/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt_text: promptText,
                dataset_id: datasetId ? parseInt(datasetId) : null
            })
        });

        const data = await response.json();

        if (data.success) {
            responseCont.innerHTML = `
                <div class="card" style="animation: fadeInUp 0.5s ease;">
                    <div class="card-header">Response</div>
                    <div class="card-body">
                        <p>${data.response}</p>
                    </div>
                </div>
            `;
        } else {
            responseCont.innerHTML = `
                <div class="alert alert-error">${data.error}</div>
            `;
        }
    } catch (error) {
        responseCont.innerHTML = `
            <div class="alert alert-error">An error occurred</div>
        `;
        console.error('Prompt error:', error);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Query';
    }
};

// Delete Dataset
const deleteDataset = async (datasetId) => {
    if (!confirm('Are you sure you want to delete this dataset? This will remove all data and cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`/dataset/${datasetId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showAlert('Dataset deleted successfully', 'success');

            // Remove the card from DOM with animation
            const card = document.getElementById(`dataset-${datasetId}`);
            if (card) {
                card.style.opacity = '0';
                card.style.transform = 'scale(0.9)';
                card.style.transition = 'all 0.3s ease';
                setTimeout(() => card.remove(), 300);
            }

            // Reload datasets after a short delay
            setTimeout(() => loadDatasets(), 500);
        } else {
            showAlert(data.error || 'Failed to delete dataset', 'error');
        }
    } catch (error) {
        showAlert('An error occurred while deleting', 'error');
        console.error('Delete error:', error);
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initFileUpload();
    loadDatasets();
    initPrompt();

    // Add active class to current nav link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.navbar-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});
