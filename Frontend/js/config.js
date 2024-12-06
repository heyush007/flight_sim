// API Configuration
const CONFIG = {
    API_BASE_URL: 'http://localhost:5000/api',
    ENDPOINTS: {
        USER: '/game/user',
        AIRPORTS: '/game/airports',
        FLIGHT: '/game/flight',
        FLIGHT_DURATION: '/game/flight-duration',
        WEATHER: '/weather',
        ACHIEVEMENTS: '/achievements',
        LEADERBOARD: '/leaderboard'
    },
    GAME: {
        DEFAULT_FUEL: 500,
        FUEL_CONSUMPTION_RATE: 10,
        MIN_LEVEL_SCORE: 70,
        MAX_RETRIES: 3
    }
};

// Game States
const GAME_STATES = {
    INIT: 'init',
    AIRPORT_SELECTION: 'airport_selection',
    FLIGHT_PLANNING: 'flight_planning',
    IN_FLIGHT: 'in_flight',
    HURDLE: 'hurdle',
    COMPLETED: 'completed',
    FAILED: 'failed'
};

// Error Messages
const ERROR_MESSAGES = {
    CONNECTION_ERROR: 'Unable to connect to the server. Please check your internet connection.',
    INVALID_INPUT: 'Please provide valid input.',
    SERVER_ERROR: 'An error occurred on the server. Please try again later.',
    AUTHENTICATION_ERROR: 'Authentication failed. Please try again.'
}; 