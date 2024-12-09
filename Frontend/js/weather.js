async function loadWeather(city) {
    try {
        const weatherData = await api.getWeather(city);
        if (weatherData.status === "success") {
            displayWeather(weatherData.data);
        } else {
            alert(weatherData.message);
        }
    } catch (error) {
        utils.handleError(error, ERROR_MESSAGES.CONNECTION_ERROR);
    }
}

function displayWeather(weather) {
    const weatherInfo = document.getElementById("weather-info");
    weatherInfo.innerHTML = `
        <div>
            <h4>${weather.city}</h4>
            <p>Temperature: ${weather.temperature}°C</p>
            <p>Humidity: ${weather.humidity}%</p>
            <p>Description: ${weather.description}</p>
            <p>Wind Speed: ${weather.wind_speed} m/s</p>
        </div>
    `;
    utils.showElement("weather-section");
}

/*
// Example usage
document.addEventListener("DOMContentLoaded", () => {
    loadWeather("helsinki"); // Load weather for a default city
});

 */