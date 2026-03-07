/**
 * Dashboard Workflow - Unified Upload Interface
 * Handles all workflow steps via AJAX
 */

// Global state
let currentStep = 1;
let uploadedData = {};

// ============================================================================
// STEP 1: Upload File
// ============================================================================

document.getElementById('uploadForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const formData = new FormData();
    const fileInput = document.getElementById('file');
    const nameInput = document.getElementById('name');

    formData.append('file', fileInput.files[0]);
    formData.append('name', nameInput.value || fileInput.files[0].name);

    try {
        showLoading('Uploading file...');

        const response = await fetch('/upload/file', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            uploadedData = data;
            showPreview(data);
            updateProgress(2);
        } else {
            showError(data.error);
        }
    } catch (error) {
        showError('Upload failed: ' + error.message);
    } finally {
        hideLoading();
    }
});

function showPreview(data) {
    // Show preview section
    document.getElementById('preview-section').classList.remove('hidden');

    // Display stats
    const statsHtml = `
        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 1rem; border-radius: 6px; text-align: center;">
            <div style="font-size: 2rem; font-weight: 700;">${data.stats.rows}</div>
            <div style="font-size: 0.9rem;">Total Rows</div>
        </div>
        <div style="background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); color: white; padding: 1rem; border-radius: 6px; text-align: center;">
            <div style="font-size: 2rem; font-weight: 700;">${data.stats.columns}</div>
            <div style="font-size: 0.9rem;">Columns</div>
        </div>
        <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 1rem; border-radius: 6px; text-align: center;">
            <div style="font-size: 2rem; font-weight: 700;">${data.stats.duplicates}</div>
            <div style="font-size: 0.9rem;">Duplicates</div>
        </div>
    `;
    document.getElementById('preview-stats').innerHTML = statsHtml;

    // Display table
    displayTable('preview-table', data.preview, data.columns);

    // Scroll to preview
    document.getElementById('preview-section').scrollIntoView({ behavior: 'smooth' });
}

// ============================================================================
// STEP 2: Clean Data
// ============================================================================

async function cleanData() {
    try {
        showLoading('Cleaning data...');

        const response = await fetch('/upload/clean', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (data.success) {
            showCleaned(data);
            updateProgress(3);
        } else {
            showError(data.error);
        }
    } catch (error) {
        showError('Cleaning failed: ' + error.message);
    } finally {
        hideLoading();
    }
}

function showCleaned(data) {
    // Show cleaned section
    document.getElementById('cleaned-section').classList.remove('hidden');

    // Display comparison
    const comparisonHtml = `
        <div style="background: #f3f4f6; padding: 1rem; border-radius: 6px;">
            <h4 style="margin-bottom: 0.5rem;">Before vs After Cleaning:</h4>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                <div>
                    <strong>Before:</strong>
                    <div>Rows: ${data.stats.before.rows}</div>
                    <div>NULLs: ${data.stats.before.nulls}</div>
                    <div>Duplicates: ${data.stats.before.duplicates}</div>
                </div>
                <div style="color: #10b981;">
                    <strong>After:</strong>
                    <div>Rows: ${data.stats.after.rows}</div>
                    <div>NULLs: ${data.stats.after.nulls}</div>
                    <div>Duplicates: ${data.stats.after.duplicates}</div>
                </div>
            </div>
        </div>
    `;
    document.getElementById('cleaned-comparison').innerHTML = comparisonHtml;

    // Display cleaned table
    displayTable('cleaned-table', data.preview, data.columns);

    // Display column checkboxes
    const checkboxesHtml = data.columns.map(col => `
        <label class="column-checkbox">
            <input type="checkbox" value="${col}" checked> ${col}
        </label>
    `).join('');
    document.getElementById('column-selection').innerHTML = checkboxesHtml;

    // Scroll to cleaned section
    document.getElementById('cleaned-section').scrollIntoView({ behavior: 'smooth' });
}

// ============================================================================
// STEP 3: Select Columns
// ============================================================================

async function selectColumns() {
    const checkboxes = document.querySelectorAll('#column-selection input[type="checkbox"]:checked');
    const selectedColumns = Array.from(checkboxes).map(cb => cb.value);

    if (selectedColumns.length === 0) {
        showError('Please select at least one column');
        return;
    }

    try {
        showLoading('Processing selection...');

        const response = await fetch('/upload/select-columns', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ columns: selectedColumns })
        });

        const data = await response.json();

        if (data.success) {
            showDownload(data);
            updateProgress(4);
        } else {
            showError(data.error);
        }
    } catch (error) {
        showError('Selection failed: ' + error.message);
    } finally {
        hideLoading();
    }
}

function showDownload(data) {
    // Show download section
    document.getElementById('download-section').classList.remove('hidden');

    // Display info
    const infoHtml = `
        <div style="font-size: 1.5rem; color: #10b981; margin-bottom: 0.5rem;">✅ Dataset Ready!</div>
        <div style="font-size: 1.2rem; font-weight: 600;">${data.rows} rows × ${data.columns} columns</div>
        <div style="color: var(--text-secondary); margin-top: 0.5rem;">100% BI-Ready Data</div>
    `;
    document.getElementById('download-info').innerHTML = infoHtml;

    // Scroll to download section
    document.getElementById('download-section').scrollIntoView({ behavior: 'smooth' });
}

// ============================================================================
// STEP 4: Download Functions
// ============================================================================

function downloadCSV() {
    window.location.href = '/upload/download/csv';
    updateProgress(5);
}

function downloadExcel() {
    window.location.href = '/upload/download/excel';
    updateProgress(5);
}

// ============================================================================
// STEP 5: Analytics
// ============================================================================

async function showAnalytics() {
    document.getElementById('analytics-section').classList.remove('hidden');
    updateProgress(6);

    // Load auto mode by default
    await loadAutoMode();

    // Scroll to analytics
    document.getElementById('analytics-section').scrollIntoView({ behavior: 'smooth' });
}

async function loadAutoMode() {
    try {
        showLoading('Generating analytics...');

        const response = await fetch('/upload/analyze-auto', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (data.success) {
            displayAutoMode(data);
        } else {
            showError(data.error);
        }
    } catch (error) {
        showError('Analytics failed: ' + error.message);
    } finally {
        hideLoading();
    }
}

function displayAutoMode(data) {
    // Display stats
    const statsHtml = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem; border-radius: 6px; text-align: center;">
                <div style="font-size: 1.5rem; font-weight: 700;">${data.stats.total_rows}</div>
                <div>Total Rows</div>
            </div>
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 1rem; border-radius: 6px; text-align: center;">
                <div style="font-size: 1.5rem; font-weight: 700;">${data.stats.total_columns}</div>
                <div>Columns</div>
            </div>
            <div style="background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); color: white; padding: 1rem; border-radius: 6px; text-align: center;">
                <div style="font-size: 1.5rem; font-weight: 700;">${data.stats.numeric_columns}</div>
                <div>Numeric</div>
            </div>
            <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 1rem; border-radius: 6px; text-align: center;">
                <div style="font-size: 1.5rem; font-weight: 700;">${data.stats.categorical_columns}</div>
                <div>Categorical</div>
            </div>
        </div>
    `;
    document.getElementById('auto-stats').innerHTML = statsHtml;

    // Display insights
    const insightsHtml = `
        <div style="background: #eff6ff; padding: 1.5rem; border-radius: 6px; border-left: 4px solid #3b82f6;">
            <h3 style="margin-top: 0; color: #1e40af;">📊 Key Insights</h3>
            <ul style="margin: 0;">
                ${data.insights.map(insight => `<li>${insight}</li>`).join('')}
            </ul>
        </div>
    `;
    document.getElementById('auto-insights').innerHTML = insightsHtml;

    // Render charts
    renderCharts(data.charts);
}

function renderCharts(charts) {
    const container = document.getElementById('charts-container');
    container.innerHTML = '';

    charts.forEach((chart, index) => {
        const chartDiv = document.createElement('div');
        chartDiv.className = 'chart-container';

        const canvas = document.createElement('canvas');
        canvas.id = `chart-${index}`;
        chartDiv.appendChild(canvas);
        container.appendChild(chartDiv);

        new Chart(canvas, {
            type: chart.type,
            data: chart.data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: chart.title
                    }
                }
            }
        });
    });
}

async function askQuestion() {
    const query = document.getElementById('query-input').value.trim();

    if (!query) {
        showError('Please enter a question');
        return;
    }

    try {
        showLoading('Processing query...');

        const response = await fetch('/upload/analyze-prompt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });

        const data = await response.json();

        if (data.success) {
            const responseHtml = `
                <div style="background: #f3f4f6; padding: 1rem; border-radius: 6px; margin-top: 1rem;">
                    <strong>Query:</strong> ${data.query}<br>
                    <strong>Response:</strong> ${data.message}
                </div>
            `;
            document.getElementById('prompt-response').innerHTML = responseHtml;
        } else {
            showError(data.error);
        }
    } catch (error) {
        showError('Query failed: ' + error.message);
    } finally {
        hideLoading();
    }
}

// ============================================================================
// Tab Switching
// ============================================================================

function switchTab(tab) {
    if (tab === 'auto') {
        document.getElementById('auto-mode-tab').classList.remove('hidden');
        document.getElementById('prompt-mode-tab').classList.add('hidden');
        document.querySelectorAll('.tab')[0].classList.add('active');
        document.querySelectorAll('.tab')[1].classList.remove('active');
    } else {
        document.getElementById('auto-mode-tab').classList.add('hidden');
        document.getElementById('prompt-mode-tab').classList.remove('hidden');
        document.querySelectorAll('.tab')[0].classList.remove('active');
        document.querySelectorAll('.tab')[1].classList.add('active');
    }
}

// ============================================================================
// Utility Functions
// ============================================================================

function displayTable(tableId, data, columns) {
    if (!data || data.length === 0) return;

    const table = document.getElementById(tableId);
    let html = '<thead><tr>';
    columns.forEach(col => {
        html += `<th>${col}</th>`;
    });
    html += '</tr></thead><tbody>';

    data.forEach(row => {
        html += '<tr>';
        columns.forEach(col => {
            html += `<td>${row[col] !== null && row[col] !== undefined ? row[col] : ''}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody>';

    table.innerHTML = html;
}

function updateProgress(step) {
    currentStep = step;

    // Update indicators
    for (let i = 1; i <= 6; i++) {
        const indicator = document.getElementById(`step${i}-indicator`);
        if (i < step) {
            indicator.classList.add('completed');
            indicator.classList.remove('active');
        } else if (i === step) {
            indicator.classList.add('active');
            indicator.classList.remove('completed');
        } else {
            indicator.classList.remove('active', 'completed');
        }
    }
}

function showLoading(message) {
    // Simple loading implementation
    document.body.style.cursor = 'wait';
}

function hideLoading() {
    document.body.style.cursor = 'default';
}

function showError(message) {
    alert('Error: ' + message);
}
