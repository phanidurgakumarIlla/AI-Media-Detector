document.addEventListener('DOMContentLoaded', async () => {
    // 0. AUTHENTICATION GATE
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    // Verify token validity and fetch user profile
    try {
        const userRes = await fetch('/auth/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!userRes.ok) {
            // Token expired or invalid
            localStorage.removeItem('token');
            window.location.href = 'login.html';
            return;
        }
        const userData = await userRes.json();

        // Navigation Container (Top Right)
        const navContainer = document.createElement('div');
        navContainer.style.position = 'absolute';
        navContainer.style.top = '1.5rem';
        navContainer.style.right = '1.5rem';
        navContainer.style.display = 'flex';
        navContainer.style.gap = '1rem';
        navContainer.style.zIndex = '1000';

        // Show Admin Panel Button if admin
        if (userData.role === 'admin') {
            const adminBtn = document.createElement('button');
            adminBtn.onclick = () => { window.location.href = 'admin.html'; };
            adminBtn.className = 'btn outline';
            adminBtn.style.padding = '0.5rem 1rem';
            adminBtn.textContent = 'Admin Panel';
            navContainer.appendChild(adminBtn);
        }

        // Add Logout Button (Moved from tabs)
        const logoutBtn = document.createElement('button');
        logoutBtn.className = 'btn';
        logoutBtn.style.padding = '0.5rem 1rem';
        logoutBtn.style.backgroundColor = 'var(--danger)';
        logoutBtn.style.borderColor = 'var(--danger)';
        logoutBtn.style.color = '#fff';
        logoutBtn.textContent = 'Logout';
        logoutBtn.onclick = () => {
            localStorage.removeItem('token');
            window.location.href = 'login.html';
        };
        navContainer.appendChild(logoutBtn);
        document.body.appendChild(navContainer);

        // Unhide the app now that auth is verified
        document.getElementById('app-content').style.display = 'block';

    } catch (err) {
        localStorage.removeItem('token');
        window.location.href = 'login.html';
        return;
    }

    // Elements
    const tabUpload = document.getElementById('tab-upload');
    const tabInstagram = document.getElementById('tab-instagram');
    const tabYoutube = document.getElementById('tab-youtube');

    const sectionUpload = document.getElementById('section-upload');
    const sectionInstagram = document.getElementById('section-instagram');
    const sectionYoutube = document.getElementById('section-youtube');

    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileNameDisplay = document.getElementById('file-name');
    const fileSizeDisplay = document.getElementById('file-size');
    const btnAnalyzeUpload = document.getElementById('btn-analyze-upload');

    const urlInstagram = document.getElementById('url-instagram');
    const btnAnalyzeInstagram = document.getElementById('btn-analyze-instagram');

    const urlYoutube = document.getElementById('url-youtube');
    const btnAnalyzeYoutube = document.getElementById('btn-analyze-youtube');

    const inputContainer = document.getElementById('input-container');
    const loadingContainer = document.getElementById('loading-container');
    const resultContainer = document.getElementById('result-container');
    const errorMsg = document.getElementById('error-message');

    const btnReset = document.getElementById('btn-reset');
    const progressCircle = document.querySelector('.progress-circle .progress');
    const scoreText = document.getElementById('score-text');
    const verdictHeading = document.getElementById('verdict-heading');
    const verdictDetails = document.getElementById('verdict-details');
    const aiConf = document.getElementById('ai-conf');
    const realConf = document.getElementById('real-conf');

    // Model Detail Elements
    const modelDetailsPanel = document.getElementById('model-details-panel');
    const detailModelName = document.getElementById('detail-model-name');
    const detailModelType = document.getElementById('detail-model-type');
    const detailModelDataset = document.getElementById('detail-model-dataset');
    const detailModelAccuracy = document.getElementById('detail-model-accuracy');

    // Algorithm Badge
    const algorithmIcon = document.getElementById('algorithm-icon');
    const algorithmName = document.getElementById('algorithm-name');
    const algorithmBadge = document.getElementById('algorithm-badge');

    // Chart elements
    const chartAiBar  = document.getElementById('chart-ai-bar');
    const chartRealBar = document.getElementById('chart-real-bar');
    const chartConfBar = document.getElementById('chart-conf-bar');
    const chartAiPct  = document.getElementById('chart-ai-pct');
    const chartRealPct = document.getElementById('chart-real-pct');
    const chartConfPct = document.getElementById('chart-conf-pct');

    // Model Performance Chart Elements
    const chartAccuracyBar = document.getElementById('chart-accuracy-bar');
    const chartPrecisionBar = document.getElementById('chart-precision-bar');
    const chartRecallBar = document.getElementById('chart-recall-bar');
    const chartF1Bar = document.getElementById('chart-f1-bar');
    
    const chartAccuracyPct = document.getElementById('chart-accuracy-pct');
    const chartPrecisionPct = document.getElementById('chart-precision-pct');
    const chartRecallPct = document.getElementById('chart-recall-pct');
    const chartF1Pct = document.getElementById('chart-f1-pct');
    
    const modelPerfName = document.getElementById('model-perf-name');

    // Confusion Matrix Elements
    const matrixTP = document.getElementById('matrix-tp');
    const matrixFP = document.getElementById('matrix-fp');
    const matrixFN = document.getElementById('matrix-fn');
    const matrixTN = document.getElementById('matrix-tn');

    // AI Guide Elements
    const guideText = document.getElementById('guide-text');
    const guideDots = document.querySelectorAll('.guide-dot');

    const setGuideStep = (stepIndex, text) => {
        if (guideText) guideText.textContent = text;
        guideDots.forEach((dot, i) => {
            dot.classList.toggle('active', i === stepIndex);
        });
    }

    // --- In-Page Algorithm Card Selection ---
    const setupAlgoCards = () => {
        const cards = document.querySelectorAll('.algo-card');
        cards.forEach(card => {
            card.addEventListener('click', () => {
                cards.forEach(c => c.classList.remove('active'));
                card.classList.add('active');
                const radio = card.querySelector('input');
                if (radio) radio.checked = true;
                setGuideStep(2, "Algorithm selected. Now provide your media source to begin.");
            });
        });
    };
    setupAlgoCards();;

    let currentFile = null;

    // --- Theme Toggle Logic ---
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            html.classList.add('theme-transition');
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            setTimeout(() => {
                html.classList.remove('theme-transition');
            }, 500);
        });
    }

    // --- Main Page Robot Cursor Tracking ---
    const mainRobot = document.getElementById('main-robot');
    if (mainRobot) {
        document.addEventListener('mousemove', (e) => {
            const eyes = mainRobot.querySelectorAll('.robot-eye');
            const pupils = mainRobot.querySelectorAll('.eye-pupil');
            eyes.forEach((eye, i) => {
                const rect = eye.getBoundingClientRect();
                if (rect.width === 0) return;
                const cx = rect.left + rect.width / 2;
                const cy = rect.top + rect.height / 2;
                const dx = e.clientX - cx;
                const dy = e.clientY - cy;
                const ang = Math.atan2(dy, dx);
                const dist = Math.min(Math.hypot(dx, dy), 8);
                if (pupils[i]) {
                    pupils[i].style.transform = `translate(calc(-50% + ${Math.cos(ang) * dist}px), calc(-50% + ${Math.sin(ang) * dist}px))`;
                }
            });
        });
    }

    // Tabs
    function switchTab(activeTab, activeSection) {
        // Reset all
        [tabUpload, tabInstagram, tabYoutube].forEach(t => t.classList.remove('active'));
        [sectionUpload, sectionInstagram, sectionYoutube].forEach(s => s.classList.remove('active'));
        [sectionUpload, sectionInstagram, sectionYoutube].forEach(s => s.classList.add('hidden'));

        // Set active
        activeTab.classList.add('active');
        activeSection.classList.add('active');
        activeSection.classList.remove('hidden');

        // Guide Update
        setGuideStep(1, "Step 2: Please choose an algorithm and then provide your media.");
    }

    tabUpload.addEventListener('click', () => switchTab(tabUpload, sectionUpload));
    tabInstagram.addEventListener('click', () => switchTab(tabInstagram, sectionInstagram));
    tabYoutube.addEventListener('click', () => switchTab(tabYoutube, sectionYoutube));

    // Drag and Drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }, false);

    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', function () {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length) {
            currentFile = files[0];
            fileNameDisplay.textContent = currentFile.name;
            fileSizeDisplay.textContent = (currentFile.size / (1024 * 1024)).toFixed(2) + ' MB';
            btnAnalyzeUpload.disabled = false;
            setGuideStep(2, "File uploaded successfully. Choose an algorithm or keep 'Auto Cascade' then hit Analyze.");
        }
    }

    // URL Inputs
    urlInstagram.addEventListener('input', () => {
        const val = urlInstagram.value.toLowerCase();
        btnAnalyzeInstagram.disabled = !val.includes('instagram.com');
    });

    urlYoutube.addEventListener('input', () => {
        const val = urlYoutube.value.toLowerCase();
        btnAnalyzeYoutube.disabled = !(val.includes('youtube.com') || val.includes('youtu.be'));
    });

    // Audio Context for the alert beep
    const playAlertSound = () => {
        try {
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

            // Create 3 rapid beeps for maximum alert effect
            for (let i = 0; i < 3; i++) {
                const oscillator = audioCtx.createOscillator();
                const gainNode = audioCtx.createGain();

                oscillator.type = 'square';
                oscillator.frequency.setValueAtTime(800, audioCtx.currentTime + (i * 0.2)); // High pitch

                gainNode.gain.setValueAtTime(0.2, audioCtx.currentTime + (i * 0.2));
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + (i * 0.2) + 0.1);

                oscillator.connect(gainNode);
                gainNode.connect(audioCtx.destination);

                oscillator.start(audioCtx.currentTime + (i * 0.2));
                oscillator.stop(audioCtx.currentTime + (i * 0.2) + 0.15);
            }
        } catch (e) {
            console.error("Audio API not supported");
        }
    };

    // API Calls
    const showError = (msg) => {
        errorMsg.textContent = msg;
        errorMsg.classList.remove('hidden');
        loadingContainer.classList.add('hidden');
        inputContainer.classList.remove('hidden');
    };

    const showLoading = () => {
        errorMsg.classList.add('hidden');
        inputContainer.classList.add('hidden');
        loadingContainer.classList.remove('hidden');
    };

    // Algorithm icon map
    const algoIconMap = {
        'Auto Cascade (ML Consolidated)': { icon: '✨', color: '#8a2be2' },
        'Keyword Heuristic':       { icon: '🏷️', color: '#f59e0b' },
        'Audio Heuristic (AI Signature)': { icon: '🎙️', color: '#ec4899' },
        'Audio Heuristic (Spectral)':   { icon: '📊', color: '#f43f5e' },
        'Fallback Heuristic':      { icon: '⚙️', color: '#6b7280' },
    };

    // Animated bar helper
    function animateBar(barEl, pctEl, targetPct, color, delay = 0) {
        setTimeout(() => {
            let cur = 0;
            const step = targetPct / (900 / 16);
            const iv = setInterval(() => {
                cur = Math.min(cur + step, targetPct);
                barEl.style.width = cur + '%';
                barEl.style.background = color;
                pctEl.textContent = Math.round(cur) + '%';
                if (cur >= targetPct) clearInterval(iv);
            }, 16);
        }, delay);
    }

    const showResult = (result) => {
        console.log("=== AI Media Detector: Analysis Result Received ===");
        console.log(result);
        
        // Save to session storage for "Back to Results" persistence
        sessionStorage.setItem('lastResult', JSON.stringify(result));

        loadingContainer.classList.add('hidden');
        resultContainer.classList.remove('hidden');

        const isFake = result.isFake;
        const primaryColor = isFake ? 'var(--danger)' : 'var(--success)';

        // --- Phase 28/29: Extreme Minimalist & Safe Results Display ---
        if (verdictHeading) {
            verdictHeading.textContent = isFake ? 'AI Generated Content Detected 🤖' : 'Authentic Media Verified ✅';
            verdictHeading.style.color = primaryColor;
            verdictHeading.className = isFake ? 'verdict-fake' : 'verdict-real';
        }
        
        if (verdictDetails) {
            verdictDetails.textContent = result.details || (isFake ? "Neural analysis detected diffusion artifacts and generative patterns." : "Media exhibits natural organic textures and genuine provenance.");
        }
        
        // Hide all secondary analysis panels to ensure "Simplified Mode"
        const toggleHidden = (id) => {
            const el = document.getElementById(id);
            if (el) el.classList.add('hide-metrics', 'hidden');
        };
        
        ['model-details-panel', 'algorithm-badge', 'chart-ai-bar', 'chart-real-bar', 'progress-circle', 'chart-section'].forEach(toggleHidden);

        // Update detection method text only if it exists
        if (algorithmName) algorithmName.textContent = result.algorithmUsed || "Forensic Scan";
    };

    btnAnalyzeUpload.addEventListener('click', async () => {
        if (!currentFile) return;
        showLoading();

        const formData = new FormData();
        formData.append('file', currentFile);
        
        const selectedAlgo = document.querySelector('input[name="algo-global"]:checked')?.value || "auto";
        formData.append('algorithm', selectedAlgo);

        try {
            const res = await fetch('/analyze/upload', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Analysis failed');
            showResult(data);
        } catch (err) {
            showError(err.message);
        }
    });

    const analyzeUrl = async (url) => {
        if (!url) return;
        showLoading();

        try {
            const selectedAlgo = document.querySelector('input[name="algo-global"]:checked')?.value || "auto";
            const res = await fetch('/analyze/url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ url, algorithm: selectedAlgo })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Analysis failed');
            showResult(data);
        } catch (err) {
            showError(err.message);
        }
    }

    btnAnalyzeInstagram.addEventListener('click', () => analyzeUrl(urlInstagram.value));
    btnAnalyzeYoutube.addEventListener('click', () => analyzeUrl(urlYoutube.value));

    // Reset
    btnReset.addEventListener('click', () => {
        resultContainer.classList.add('hidden');
        
        // Force Input Container Visibility
        if (inputContainer) {
            inputContainer.classList.remove('hidden', 'hide-metrics');
            inputContainer.style.display = 'block';
        }
        
        if (dropZone) dropZone.classList.remove('hidden');
        if (imagePreview) imagePreview.classList.add('hidden');
        if (videoPreview) videoPreview.classList.add('hidden');
        if (audioPreview) audioPreview.classList.add('hidden');
        
        // Ensure the active section is shown
        const activeSection = document.querySelector('.section.active');
        if (activeSection) activeSection.classList.remove('hidden');
        // document.body.classList.remove('danger-mode'); // Clean up just in case
        
        // Explicitly clear persistent storage
        sessionStorage.removeItem('lastResult');

        setGuideStep(0, "Ready for a new analysis. Please select a tab to begin.");
        currentFile = null;
        fileNameDisplay.textContent = 'Drag & Drop your media here';
        fileSizeDisplay.textContent = 'We support any Video, Audio, or Photo';
        btnAnalyzeUpload.disabled = true;
        fileInput.value = '';

        urlInstagram.value = '';
        btnAnalyzeInstagram.disabled = true;

        urlYoutube.value = '';
        btnAnalyzeYoutube.disabled = true;


        // Reset animations and guide
        if (progressCircle) progressCircle.style.strokeDashoffset = 565.48;
        if (scoreText) scoreText.textContent = '0%';
        
        // Reset Robot State
        setGuideStep(0, "Ready for a new analysis. Please select a tab to begin.");
    });

    // --- Result Restoration Logic (for 'Back to Analysis' button) ---
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('restore') === 'true') {
        const lastResult = sessionStorage.getItem('lastResult');
        if (lastResult) {
            try {
                const parsed = JSON.parse(lastResult);
                showResult(parsed);
                // Also scroll to result
                setTimeout(() => resultContainer.scrollIntoView({ behavior: 'smooth' }), 500);
                
                // Clean URL after restoration so F5/Refresh doesn't restore again
                window.history.replaceState({}, document.title, window.location.pathname);
            } catch (e) {
                console.error("Failed to restore last result:", e);
            }
        }
    }
});
