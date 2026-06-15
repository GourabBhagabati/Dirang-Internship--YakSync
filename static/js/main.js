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

console.log('YakSync IoT Platform Loaded Successfully');
