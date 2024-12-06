// Utility functions for the game

const utils = {
    // DOM Helper Functions
    showElement(elementId) {
        document.getElementById(elementId).classList.remove('hidden');
    },

    hideElement(elementId) {
        document.getElementById(elementId).classList.add('hidden');
    },

    updateText(elementId, text) {
        document.getElementById(elementId).textContent = text;
    },

    // Data Formatting
    formatTime(minutes) {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return `${hours}h ${mins}m`;
    },

    formatDistance(distance) {
        return `${Math.round(distance)} km`;
    },

    // Validation Functions
    isValidUsername(username) {
        return username && username.length >= 3 && username.length <= 20;
    },

    // Local Storage Management
    saveToStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('Error saving to localStorage:', e);
        }
    },

    getFromStorage(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (e) {
            console.error('Error reading from localStorage:', e);
            return null;
        }
    },

    // Error Handling
    handleError(error, customMessage = '') {
        console.error(error);
        alert(customMessage || ERROR_MESSAGES.SERVER_ERROR);
    },

    // Game State Management
    updateGameState(state) {
        this.saveToStorage('gameState', state);
        document.body.setAttribute('data-game-state', state);
    },

    // Animation Helpers
    animate(element, animation, duration = 500) {
        element.style.animation = `${animation} ${duration}ms ease`;
        return new Promise(resolve => {
            setTimeout(() => {
                element.style.animation = '';
                resolve();
            }, duration);
        });
    }
}; 