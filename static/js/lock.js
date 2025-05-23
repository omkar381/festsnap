document.addEventListener('DOMContentLoaded', function() {
    // Create the lock overlay if it doesn't exist already
    if (!document.getElementById('lock-overlay')) {
        createLockOverlay();
    }
    
    // Check if site is unlocked already via localStorage
    const siteUnlocked = localStorage.getItem('nirmanSiteUnlocked');
    if (siteUnlocked !== 'true') {
        showLockOverlay();
    }
});

function createLockOverlay() {
    // Create the overlay container
    const overlay = document.createElement('div');
    overlay.id = 'lock-overlay';
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100%';
    overlay.style.height = '100%';
    overlay.style.backgroundColor = 'rgba(79, 70, 229, 0.95)';
    overlay.style.display = 'none';
    overlay.style.justifyContent = 'center';
    overlay.style.alignItems = 'center';
    overlay.style.zIndex = '9999';
    overlay.style.backdropFilter = 'blur(8px)';
    
    // Create the content container
    const container = document.createElement('div');
    container.style.backgroundColor = 'white';
    container.style.padding = '2rem';
    container.style.borderRadius = '0.5rem';
    container.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
    container.style.maxWidth = '90%';
    container.style.width = '400px';
    container.style.textAlign = 'center';
    
    // Create the header
    const header = document.createElement('h2');
    header.textContent = 'NIRMAN 2K25';
    header.style.fontSize = '1.5rem';
    header.style.fontWeight = 'bold';
    header.style.marginBottom = '0.5rem';
    header.style.color = '#4F46E5';
    
    const subheader = document.createElement('p');
    subheader.textContent = 'PDA College of Engineering';
    subheader.style.color = '#6B7280';
    subheader.style.marginBottom = '1.5rem';
    
    // Create the message
    const message = document.createElement('p');
    message.textContent = 'This site is locked. Enter the PIN to access:';
    message.style.marginBottom = '1rem';
    
    // Create the input
    const inputContainer = document.createElement('div');
    inputContainer.style.marginBottom = '1.5rem';
    
    const input = document.createElement('input');
    input.type = 'password';
    input.id = 'pin-input';
    input.placeholder = 'Enter PIN';
    input.style.width = '100%';
    input.style.padding = '0.5rem 1rem';
    input.style.border = '1px solid #D1D5DB';
    input.style.borderRadius = '0.375rem';
    input.style.fontSize = '1rem';
    
    // Create the error message
    const errorMsg = document.createElement('p');
    errorMsg.id = 'pin-error';
    errorMsg.style.color = '#EF4444';
    errorMsg.style.fontSize = '0.875rem';
    errorMsg.style.marginTop = '0.5rem';
    errorMsg.style.display = 'none';
    
    // Create the button
    const button = document.createElement('button');
    button.textContent = 'Unlock';
    button.id = 'unlock-button';
    button.style.backgroundColor = '#4F46E5';
    button.style.color = 'white';
    button.style.border = 'none';
    button.style.padding = '0.5rem 1rem';
    button.style.borderRadius = '0.375rem';
    button.style.fontSize = '1rem';
    button.style.cursor = 'pointer';
    button.style.width = '100%';
    button.style.transition = 'background-color 300ms';
    
    button.addEventListener('mouseenter', function() {
        this.style.backgroundColor = '#7C3AED';
    });
    
    button.addEventListener('mouseleave', function() {
        this.style.backgroundColor = '#4F46E5';
    });
    
    // Add event listeners
    button.addEventListener('click', attemptUnlock);
    input.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            attemptUnlock();
        }
    });
    
    // Assemble the overlay
    inputContainer.appendChild(input);
    inputContainer.appendChild(errorMsg);
    
    container.appendChild(header);
    container.appendChild(subheader);
    container.appendChild(message);
    container.appendChild(inputContainer);
    container.appendChild(button);
    
    overlay.appendChild(container);
    document.body.appendChild(overlay);
}

function showLockOverlay() {
    const overlay = document.getElementById('lock-overlay');
    if (overlay) {
        overlay.style.display = 'flex';
        document.body.style.overflow = 'hidden'; // Prevent scrolling
        
        // Focus the input
        setTimeout(function() {
            const input = document.getElementById('pin-input');
            if (input) {
                input.focus();
            }
        }, 100);
    }
}

function hideLockOverlay() {
    const overlay = document.getElementById('lock-overlay');
    if (overlay) {
        overlay.style.display = 'none';
        document.body.style.overflow = ''; // Re-enable scrolling
    }
}

function attemptUnlock() {
    const input = document.getElementById('pin-input');
    const errorMsg = document.getElementById('pin-error');
    
    if (input.value === '2005') {
        // Correct PIN
        localStorage.setItem('nirmanSiteUnlocked', 'true');
        hideLockOverlay();
        
        // Reset error message
        errorMsg.style.display = 'none';
    } else {
        // Wrong PIN
        errorMsg.textContent = 'Incorrect PIN. Please try again.';
        errorMsg.style.display = 'block';
        input.value = '';
        input.focus();
        
        // Shake effect
        const container = errorMsg.closest('div').parentElement;
        container.style.animation = 'shake 0.5s';
        setTimeout(function() {
            container.style.animation = '';
        }, 500);
    }
}

// Add shake keyframes to the document
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0% { transform: translateX(0); }
        10% { transform: translateX(-10px); }
        20% { transform: translateX(10px); }
        30% { transform: translateX(-10px); }
        40% { transform: translateX(10px); }
        50% { transform: translateX(-5px); }
        60% { transform: translateX(5px); }
        70% { transform: translateX(-3px); }
        80% { transform: translateX(3px); }
        90% { transform: translateX(-1px); }
        100% { transform: translateX(0); }
    }
`;
document.head.appendChild(style); 