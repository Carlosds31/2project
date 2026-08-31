document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const emailInput = document.getElementById('emailInput');
    const emailSuggestions = document.getElementById('emailSuggestions');
    const quickKeys = document.getElementById('quickKeys');

    const passwordInput = document.getElementById('passwordInput');
    const togglePasswordBtn = document.getElementById('togglePasswordBtn');
    const eyeOpenIcon = document.getElementById('eyeOpenIcon');
    const eyeClosedIcon = document.getElementById('eyeClosedIcon');

    const loginForm = document.getElementById('loginForm');

    const googleBtn = document.getElementById('googleBtn');
    const googleModal = document.getElementById('googleModal');
    const closeGoogleModal = document.getElementById('closeGoogleModal');
    const googleAccountItems = document.querySelectorAll('.google-account-item');

    // Domains for email smart suggestions
    const DOMAINS = ['gmail.com', 'outlook.com', 'yahoo.com', 'icloud.com'];

    // ------------------------------------------------------------------
    // 1. Email Smart Suggestions & Quick Keys
    // ------------------------------------------------------------------
    function updateEmailSuggestions() {
        const val = emailInput.value.trim();
        emailSuggestions.innerHTML = '';

        // If empty or purely numbers (likely phone number), hide suggestions
        if (!val || /^\d+$/.test(val)) {
            emailSuggestions.hidden = true;
            return;
        }

        let prefix = val;
        let domainSearch = '';

        if (val.includes('@')) {
            const parts = val.split('@');
            prefix = parts[0];
            domainSearch = parts[1].toLowerCase();
        }

        // Don't suggest if user already typed full domain with extension
        if (domainSearch.includes('.') && DOMAINS.some(d => domainSearch === d)) {
            emailSuggestions.hidden = true;
            return;
        }

        if (!prefix) {
            emailSuggestions.hidden = true;
            return;
        }

        const filteredDomains = DOMAINS.filter(d => d.startsWith(domainSearch));

        if (filteredDomains.length === 0) {
            emailSuggestions.hidden = true;
            return;
        }

        filteredDomains.forEach(domain => {
            const li = document.createElement('li');
            li.role = 'option';
            li.textContent = `${prefix}@${domain}`;
            li.addEventListener('mousedown', (e) => {
                e.preventDefault(); // Prevent input blur
                emailInput.value = `${prefix}@${domain}`;
                emailSuggestions.hidden = true;
                passwordInput.focus();
            });
            emailSuggestions.appendChild(li);
        });

        emailSuggestions.hidden = false;
    }

    emailInput.addEventListener('input', updateEmailSuggestions);

    emailInput.addEventListener('focus', () => {
        if (emailInput.value.trim()) {
            updateEmailSuggestions();
        }
    });

    emailInput.addEventListener('blur', () => {
        // Delay hiding so mousedown on suggestion works
        setTimeout(() => {
            emailSuggestions.hidden = true;
        }, 150);
    });

    // Quick Keys (@ and .com)
    if (quickKeys) {
        quickKeys.addEventListener('click', (e) => {
            const btn = e.target.closest('.quick-key-btn');
            if (!btn) return;

            const insertText = btn.getAttribute('data-insert');
            const start = emailInput.selectionStart || emailInput.value.length;
            const end = emailInput.selectionEnd || emailInput.value.length;
            const currentVal = emailInput.value;

            // Avoid adding double @ or double .com
            if (insertText === '@' && currentVal.includes('@')) {
                emailInput.focus();
                return;
            }
            if (insertText === '.com' && currentVal.endsWith('.com')) {
                emailInput.focus();
                return;
            }

            emailInput.value = currentVal.substring(0, start) + insertText + currentVal.substring(end);
            emailInput.focus();
            const newCursorPos = start + insertText.length;
            emailInput.setSelectionRange(newCursorPos, newCursorPos);

            updateEmailSuggestions();
        });
    }

    // ------------------------------------------------------------------
    // 2. Toggle Password Visibility
    // ------------------------------------------------------------------
    if (togglePasswordBtn) {
        togglePasswordBtn.addEventListener('click', () => {
            const isPassword = passwordInput.getAttribute('type') === 'password';
            if (isPassword) {
                passwordInput.setAttribute('type', 'text');
                eyeOpenIcon.style.display = 'none';
                eyeClosedIcon.style.display = 'block';
                togglePasswordBtn.setAttribute('aria-label', 'Masquer le mot de passe');
            } else {
                passwordInput.setAttribute('type', 'password');
                eyeOpenIcon.style.display = 'block';
                eyeClosedIcon.style.display = 'none';
                togglePasswordBtn.setAttribute('aria-label', 'Afficher le mot de passe');
            }
        });
    }

    // ------------------------------------------------------------------
    // 3. Google Sign-In Direct Account Selection
    // ------------------------------------------------------------------
    if (googleBtn && googleModal) {
        googleBtn.addEventListener('click', () => {
            googleModal.hidden = false;
            googleModal.setAttribute('aria-hidden', 'false');
        });

        closeGoogleModal.addEventListener('click', () => {
            googleModal.hidden = true;
            googleModal.setAttribute('aria-hidden', 'true');
        });

        googleModal.addEventListener('click', (e) => {
            if (e.target === googleModal) {
                googleModal.hidden = true;
                googleModal.setAttribute('aria-hidden', 'true');
            }
        });

        googleAccountItems.forEach(item => {
            item.addEventListener('click', () => {
                const selectedEmail = item.getAttribute('data-email');
                if (selectedEmail) {
                    emailInput.value = selectedEmail;
                    googleModal.hidden = true;
                    googleModal.setAttribute('aria-hidden', 'true');

                    // Simulate account sign-in feedback
                    alert(`Connexion réussie avec le compte Google : ${selectedEmail}`);
                }
            });
        });
    }

    // ------------------------------------------------------------------
    // 4. Form Submission
    // ------------------------------------------------------------------
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const email = emailInput.value.trim();
            const password = passwordInput.value;

            if (!email || !password) {
                alert('Veuillez remplir tous les champs.');
                return;
            }

            alert(`Connexion effectuée pour : ${email}`);
        });
    }
});
