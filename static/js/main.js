// YakSync Main JavaScript

// Auto-dismiss messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.messages .alert');
    
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
            message.style.transform = 'translateX(400px)';
            setTimeout(function() {
                message.remove();
            }, 300);
        }, 5000);
    });
});

// Mobile sidebar toggle
document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebarMenu');
    const toggleBtn = document.getElementById('sidebarToggle');
    const overlay = document.getElementById('sidebarOverlay');
    
    if (sidebar && toggleBtn && overlay) {
        function toggleSidebar() {
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
        }

        function closeSidebar() {
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        }

        toggleBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleSidebar();
        });
        
        overlay.addEventListener('click', closeSidebar);
        
        // Close sidebar on window resize to desktop size
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                closeSidebar();
            }
        });
    }
});

// Form validation helper
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const inputs = form.querySelectorAll('input[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('error');
            isValid = false;
        } else {
            input.classList.remove('error');
        }
    });
    
    return isValid;
}

// Smooth scroll for anchor links
document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

// Profile & Notifications Dropdown Toggle
document.addEventListener('DOMContentLoaded', function() {
    const trigger = document.getElementById('userProfileTrigger');
    const dropdown = document.getElementById('profileDropdown');
    const notifTrigger = document.getElementById('notificationsTrigger');
    const notifDropdown = document.getElementById('notificationsDropdown');
    
    if (trigger && dropdown) {
        trigger.addEventListener('click', function(e) {
            e.stopPropagation();
            trigger.classList.toggle('active');
            dropdown.classList.toggle('active');
            
            // Close notification dropdown if open
            if (notifTrigger && notifDropdown) {
                notifTrigger.classList.remove('active');
                notifDropdown.classList.remove('active');
            }
        });
        
        document.addEventListener('click', function(e) {
            if (!dropdown.contains(e.target) && !trigger.contains(e.target)) {
                trigger.classList.remove('active');
                dropdown.classList.remove('active');
            }
        });
    }

    // Notifications Dropdown Toggle
    if (notifTrigger && notifDropdown) {
        notifTrigger.addEventListener('click', function(e) {
            e.stopPropagation();
            notifTrigger.classList.toggle('active');
            notifDropdown.classList.toggle('active');
            
            // Close profile dropdown if open
            if (trigger && dropdown) {
                trigger.classList.remove('active');
                dropdown.classList.remove('active');
            }
        });
        
        document.addEventListener('click', function(e) {
            if (!notifDropdown.contains(e.target) && !notifTrigger.contains(e.target)) {
                notifTrigger.classList.remove('active');
                notifDropdown.classList.remove('active');
            }
        });
    }
});

// Dynamic updates polling
document.addEventListener('DOMContentLoaded', function() {
    const POLL_INTERVAL = 10000; // 10 seconds

    function fetchUpdates() {
        fetch('/dashboard/api/updates/')
            .then(response => {
                if (!response.ok) throw new Error('Network response not ok');
                return response.json();
            })
            .then(data => {
                updateNavbarAlerts(data);
                updateDashboardStats(data);
                updateDashboardLists(data);
            })
            .catch(error => {
                console.error('Error fetching dashboard updates:', error);
            });
    }

    function updateNavbarAlerts(data) {
        // Update badge count
        const container = document.getElementById('navNotificationBadgeContainer');
        if (container) {
            if (data.unread_critical_count > 0) {
                container.innerHTML = `
                    <span class="notification-badge" style="position: absolute; top: 2px; right: 2px; background: var(--danger-color); color: white; font-size: 0.65rem; font-weight: 700; min-width: 16px; height: 16px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2px solid var(--card-bg); padding: 2px;">
                        ${data.unread_critical_count}
                    </span>
                `;
            } else {
                container.innerHTML = '';
            }
        }

        // Update dropdown body
        const dropdownBody = document.getElementById('navNotificationsBody');
        if (dropdownBody && data.html && data.html.navbar_alerts) {
            dropdownBody.innerHTML = data.html.navbar_alerts;
        }
    }

    function updateDashboardStats(data) {
        if (!data.stats) return;

        const elTotalAnimals = document.getElementById('stat-total-animals');
        const elTotalDevices = document.getElementById('stat-total-devices');
        const elActiveDevices = document.getElementById('stat-active-devices');
        const elInactiveDevices = document.getElementById('stat-inactive-devices');
        const elMaintenanceDevices = document.getElementById('stat-maintenance-devices');
        const elActiveProtocols = document.getElementById('stat-active-protocols');
        const elActiveAlerts = document.getElementById('stat-active-alerts');

        if (elTotalAnimals) elTotalAnimals.textContent = data.stats.total_animals;
        if (elTotalDevices) elTotalDevices.textContent = data.stats.total_devices;
        if (elActiveDevices) elActiveDevices.textContent = data.stats.active_devices;
        if (elInactiveDevices) elInactiveDevices.textContent = data.stats.inactive_devices;
        if (elMaintenanceDevices) elMaintenanceDevices.textContent = data.stats.maintenance_devices;
        if (elActiveProtocols) elActiveProtocols.textContent = data.stats.active_protocols;
        if (elActiveAlerts) elActiveAlerts.textContent = data.stats.active_alerts;
    }

    function updateDashboardLists(data) {
        if (!data.html) return;

        const elRecentAlerts = document.getElementById('dashboardRecentAlerts');
        const elRecentActivities = document.getElementById('dashboardRecentActivities');
        const elHormonesList = document.getElementById('dashboardHormonesList');

        if (elRecentAlerts && data.html.dashboard_alerts) {
            elRecentAlerts.innerHTML = data.html.dashboard_alerts;
        }
        if (elRecentActivities && data.html.dashboard_activities) {
            elRecentActivities.innerHTML = data.html.dashboard_activities;
        }
        if (elHormonesList && data.html.dashboard_hormones) {
            elHormonesList.innerHTML = data.html.dashboard_hormones;
        }
    }

    // Start polling if user is authenticated (notificationsTrigger exists)
    if (document.getElementById('notificationsTrigger')) {
        // Repeated polling (10s)
        setInterval(fetchUpdates, POLL_INTERVAL);
    }
});

console.log('YakSync IoT Platform Loaded Successfully');
