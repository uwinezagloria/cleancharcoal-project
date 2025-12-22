// admin.js - Admin User Management Logic

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('👑 Admin User Management Loaded');
    
    // Wait a bit to ensure all elements are ready
    setTimeout(function() {
        loadUsers();
        
        const userForm = document.getElementById('userForm');
        if (userForm) {
            userForm.addEventListener('submit', handleUserFormSubmit);
        }
        
        const userSearch = document.getElementById('userSearch');
        if (userSearch) {
            userSearch.addEventListener('input', function() {
                filterUsers(this.value);
            });
        }

        // Attach event listener to confirm delete button
        const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
        if (confirmDeleteBtn) {
            confirmDeleteBtn.addEventListener('click', confirmDeleteUser);
        }

        // Initialize district/sector field visibility
        if (typeof toggleDistrictSectorFields === 'function') {
            toggleDistrictSectorFields();
        }
    }, 100);
});

let users = [];
let isEditMode = false;

// ===== CRUD OPERATIONS (Real-time API calls) =====

async function loadUsers() {
    try {
        const token = localStorage.getItem('token');
        const csrftoken = getCookie('csrftoken');
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (csrftoken) {
            headers['X-CSRFToken'] = csrftoken;
        }
        if (token) {
            headers['Authorization'] = `Token ${token}`;
        }
        
        const response = await fetch('/api/admin/users/', {
            method: 'GET',
            headers: headers,
            credentials: 'include'
        });

        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '/login/';
                return;
            }
            throw new Error('Failed to load users');
        }

        const data = await response.json();
        console.log('Users data received:', data);
        console.log('Number of users received:', data ? data.length : 0);
        console.log('Type of data:', typeof data);
        console.log('Is array?', Array.isArray(data));
        
        if (!Array.isArray(data)) {
            console.error('Expected array but got:', typeof data, data);
            document.getElementById('totalUsersCount').textContent = 'Error: Invalid data format';
            document.getElementById('usersTableBody').innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Error: API returned invalid data format. Expected array but got ${typeof data}.
                        <br><small>Check browser console for details.</small>
                    </td>
                </tr>
            `;
            return;
        }
        
        if (data.length === 0) {
            console.warn('API returned empty array - no users found');
            document.getElementById('totalUsersCount').textContent = 'No users found';
        }
        
        // Log all user IDs received from API
        console.log('User IDs from API:', data.map(u => u.id));
        console.log('User usernames from API:', data.map(u => u.username));
        
        // Process all users - don't filter any out
        console.log('Processing users...');
        users = data.map((user, index) => {
            console.log(`Processing user ${index + 1}/${data.length}: ID=${user.id}, username=${user.username}`, user);
            try {
                // Ensure we have all required fields with defaults
                const role = user.role || 'burner';
                const fullName = `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username || 'Unknown';
                const email = user.email || user.username || '';
                
                const processedUser = {
                    id: user.id,
                    fullName: fullName,
                    email: email,
                    username: user.username || '',
                    role: role,
                    status: user.is_active !== undefined ? user.is_active : true,
                    first_name: user.first_name || '',
                    last_name: user.last_name || '',
                    phone: user.phone || '',
                    leader_district: user.leader_district || '',
                    leader_sector: user.leader_sector || ''
                };
                console.log(`Processed user ${index + 1}:`, processedUser);
                return processedUser;
            } catch (error) {
                console.error('Error processing user:', user, error);
                // Return a minimal user object even if processing fails
                const fallbackUser = {
                    id: user.id,
                    fullName: user.username || 'Unknown',
                    email: user.email || user.username || '',
                    username: user.username || '',
                    role: 'burner',
                    status: true,
                    first_name: user.first_name || '',
                    last_name: user.last_name || '',
                    phone: '',
                    leader_district: '',
                    leader_sector: ''
                };
                console.log(`Created fallback user for ${user.id}:`, fallbackUser);
                return fallbackUser;
            }
        }); // Don't filter - all users should have IDs
        
        console.log(`✅ Processed ${users.length} users from ${data.length} API responses`);
        console.log('📋 Final users list with IDs:', users.map(u => ({ id: u.id, username: u.username, role: u.role })));
        
        if (users.length === 0) {
            console.error('❌ No valid users after processing!');
        }
        
        if (users.length !== data.length) {
            console.warn(`⚠️ Warning: Processed ${users.length} users but API returned ${data.length}`);
        }
        
        renderUsers(users);
    } catch (error) {
        console.error('Error loading users:', error);
        document.getElementById('totalUsersCount').textContent = 'Error loading users: ' + error.message;
        document.getElementById('usersTableBody').innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Failed to load users. Please refresh the page.
                </td>
            </tr>
        `;
    }
}

// Toggle district field based on role
window.toggleDistrictSectorFields = function() {
    const role = document.getElementById('userRole').value;
    const districtFieldGroup = document.getElementById('districtFieldGroup');
    const districtInput = document.getElementById('userDistrict');
    const districtRequired = document.getElementById('districtRequired');
    
    if (role === 'leader') {
        districtFieldGroup.style.display = 'block';
        districtInput.required = true;
        districtRequired.style.display = 'inline';
    } else {
        districtFieldGroup.style.display = 'block';
        districtInput.required = false;
        districtRequired.style.display = 'none';
    }
}

function handleUserFormSubmit(e) {
    e.preventDefault();
    
    const id = document.getElementById('userId').value;
    const fullName = document.getElementById('fullName').value.trim();
    const email = document.getElementById('userEmail').value.trim();
    const role = document.getElementById('userRole').value;
    const password = document.getElementById('userPassword').value;
    const status = document.getElementById('userStatus').checked;
    const district = document.getElementById('userDistrict').value.trim();

    if (!validateEmail(email)) {
        alert('Please enter a valid email address.');
        return;
    }

    // Validate district for leaders
    if (role === 'leader') {
        if (!district) {
            alert('District is required for leaders.');
            return;
        }
    }

    if (isEditMode) {
        updateUser(id, fullName, email, role, password, status);
    } else {
        if (!password) {
            alert('Password is required for new users.');
            return;
        }
        createUser(fullName, email, role, password, status, district);
    }
    
    const userModalEl = document.getElementById('userModal');
    const modalInstance = bootstrap.Modal.getInstance(userModalEl) || new bootstrap.Modal(userModalEl);
    modalInstance.hide();
    
    document.getElementById('userForm').reset();
    // Reset field visibility after form reset
    toggleDistrictSectorFields();
}

async function createUser(fullName, email, role, password, status, district = '') {
    try {
        const token = localStorage.getItem('token');
        const csrftoken = getCookie('csrftoken');
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (csrftoken) {
            headers['X-CSRFToken'] = csrftoken;
        }
        if (token) {
            headers['Authorization'] = `Token ${token}`;
        }

        // Split full name into first and last name
        const nameParts = fullName.trim().split(' ');
        const first_name = nameParts[0] || '';
        const last_name = nameParts.slice(1).join(' ') || '';
        const username = email; // Use email as username

        let endpoint = '';
        let payload = {};

        if (role === 'leader') {
            // For leaders, only district is required
            if (!district) {
                alert('District is required for leaders');
                return;
            }
            
            endpoint = '/api/admin/leaders/';
            payload = {
                username: username,
                password: password,
                first_name: first_name,
                last_name: last_name,
                leader_district: district.trim(),
                leader_sector: '', // Optional, can be empty
                phone: ''
            };
        } else if (role === 'burner' || role === 'producer') {
            endpoint = '/api/admin/burners/create/';
            payload = {
                username: username,
                password: password,
                first_name: first_name,
                last_name: last_name,
                phone: ''
            };
            // Add district only if provided
            if (district && district.trim()) {
                payload.district = district.trim();
            }
        } else {
            alert('Invalid role selected');
            return;
        }

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(payload),
            credentials: 'include'
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || data.detail || 'Failed to create user');
        }

        // Show success modal
        const successMessage = `User <strong>${fullName}</strong> has been successfully created as a <strong>${role.toUpperCase()}</strong>.`;
        document.getElementById('createUserSuccessMessage').innerHTML = successMessage;
        
        const successModal = new bootstrap.Modal(document.getElementById('createUserSuccessModal'));
        successModal.show();
        
        // Reload users from API after a short delay
        setTimeout(() => {
            loadUsers();
        }, 500);

        // Auto-close success modal after 3 seconds
        setTimeout(() => {
            const successModalInstance = bootstrap.Modal.getInstance(document.getElementById('createUserSuccessModal'));
            if (successModalInstance) {
                successModalInstance.hide();
            }
        }, 3000);
    } catch (error) {
        console.error('Error creating user:', error);
        alert('Failed to create user: ' + error.message);
    }
}

async function updateUser(id, fullName, email, role, password, status) {
    try {
        const user = users.find(u => u.id == id);
        if (!user) {
            alert('User not found');
            return;
        }

        const token = localStorage.getItem('token');
        const csrftoken = getCookie('csrftoken');
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (csrftoken) {
            headers['X-CSRFToken'] = csrftoken;
        }
        if (token) {
            headers['Authorization'] = `Token ${token}`;
        }

        // Split full name into first and last name
        const nameParts = fullName.trim().split(' ');
        const first_name = nameParts[0] || '';
        const last_name = nameParts.slice(1).join(' ') || '';

        let endpoint = '';
        let payload = {};

        if (user.role === 'leader') {
            endpoint = `/api/admin/leaders/${id}/`;
            payload = {
                first_name: first_name,
                last_name: last_name,
                leader_district: user.leader_district || '',
                leader_sector: user.leader_sector || '',
                phone: user.phone || ''
            };
            if (password) {
                payload.password = password;
            }
        } else if (user.role === 'burner' || user.role === 'producer') {
            endpoint = `/api/admin/burners/${id}/`;
            payload = {
                first_name: first_name,
                last_name: last_name,
                phone: user.phone || ''
            };
            if (password) {
                payload.password = password;
            }
        } else {
            alert('Cannot update admin users');
            return;
        }

        const response = await fetch(endpoint, {
            method: 'PATCH',
            headers: headers,
            body: JSON.stringify(payload),
            credentials: 'include'
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || data.detail || 'Failed to update user');
        }

        // Update is_active status if changed
        if (status !== user.status) {
            // Note: This might require a separate endpoint or admin action
            console.log('Status change requested but may need separate endpoint');
        }

        alert(`User ${fullName} updated successfully.`);
        loadUsers(); // Reload users from API
    } catch (error) {
        console.error('Error updating user:', error);
        alert('Failed to update user: ' + error.message);
    }
}

// Store the user ID to delete
let userToDeleteId = null;

// Show delete confirmation modal
window.deleteUser = function(id) {
    const user = users.find(u => u.id == id);
    if (!user) {
        alert('User not found');
        return;
    }

    // Check if user is admin
    if (user.role === 'admin') {
        alert('Cannot delete admin users');
        return;
    }

    // Store the user ID to delete
    userToDeleteId = id;

    // Populate modal with user information
    document.getElementById('deleteUserName').textContent = user.fullName || user.username || 'Unknown';
    document.getElementById('deleteUserEmail').textContent = user.email || user.username || 'N/A';
    document.getElementById('deleteUserRole').textContent = (user.role || 'burner').toUpperCase();

    // Show the modal
    const deleteModal = new bootstrap.Modal(document.getElementById('deleteUserModal'));
    deleteModal.show();
}

// Handle confirmed deletion
async function confirmDeleteUser() {
    if (!userToDeleteId) {
        console.error('No user ID to delete');
        return;
    }

    const user = users.find(u => u.id == userToDeleteId);
    if (!user) {
        alert('User not found');
        userToDeleteId = null;
        return;
    }

    // Disable the delete button to prevent double-clicks
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    confirmBtn.disabled = true;
    confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Deleting...';

    try {
        const token = localStorage.getItem('token');
        const csrftoken = getCookie('csrftoken');
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (csrftoken) {
            headers['X-CSRFToken'] = csrftoken;
        }
        if (token) {
            headers['Authorization'] = `Token ${token}`;
        }

        let endpoint = '';
        if (user.role === 'leader') {
            endpoint = `/api/admin/leaders/${userToDeleteId}/`;
        } else if (user.role === 'burner' || user.role === 'producer') {
            endpoint = `/api/admin/burners/${userToDeleteId}/`;
        } else {
            alert('Cannot delete admin users');
            userToDeleteId = null;
            confirmBtn.disabled = false;
            confirmBtn.innerHTML = '<i class="fas fa-trash-alt me-2"></i>Delete User';
            return;
        }

        const response = await fetch(endpoint, {
            method: 'DELETE',
            headers: headers,
            credentials: 'include'
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || data.detail || 'Failed to delete user');
        }

        // Close the delete confirmation modal
        const deleteModal = bootstrap.Modal.getInstance(document.getElementById('deleteUserModal'));
        deleteModal.hide();

        // Show success modal
        const successMessage = `User <strong>${user.fullName || user.username}</strong> has been permanently deleted from the system.`;
        document.getElementById('deleteSuccessMessage').innerHTML = successMessage;
        
        const successModal = new bootstrap.Modal(document.getElementById('deleteSuccessModal'));
        successModal.show();
        
        // Reload users from API after a short delay
        setTimeout(() => {
            loadUsers();
        }, 500);
        
        // Reset
        userToDeleteId = null;

        // Auto-close success modal after 3 seconds
        setTimeout(() => {
            const successModalInstance = bootstrap.Modal.getInstance(document.getElementById('deleteSuccessModal'));
            if (successModalInstance) {
                successModalInstance.hide();
            }
        }, 3000);
    } catch (error) {
        console.error('Error deleting user:', error);
        alert('Failed to delete user: ' + error.message);
        
        // Re-enable button
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = '<i class="fas fa-trash-alt me-2"></i>Delete User';
    }
}


// ===== RENDERING & FILTERING =====

function renderUsers(userList) {
    const tableBody = document.getElementById('usersTableBody');
    const totalCount = document.getElementById('totalUsersCount');
    const noUsers = document.getElementById('noUsersMessage');
    
    if (!tableBody || !totalCount || !noUsers) {
        console.error('Required DOM elements not found');
        return;
    }
    
    tableBody.innerHTML = '';
    
    if (userList.length === 0) {
        noUsers.style.display = 'block';
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">
                    <i class="fas fa-users-slash me-2"></i>
                    No users found
                </td>
            </tr>
        `;
    } else {
        noUsers.style.display = 'none';
        userList.forEach(user => {
            const row = document.createElement('tr');
            const roleColor = getRoleColor(user.role);
            
            row.innerHTML = `
                <td>${user.id}</td>
                <td>${escapeHtml(user.fullName || user.username || 'N/A')}</td>
                <td>${escapeHtml(user.email || user.username || 'N/A')}</td>
                <td><span class="badge bg-${roleColor}">${(user.role || 'burner').toUpperCase()}</span></td>
                <td><span class="badge bg-${user.status ? 'success' : 'danger'}">${user.status ? 'Active' : 'Inactive'}</span></td>
                <td>
                    <button class="btn btn-sm btn-info text-white me-2" data-bs-toggle="modal" data-bs-target="#userModal" onclick="prepareUserModal('edit', ${user.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.id})" ${user.role === 'admin' ? 'disabled' : ''}>
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    }
    
    totalCount.textContent = `Total Users: ${users.length} (${userList.length} shown)`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function filterUsers(searchTerm) {
    const term = searchTerm.toLowerCase();
    const filteredList = users.filter(user => 
        user.fullName.toLowerCase().includes(term) || 
        user.email.toLowerCase().includes(term) ||
        user.role.toLowerCase().includes(term)
    );
    renderUsers(filteredList);
}

// ===== MODAL INTERACTION =====

window.prepareUserModal = function(mode, userId = null) {
    const modalLabel = document.getElementById('userModalLabel');
    const submitBtn = document.getElementById('userModalSubmitBtn');
    const userForm = document.getElementById('userForm');
    
    userForm.reset();
    document.getElementById('userId').value = '';
    
    isEditMode = mode === 'edit';

    const emailField = document.getElementById('userEmail');

    if (isEditMode) {
        const user = users.find(u => u.id == userId);
        if (user) {
            modalLabel.textContent = `Edit User: ${user.fullName}`;
            submitBtn.textContent = 'Save Changes';
            document.getElementById('userId').value = user.id;
            document.getElementById('fullName').value = user.fullName;
            document.getElementById('userEmail').value = user.email || user.username;
            document.getElementById('userRole').value = user.role;
            document.getElementById('userStatus').checked = user.status;
            
            // Set district if available
            if (user.leader_district) {
                document.getElementById('userDistrict').value = user.leader_district;
            } else if (user.district) {
                document.getElementById('userDistrict').value = user.district;
            }
            
            // Toggle fields based on role
            toggleDistrictSectorFields();
            
            emailField.disabled = true;
            document.getElementById('userRole').disabled = true; // Cannot change role
            
            document.getElementById('userPassword').placeholder = 'Leave blank to keep current password';
        }
    } else {
        modalLabel.textContent = 'Add New User';
        submitBtn.textContent = 'Add User';
        emailField.disabled = false;
        document.getElementById('userRole').disabled = false;
        document.getElementById('userPassword').placeholder = 'Enter password for new user';
        
        // Toggle fields based on default role (burner)
        toggleDistrictSectorFields();
    }
}


// ===== UTILITIES =====

function generateId() {
    return 'user-' + Date.now().toString(36) + Math.random().toString(36).substring(2, 5);
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function getRoleColor(role) {
    switch(role) {
        case 'admin':
            return 'dark';
        case 'leader':
            return 'primary';
        case 'producer':
            return 'success';
        default:
            return 'secondary';
    }
}