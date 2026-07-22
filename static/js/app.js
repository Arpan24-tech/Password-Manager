// Utility Helper: Display Status Messages
function showMessage(elementId, text, isError = false) {
    const msgBox = document.getElementById(elementId);
    if (!msgBox) return;

    msgBox.textContent = text;
    msgBox.className = `message-box ${isError ? 'error' : 'success'}`;
    msgBox.style.display = 'block';
}

// 1. Handle User Registration
async function handleRegister(event) {
    event.preventDefault();
    const username = document.getElementById('username').value.trim();
    const masterPass = document.getElementById('master-pass').value;
    const confirmPass = document.getElementById('confirm-pass').value;

    if (masterPass !== confirmPass) {
        showMessage('message', 'Master passwords do not match.', true);
        return;
    }

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, master_password: masterPass })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('message', 'Account created! Redirecting to login...');
            setTimeout(() => {
                window.location.href = '/login';
            }, 1500);
        } else {
            showMessage('message', data.message || 'Registration failed.', true);
        }
    } catch (err) {
        showMessage('message', 'An error occurred while connecting to server.', true);
    }
}

// 2. Handle User Login
async function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById('username').value.trim();
    const masterPass = document.getElementById('master-pass').value;

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, master_password: masterPass })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('message', 'Login successful! Unlocking vault...');
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
        } else {
            showMessage('message', data.message || 'Invalid credentials.', true);
        }
    } catch (err) {
        showMessage('message', 'An error occurred while connecting to server.', true);
    }
}

// 3. Handle Adding New Vault Credentials
async function handleAddEntry(event) {
    event.preventDefault();
    const service = document.getElementById('service').value.trim();
    const username = document.getElementById('vault-user').value.trim();
    const password = document.getElementById('vault-pass').value;

    try {
        const response = await fetch('/api/vault/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ service, username, password })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('vault-message', data.message);
            document.getElementById('vault-form').reset();
            loadVaultEntries(); // Refresh table view
        } else {
            showMessage('vault-message', data.message || 'Failed to save entry.', true);
        }
    } catch (err) {
        showMessage('vault-message', 'An error occurred while saving credential.', true);
    }
}

// 4. Load & Display Vault Entries
async function loadVaultEntries() {
    const tableBody = document.getElementById('vault-table-body');
    if (!tableBody) return; // Exit if not on dashboard page

    try {
        const response = await fetch('/api/vault/get');
        const data = await response.json();

        if (response.ok && data.entries) {
            if (data.entries.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="4" class="text-center">No stored credentials found. Add one above!</td></tr>';
                return;
            }

            tableBody.innerHTML = '';
            data.entries.forEach(entry => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><strong>${escapeHtml(entry.service)}</strong></td>
                    <td>${escapeHtml(entry.username)}</td>
                    <td>
                        <input type="password" value="${escapeHtml(entry.password)}" readonly id="pass-${entry.id}" 
                               style="background: transparent; border: none; color: #fff; width: 120px;" />
                    </td>
                    <td>
                        <button class="btn-action" onclick="togglePasswordVisibility('pass-${entry.id}', this)">Show</button>
                        <button class="btn-action" onclick="copyToClipboard('${escapeHtml(entry.password)}')">Copy</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        }
    } catch (err) {
        tableBody.innerHTML = '<tr><td colspan="4" class="text-center">Error loading vault entries.</td></tr>';
    }
}

// Helper: Toggle Password Masking
function togglePasswordVisibility(inputId, btn) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = 'Hide';
    } else {
        input.type = 'password';
        btn.textContent = 'Show';
    }
}

// Helper: Copy Password to Clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('Password copied to clipboard!');
    });
}

// Helper: Prevent XSS injection in dynamic text
function escapeHtml(str) {
    return str.replace(/[&<>"']/g, function (m) {
        return {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        }[m];
    });
}

// Initialize Vault Data on Dashboard Load
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('vault-table-body')) {
        loadVaultEntries();
    }
});