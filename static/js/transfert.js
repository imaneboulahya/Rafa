document.addEventListener('DOMContentLoaded', function() {
    // Toggle sidebar
    const sidebarToggle = document.getElementById('sidebarToggle');
    const servicesSidebar = document.getElementById('servicesSidebar');
    const overlay = document.getElementById('overlay');
    
    if (sidebarToggle && servicesSidebar && overlay) {
        sidebarToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            servicesSidebar.classList.toggle('active');
            overlay.classList.toggle('active');
        });
        
        overlay.addEventListener('click', function() {
            servicesSidebar.classList.remove('active');
            overlay.classList.remove('active');
        });
        
        document.addEventListener('click', function(e) {
            if (!servicesSidebar.contains(e.target) && e.target !== sidebarToggle) {
                servicesSidebar.classList.remove('active');
                overlay.classList.remove('active');
            }
        });
    }
    
    // Form validation for payment inputs
    const paymentForms = document.querySelectorAll('.payment-form');
    paymentForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const amountPaid = parseFloat(this.querySelector('input[name="amount_paid"]').value);
            const totalAmount = parseFloat(this.querySelector('input[name="total_amount"]').value);
            
            if (amountPaid > totalAmount) {
                e.preventDefault();
                alert('Amount paid cannot be greater than total amount');
            }
        });
    });
    
    // Mobile menu toggle
    const toggleButton = document.querySelector('.toggle-button');
    const navbarLinks = document.querySelector('.navbar-links');
    
    if (toggleButton && navbarLinks) {
        toggleButton.addEventListener('click', function() {
            navbarLinks.classList.toggle('active');
            toggleButton.classList.toggle('active');
        });
    }
});