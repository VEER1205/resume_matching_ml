// State Management
const state = {
    jobDescription: '',
    resumes: [],
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

// Theme Management
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

// File Management
function handleAddResume(e) {
    const files = Array.from(e.target.files);
    
    files.forEach(file => {
        const reader = new FileReader();
        reader.onload = (event) => {
            state.resumes.push({
                name: file.name,
                content: event.target.result
            });
            renderFileList();
        };
        reader.readAsText(file);
    });

    resumeInputEl.value = '';
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

    state.resumes.forEach((resume, idx) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';

        const displayName = resume.name.length > 40 ? resume.name.substring(0, 37) + '…' : resume.name;

        fileItem.innerHTML = `
            <div class="file-info">
                <i class="fas fa-check" style="color: #10b981; font-size: 0.875rem;"></i>
                <span class="file-name" title="${resume.name}">${displayName}</span>
            </div>
            <button class="file-remove" title="Remove">Remove</button>
        `;

        fileItem.querySelector('.file-remove').addEventListener('click', () => {
            handleRemoveFile(idx);
        });

        fileListEl.appendChild(fileItem);
    });
}

// Ranking Logic
function handleRank() {
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
    rankButtonEl.innerHTML = '<i class="fas fa-spinner loading"></i>Analyzing…';

    // Process
    setTimeout(() => {
        state.rankings = rankResumesLogic(state.jobDescription, state.resumes);
        renderRankings();

        rankButtonEl.disabled = false;
        rankButtonEl.innerHTML = '<i class="fas fa-fire"></i>Analyze Resumes';
    }, 800);
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

    const metricsHTML = `
        <div class="metrics-grid">
            <div class="metric">
                <div class="metric-label">Skill Match</div>
                <div class="metric-value">${ranking.skillScore}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${ranking.skillScore}%"></div>
                </div>
            </div>
            <div class="metric">
                <div class="metric-label">Text Similarity</div>
                <div class="metric-value">${ranking.textScore}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${ranking.textScore}%"></div>
                </div>
            </div>
        </div>
    `;

    let skillsHTML = `
        <div class="skills-section">
            <div class="skills-label">Matched Skills (${ranking.matchedSkills.length}/${ranking.totalJobSkills})</div>
            <div class="skills-list">
    `;

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