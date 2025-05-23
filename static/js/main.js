// Enable dismissible flash messages
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('[role="alert"]');
    
    flashMessages.forEach(message => {
        const closeButton = message.querySelector('button');
        if (closeButton) {
            closeButton.addEventListener('click', function() {
                message.style.display = 'none';
            });
            
            // Auto-dismiss success messages after 5 seconds
            if (message.classList.contains('bg-green-100')) {
                setTimeout(() => {
                    message.style.display = 'none';
                }, 5000);
            }
        }
    });
});

// Add smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop,
                behavior: 'smooth'
            });
        }
    });
}); 