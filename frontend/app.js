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
        state.resumes.push(file);
    });
    renderFileList();
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

// --- CORE RANKING LOGIC ---
async function handleRank() {
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
        // Loop through each file and send to API
        for (const file of state.resumes) {
            const formData = new FormData();
            formData.append('job_description', state.jobDescription);
            formData.append('file', file);

            // ⚠️ REPLACE THIS URL WITH YOUR ACTUAL RENDER URL ⚠️
            // Example: https://resume-matcher-api.onrender.com/match
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
                
                results.push({
                    name: jsonResponse.filename,
                    preview: "Processed via Gemini & ML", 
                    hybridScore: data.match_percentage, 
                    // Store both lists from backend
                    matchedSkills: data.extracted_skills || [], 
                    missingSkills: data.missing_skills || []
                });
            }
        }

        // Sort by Score (High to Low)
        state.rankings = results.sort((a, b) => b.hybridScore - a.hybridScore);
        renderRankings();

    } catch (error) {
        console.error(error);
        showError('Connection failed. Make sure your Backend API is running.');
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
                <div class="empty-icon"><i class="fas fa-briefcase"></i></div>
                <p class="empty-text">No results found.</p>
            </div>`;
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

    // 1. Card Header
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

    // 2. Score Bar
    const metricsHTML = `
        <div class="metrics-grid">
            <div class="metric" style="grid-column: span 2;">
                <div class="metric-label">Overall Match</div>
                <div class="metric-value">${ranking.hybridScore}%</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${ranking.hybridScore}%"></div>
                </div>
            </div>
        </div>
    `;

    // 3. Matched Skills (Green)
    let skillsHTML = `
        <div class="skills-section">
            <div class="skills-label">✅ Detected Skills (${ranking.matchedSkills.length})</div>
            <div class="skills-list">
    `;
    
    // Show first 10 matched skills
    ranking.matchedSkills.slice(0, 10).forEach(skill => {
        skillsHTML += `<span class="skill-badge">${skill}</span>`;
    });
    if (ranking.matchedSkills.length > 10) {
        skillsHTML += `<span class="skill-badge skill-more">+${ranking.matchedSkills.length - 10}</span>`;
    }
    skillsHTML += `</div></div>`;

    // 4. Missing Skills (Red) - NEW SECTION
    if (ranking.missingSkills.length > 0) {
        skillsHTML += `
            <div class="skills-section" style="margin-top: 1rem;">
                <div class="skills-label" style="color: #ef4444;">❌ Missing Skills (${ranking.missingSkills.length})</div>
                <div class="skills-list">
        `;
        
        ranking.missingSkills.slice(0, 10).forEach(skill => {
            // Inline styles for red badges
            skillsHTML += `<span class="skill-badge" style="background: #fef2f2; color: #ef4444; border: 1px solid #fecaca;">${skill}</span>`;
        });
        
        if (ranking.missingSkills.length > 10) {
            skillsHTML += `<span class="skill-badge skill-more" style="background: #fef2f2; color: #ef4444; border: 1px solid #fecaca;">+${ranking.missingSkills.length - 10}</span>`;
        }
        skillsHTML += `</div></div>`;
    }

    card.innerHTML = headerHTML + metricsHTML + skillsHTML;
    return card;
}

// Utilities
function showError(message) {
    errorTextEl.textContent = message;
    errorBoxEl.classList.add('show');
}
function hideError() {
    errorBoxEl.classList.remove('show');
}
function handleClear() {
    state.jobDescription = '';
    state.resumes = [];
    state.rankings = [];
    jobDescriptionEl.value = '';
    fileListEl.innerHTML = '';
    clearFilesBtn.style.display = 'none';
    rankingsListEl.innerHTML = `
        <div class="empty-state">
            <div class="empty-icon"><i class="fas fa-briefcase"></i></div>
            <p class="empty-text">Add a job description and resumes to see ranked results</p>
        </div>
    `;
    hideError();
}

init();