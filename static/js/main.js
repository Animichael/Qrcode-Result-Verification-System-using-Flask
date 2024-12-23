// Initialize modules
const App = {
    init: function() {
        this.initScrollAnimation();
        this.initFormValidation();
        this.initModalEffects();
        this.initSmoothScroll();
    },


    // Scroll animations
    initScrollAnimation: function() {
        const animateOnScroll = () => {
            document.querySelectorAll('.feature-card').forEach(card => {
                if (this.isElementInViewport(card)) {
                    card.classList.add('fade-in');
                }
            });
        };

        window.addEventListener('scroll', animateOnScroll);
        animateOnScroll(); // Initial check
    },

    
    // Form validation
    initFormValidation: function() {
        // Result verification form
        const verificationForm = document.querySelector('.verification-form');
        if (verificationForm) {
            verificationForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const rollNumber = verificationForm.querySelector('input').value.trim();
                
                if (!rollNumber) {
                    this.showAlert('Please enter a valid roll number', 'error');
                    return;
                }
                
                // Add your verification logic here
                this.showAlert('Verifying roll number...', 'info');
            });
        }

        // Admin login form
        const adminLoginForm = document.getElementById('adminLoginForm');
        if (adminLoginForm) {
            adminLoginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const email = adminLoginForm.querySelector('input[type="email"]').value;
                const accessId = adminLoginForm.querySelector('input[type="password"]').value;
                
                // Add your login logic here
                this.showAlert('Processing login...', 'info');
            });
        }
    },

    // Modal effects
    initModalEffects: function() {
        const adminModal = document.getElementById('adminLoginModal');
        if (adminModal) {
            adminModal.addEventListener('show.bs.modal', function() {
                this.querySelector('.modal-content').classList.add('fade-in');
            });
        }
    },

    // Smooth scroll
    initSmoothScroll: function() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    },

    // Utility functions
    isElementInViewport: function(el) {
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    },

    showAlert: function(message, type = 'info') {
        // alert message
        alert(message);
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});



///////////////////////////////////////////////////////////////////////////////////////////
/* for admin login */
$(document).ready(function() {
    let inactivityTimer;

    function resetInactivityTimer() {
        clearTimeout(inactivityTimer);
        inactivityTimer = setTimeout(function() {
            window.location.href = '/logout';
        }, 3 * 60 * 1000); // 3 minutes
    }

    // Reset timer on user activity
    $(document).on('mousemove keypress', resetInactivityTimer);

    function showAlert(message, type) {
        const alert = $(`
            <div class="alert alert-${type} alert-float alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `);
        $('body').append(alert);
        setTimeout(() => alert.remove(), 5000);
    }

    $('#adminLoginForm').on('submit', function(e) {
        e.preventDefault();
        
        $('.spinner-overlay').css('display', 'flex');
        
        $.ajax({
            url: '/admin/login',
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                if (response.success) {
                    showAlert(response.message, 'success');
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1000);
                } else {
                    showAlert(response.message, 'danger');
                }
            },
            error: function() {
                showAlert('An error occurred. Please try again.', 'danger');
            },
            complete: function() {
                $('.spinner-overlay').hide();
            }
        });
    });
});



////////////////////////////////////////////////////////////////////////////
/* side bar js for smaller screen devices */
$(document).ready(function() {
    // Toggle sidebar
    $('.menu-toggle').click(function() {
        $('.sidebar').toggleClass('active');
        $('.sidebar-overlay').toggleClass('active');
    });

    // Close sidebar when clicking overlay
    $('.sidebar-overlay').click(function() {
        $('.sidebar').removeClass('active');
        $('.sidebar-overlay').removeClass('active');
    });

    // Close sidebar when clicking a menu item on mobile
    $('.sidebar .nav-link').click(function() {
        if (window.innerWidth <= 991) {
            $('.sidebar').removeClass('active');
            $('.sidebar-overlay').removeClass('active');
        }
    });

    // Handle window resize
    $(window).resize(function() {
        if (window.innerWidth > 991) {
            $('.sidebar').removeClass('active');
            $('.sidebar-overlay').removeClass('active');
        }
    });
});
