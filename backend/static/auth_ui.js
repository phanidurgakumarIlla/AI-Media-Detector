document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    if (token) {
        window.location.href = '/';
        return;
    }

    // Sections
    const sectionLogin = document.getElementById('section-login');
    const sectionRegister = document.getElementById('section-register');
    const sectionOtp = document.getElementById('section-otp');

    // Tabs
    const tabLogin = document.getElementById('tab-login');
    const tabRegister = document.getElementById('tab-register');

    // Labels & Errors
    const authError = document.getElementById('auth-error');
    const authSuccess = document.getElementById('auth-success');
    const displayEmailSent = document.getElementById('display-email');

    let currentUsername = ''; // To track who we are verifying

    function switchSection(targetSection) {
        [sectionLogin, sectionRegister, sectionOtp].forEach(s => {
            s.classList.remove('active');
            s.classList.add('hidden');
        });
        targetSection.classList.add('active');
        targetSection.classList.remove('hidden');
        
        authError.classList.add('hidden');
        authSuccess.classList.add('hidden');
    }

    tabLogin.addEventListener('click', () => {
        switchSection(sectionLogin);
        tabLogin.classList.add('active');
        tabRegister.classList.remove('active');
    });

    tabRegister.addEventListener('click', () => {
        switchSection(sectionRegister);
        tabRegister.classList.add('active');
        tabLogin.classList.remove('active');
    });

    // --- Login Logic ---
    const formLogin = document.getElementById('form-login');
    if (formLogin) {
        formLogin.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('login-username').value;
            const password = document.getElementById('login-password').value;
            
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            try {
                const res = await fetch('/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: formData
                });
                const data = await res.json();
                if (!res.ok) {
                    if (res.status === 403) {
                        currentUsername = username;
                        displayEmailSent.textContent = "your account (please check terminal for OTP)";
                        switchSection(sectionOtp);
                        throw new Error("Account not verified. Check terminal for code.");
                    }
                    throw new Error(data.detail || 'Login failed');
                }
                localStorage.setItem('token', data.access_token);
                window.location.href = '/';
            } catch (err) {
                authError.textContent = err.message;
                authError.classList.remove('hidden');
            }
        });
    }

    // --- Registration Logic ---
    const formReg = document.getElementById('form-register');
    if (formReg) {
        formReg.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('reg-username').value;
            const email = document.getElementById('reg-email').value;
            const password = document.getElementById('reg-password').value;
            
            try {
                const res = await fetch('/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, email, password })
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Registration failed');

                currentUsername = username;
                displayEmailSent.textContent = email;
                
                authSuccess.textContent = "Step 1 complete! Enter the OTP now.";
                authSuccess.classList.remove('hidden');
                
                setTimeout(() => switchSection(sectionOtp), 800);
            } catch (err) {
                authError.textContent = err.message;
                authError.classList.remove('hidden');
            }
        });
    }

    // --- OTP Verification Logic ---
    document.getElementById('btn-otp-verify').addEventListener('click', async () => {
        const otp = document.getElementById('otp-code').value;
        if (otp.length < 6) return;

        try {
            const res = await fetch('/auth/verify-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: currentUsername, otp_code: otp })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Verification failed');

            authSuccess.textContent = "Verified! You can now log in.";
            authSuccess.classList.remove('hidden');
            
            setTimeout(() => {
                switchSection(sectionLogin);
                tabLogin.classList.add('active');
                tabRegister.classList.remove('active');
            }, 1500);
        } catch (err) {
            authError.textContent = err.message;
            authError.classList.remove('hidden');
        }
    });

    document.getElementById('btn-otp-back').addEventListener('click', () => switchSection(sectionRegister));

    // --- Google Auth Simulation ---
    const handleGoogleSimulate = async () => {
        // Use a default demo account directly to avoid prompt blocks in some browsers
        const email = "demo.user@gmail.com"; 
        
        try {
            authSuccess.textContent = "Connecting to Google Account Picker...";
            authSuccess.classList.remove('hidden');

            const res = await fetch('/auth/google-auth', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Google Auth failed');

            localStorage.setItem('token', data.access_token);
            authSuccess.textContent = `Success! Logged in as ${data.username} via Google.`;
            authSuccess.classList.remove('hidden');
            setTimeout(() => window.location.href = '/', 1000);
        } catch (err) {
            authError.textContent = err.message;
            authError.classList.remove('hidden');
        }
    };

    document.getElementById('btn-google-login').addEventListener('click', handleGoogleSimulate);
    document.getElementById('btn-google-reg').addEventListener('click', handleGoogleSimulate);

    // --- Robot Animation Logic ---
    const robot = document.getElementById('login-robot');
    if (robot) {
        const pupils = document.querySelectorAll('.eye-pupil');
        const allInputs = document.querySelectorAll('.auth-input');

        allInputs.forEach(input => {
            input.addEventListener('focus', () => {
                if (input.type === 'password') {
                    robot.classList.add('hiding-eyes');
                } else {
                    robot.classList.remove('hiding-eyes');
                    robot.classList.add('watching');
                }
            });

            input.addEventListener('blur', () => {
                robot.classList.remove('hiding-eyes', 'watching');
            });

            input.addEventListener('input', () => {
                if (input.type !== 'password') {
                    const length = input.value.length;
                    const xOffset = Math.min((length / 20) * 8 - 10, -2);
                    pupils.forEach(p => p.style.transform = `translate(calc(-50% + ${xOffset}px), -50%)`);
                }
            });
        });

        document.addEventListener('mousemove', (e) => {
            if (robot.classList.contains('hiding-eyes')) return;
            const eyes = robot.querySelectorAll('.robot-eye');
            eyes.forEach((eye, i) => {
                const rect = eye.getBoundingClientRect();
                const cx = rect.left + rect.width / 2;
                const cy = rect.top + rect.height / 2;
                const angle = Math.atan2(e.clientY - cy, e.clientX - cx);
                const dist = Math.min(Math.hypot(e.clientX - cx, e.clientY - cy), 8);
                const px = Math.cos(angle) * dist;
                const py = Math.sin(angle) * dist;
                pupils[i].style.transform = `translate(calc(-50% + ${px}px), calc(-50% + ${py}px))`;
            });
        });
    }

    // --- Theme Toggle ---
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const html = document.documentElement;
            const current = html.getAttribute('data-theme') || 'light';
            const next = current === 'light' ? 'dark' : 'light';
            html.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
        });
    }

    // --- Hash Handling for Tab Switching (Phase 38 Restoration) ---
    if (window.location.hash === '#register') {
        if (sectionRegister && tabRegister && tabLogin) {
            switchSection(sectionRegister);
            tabRegister.classList.add('active');
            tabLogin.classList.remove('active');
        }
    }
});

