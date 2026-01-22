// State Management
const state = {
    jobDescription: '',
    resumes: [], // Now stores actual File objects
    rankings: [],
    darkMode: localStorage.getItem('darkMode') === 'true'
};

// DOM Elements
const jobDescriptionEl = document.getElementById('jobDescription');
const resumeInputEl = document.getElementById('resumeInput');
const fileListEl = document.getElementById('fileList');
const clearFilesBtn = document.getElementById('clearFilesBtn');
const rankButtonEl = document.getElementById('rankButton');
const clearButtonEl = document.getElementById('clearButton');
const rankingsListEl = document.getElementById('rankingsList');
const errorBoxEl = document.getElementById('errorBox');
const errorTextEl = document.getElementById('errorText');
const themeToggleEl = document.getElementById('themeToggle');

// Initialize
function init() {
    setupEventListeners();
    initTheme();
}

// Theme Management (Unchanged)
function initTheme() {
    const htmlElement = document.documentElement;
    if (state.darkMode) {
        htmlElement.classList.add('dark-mode');
        updateThemeIcon();
    }
}

function toggleTheme() {
    state.darkMode = !state.darkMode;
    const htmlElement = document.documentElement;
    if (state.darkMode) {
        htmlElement.classList.add('dark-mode');
    } else {
        htmlElement.classList.remove('dark-mode');
    }
    localStorage.setItem('darkMode', state.darkMode);
    updateThemeIcon();
}

function updateThemeIcon() {
    const icon = themeToggleEl.querySelector('i');
    if (state.darkMode) {
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
    } else {
        icon.classList.remove('fa-sun');
        icon.classList.add('fa-moon');
    }
}

// Event Listeners
function setupEventListeners() {
    jobDescriptionEl.addEventListener('input', (e) => {
        state.jobDescription = e.target.value;
    });

    resumeInputEl.addEventListener('change', handleAddResume);
    clearFilesBtn.addEventListener('click', handleClearFiles);
    rankButtonEl.addEventListener('click', handleRank);
    clearButtonEl.addEventListener('click', handleClear);
    themeToggleEl.addEventListener('click', toggleTheme);
}

// --- UPDATED FILE MANAGEMENT ---
function handleAddResume(e) {
    const files = Array.from(e.target.files);
    
    // Store the actual File object for sending to API
    files.forEach(file => {
        state.resumes.push(file);
    });

    renderFileList();
    resumeInputEl.value = ''; // Reset input
}

function handleRemoveFile(idx) {
    state.resumes.splice(idx, 1);
    renderFileList();
}

function handleClearFiles() {
    state.resumes = [];
    renderFileList();
}

function renderFileList() {
    fileListEl.innerHTML = '';

    if (state.resumes.length === 0) {
        clearFilesBtn.style.display = 'none';
        return;
    }

    clearFilesBtn.style.display = 'flex';

    state.resumes.forEach((file, idx) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';

        const displayName = file.name.length > 40 ? file.name.substring(0, 37) + '…' : file.name;

        fileItem.innerHTML = `
            <div class="file-info">
                <i class="fas fa-check" style="color: #10b981; font-size: 0.875rem;"></i>
                <span class="file-name" title="${file.name}">${displayName}</span>
            </div>
            <button class="file-remove" title="Remove">Remove</button>
        `;

        fileItem.querySelector('.file-remove').addEventListener('click', () => {
            handleRemoveFile(idx);
        });

        fileListEl.appendChild(fileItem);
    });
}

// --- UPDATED RANKING LOGIC WITH API ---
async function handleRank() {
    // Validation
    if (!state.jobDescription.trim()) {
        showError('Please enter a job description');
        return;
    }

    if (state.resumes.length === 0) {
        showError('Please upload at least one resume');
        return;
    }

    hideError();
    rankButtonEl.disabled = true;
    rankButtonEl.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';

    const results = [];

    try {
        // Send each resume to the backend one by one
        // (Using a loop to handle multiple files)
        for (const file of state.resumes) {
            const formData = new FormData();
            formData.append('job_description', state.jobDescription);
            formData.append('file', file);

            const response = await fetch('https://resume-jd-matching-ml.onrender.com/match', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Error processing ${file.name}`);
            }

            const jsonResponse = await response.json();
            
            if (jsonResponse.status === 'success') {
                const data = jsonResponse.data;
                
                // Add result to our list
                results.push({
                    name: jsonResponse.filename,
                    preview: "Processed via Gemini & ML", // Static text or extract from response
                    hybridScore: data.match_percentage, // The main score
                    skillScore: data.match_percentage,  // Using same score for demo (or ask backend for split)
                    textScore: data.match_percentage,   // Using same score for demo
                    matchedSkills: data.extracted_skills, // Skills from Gemini
                    totalJobSkills: data.extracted_skills.length + data.missing_skills.length
                });
            }
        }

        // Sort results: Highest score first
        state.rankings = results.sort((a, b) => b.hybridScore - a.hybridScore);
        
        renderRankings();

    } catch (error) {
        console.error(error);
        showError('Failed to connect to the server. Is the backend running?');
    } finally {
        rankButtonEl.disabled = false;
        rankButtonEl.innerHTML = '<i class="fas fa-fire"></i> Analyze Resumes';
    }
}

function renderRankings() {
    rankingsListEl.innerHTML = '';

    if (state.rankings.length === 0) {
        rankingsListEl.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">
                    <i class="fas fa-briefcase"></i>
                </div>
                <p class="empty-text">No results found. Check your inputs and try again.</p>
            </div>
        `;
        return;
    }

    state.rankings.forEach((ranking, idx) => {
        const card = createRankingCard(ranking, idx);
        rankingsListEl.appendChild(card);
    });
}

function createRankingCard(ranking, idx) {
    const card = document.createElement('div');
    card.className = 'rank-card';

    const headerHTML = `
        <div class="rank-header">
            <div class="rank-info">
                <div class="rank-number">Rank #${idx + 1}</div>
                <h3 class="rank-name">${ranking.name}</h3>
                <p class="rank-preview">${ranking.preview}</p>
            </div>
            <div class="rank-score">
                <div class="rank-score-num">${ranking.hybridScore}</div>
                <div class="rank-score-label">MATCH SCORE</div>
            </div>
        </div>
    `;

    // Note: I am reusing the hybridScore for both bars for simplicity.
    // Ideally, your backend should return separate 'text_similarity' and 'skill_similarity' scores.
    const metricsHTML = `
        <div class="metrics-grid">
            <div class="metric">
                <div class="metric-label">Overall Match</div>
                <div class="metric-value">${ranking.skillScore}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${ranking.skillScore}%"></div>
                </div>
            </div>
            <div class="metric">
                <div class="metric-label">Confidence</div>
                <div class="metric-value">${ranking.textScore}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${ranking.textScore}%"></div>
                </div>
            </div>
        </div>
    `;

    let skillsHTML = `
        <div class="skills-section">
            <div class="skills-label">Detected Skills (${ranking.matchedSkills.length})</div>
            <div class="skills-list">
    `;

    // Display first 7 skills
    ranking.matchedSkills.slice(0, 7).forEach(skill => {
        skillsHTML += `<span class="skill-badge">${skill}</span>`;
    });

    if (ranking.matchedSkills.length > 7) {
        skillsHTML += `<span class="skill-badge skill-more">+${ranking.matchedSkills.length - 7}</span>`;
    }

    skillsHTML += `
            </div>
        </div>
    `;

    card.innerHTML = headerHTML + metricsHTML + skillsHTML;
    return card;
}

// Error Handling
function showError(message) {
    errorTextEl.textContent = message;
    errorBoxEl.classList.add('show');
}

function hideError() {
    errorBoxEl.classList.remove('show');
}

// Clear All
function handleClear() {
    state.jobDescription = '';
    state.resumes = [];
    state.rankings = [];

    jobDescriptionEl.value = '';
    fileListEl.innerHTML = '';
    clearFilesBtn.style.display = 'none';
    rankingsListEl.innerHTML = `
        <div class="empty-state">
            <div class="empty-icon">
                <i class="fas fa-briefcase"></i>
            </div>
            <p class="empty-text">Add a job description and resumes to see ranked results</p>
        </div>
    `;
    hideError();
}

// Start
init();