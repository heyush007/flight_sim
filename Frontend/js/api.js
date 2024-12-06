class API {
    constructor(baseURL = CONFIG.API_BASE_URL) {
        this.baseURL = baseURL;
    }

    async makeRequest(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // User Related API Calls
    async createUser(username) {
        return this.makeRequest(CONFIG.ENDPOINTS.USER, {
            method: 'POST',
            body: JSON.stringify({ username })
        });
    }

    async getAirports(country, continent) {
        return this.makeRequest(`${CONFIG.ENDPOINTS.AIRPORTS}?country=${country}&continent=${continent}`);
    }

    async calculateFlightDuration(departureCoords, arrivalCoords) {
        return this.makeRequest(CONFIG.ENDPOINTS.FLIGHT_DURATION, {
            method: 'POST',
            body: JSON.stringify({
                departure_lat: departureCoords.lat,
                departure_lon: departureCoords.lon,
                arrival_lat: arrivalCoords.lat,
                arrival_lon: arrivalCoords.lon
            })
        });
    }

    async scheduleFlight(flightData) {
        return this.makeRequest(CONFIG.ENDPOINTS.FLIGHT, {
            method: 'POST',
            body: JSON.stringify(flightData)
        });
    }

    async getWeather(city) {
        return this.makeRequest(`${CONFIG.ENDPOINTS.WEATHER}/${city}`);
    }

    async getAchievements(userId) {
        return this.makeRequest(`${CONFIG.ENDPOINTS.ACHIEVEMENTS}/${userId}`);
    }

    async getLeaderboard() {
        return this.makeRequest(CONFIG.ENDPOINTS.LEADERBOARD);
    }
}

// Create a single instance to be used throughout the application
const api = new API(); 