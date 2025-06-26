document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const toggleButton = document.querySelector('.toggle-button');
    const navbarLinks = document.querySelector('.navbar-links');

    if (toggleButton && navbarLinks) {
        toggleButton.addEventListener('click', () => {
            navbarLinks.classList.toggle('active');
            toggleButton.classList.toggle('active');
        });
    }

    // Sidebar toggle functionality
    const sidebarToggle = document.getElementById('sidebarToggle');
    const servicesSidebar = document.getElementById('servicesSidebar');
    const overlay = document.getElementById('overlay');

    if (sidebarToggle && servicesSidebar && overlay) {
        sidebarToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            servicesSidebar.classList.toggle('active');
            overlay.classList.toggle('active');
        });

        overlay.addEventListener('click', () => {
            servicesSidebar.classList.remove('active');
            overlay.classList.remove('active');
        });
        
        document.addEventListener('click', (e) => {
            if (!servicesSidebar.contains(e.target) && e.target !== sidebarToggle) {
                servicesSidebar.classList.remove('active');
                overlay.classList.remove('active');
            }
        });
    }

    // Edit button functionality
    const editButtons = document.querySelectorAll('.edit-btn');
    editButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const clientId = this.getAttribute('data-id');
            // Implement your edit functionality here
            console.log('Editing client with ID:', clientId);
            // You might want to redirect to an edit page or show a modal
            // window.location.href = `/edit_client/${clientId}`;
        });
    });
});