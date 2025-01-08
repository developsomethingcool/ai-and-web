// Add floating particles
function createParticles() {
    const container = document.getElementById('particles');
    for (let i = 0; i < 50; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.width = Math.random() * 6 + 'px';
        particle.style.height = particle.style.width;
        particle.style.left = Math.random() * 100 + 'vw';
        particle.style.animationDuration = Math.random() * 10 + 5 + 's';
        particle.style.animationDelay = Math.random() * 5 + 's';
        container.appendChild(particle);
    }
}

// Cursor glow effect
document.addEventListener('mousemove', (e) => {
    const cursor = document.querySelector('.cursor-glow');
    cursor.style.left = e.clientX + 'px';
    cursor.style.top = e.clientY + 'px';
});

// Function to generate a random transparent color
function getRandomTransparentColor() {
    const r = Math.floor(Math.random() * 256); // Random Red value (0-255)
    const g = Math.floor(Math.random() * 256); // Random Green value (0-255)
    const b = Math.floor(Math.random() * 256); // Random Blue value (0-255)
    const a = 0.5; // Fixed transparency (adjust between 0.1 to 1)
    return `rgba(${r}, ${g}, ${b}, ${a})`;
}

// Apply random transparent colors to result cards
function applyRandomColors() {
    const resultCards = document.querySelectorAll('.result-card');
    resultCards.forEach((card) => {
        const randomColor = getRandomTransparentColor();
        card.style.backgroundColor = randomColor;
        card.style.color = getContrastColor(randomColor); // Adjust text color for contrast
    });
}

// Function to determine text color based on background brightness
function getContrastColor(rgbaColor) {
    // Extract RGB values from rgba string
    const rgba = rgbaColor.match(/rgba?\((\d+), (\d+), (\d+)/);
    const r = parseInt(rgba[1]);
    const g = parseInt(rgba[2]);
    const b = parseInt(rgba[3]);

    // Calculate brightness (YIQ formula)
    const brightness = (r * 299 + g * 587 + b * 114) / 1000;
    return brightness > 128 ? '#000000' : '#FFFFFF'; // Return black or white
}

// Run the function on page load
document.addEventListener('DOMContentLoaded', applyRandomColors);



// Initialize
createParticles();
