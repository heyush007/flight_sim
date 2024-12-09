// Function to toggle the content display on click (optional, can be removed)

document.addEventListener("DOMContentLoaded", function () {
    document.querySelector("#About_us h3").addEventListener("click", function () {
        const aboutContent = document.getElementById("about_content");
        // Toggle visibility when clicking on the "About Us" title
        if (aboutContent.style.display === "none" || aboutContent.style.display === "") {
            aboutContent.style.display = "block"; // Show content
        } else {
            aboutContent.style.display = "none"; // Hide content
        }
    });
});


document.getElementById("start-game").addEventListener("click", async () => {
    const username = document.getElementById("username").value.trim();

    if (!utils.isValidUsername(username)) {
        alert(ERROR_MESSAGES.INVALID_INPUT);
        return;
    }

    try {
        const userData = await api.createUser(username);
        if (userData.status === "success") {
            alert(userData.data.message);
            utils.hideElement("auth-section");
            utils.showElement("game-section");
            utils.updateText("username-display", username);
            utils.updateText("fuel-display", `Fuel: ${userData.data.fuel_consumed}`);
            loadAirports();
        } else {
            alert(userData.message);
        }
    } catch (error) {
        utils.handleError(error, ERROR_MESSAGES.CONNECTION_ERROR);
    }
});

async function loadAirports() {
    try {
        const airports = await api.getAirports("US", "NA"); // Example: US and North America
        const departureSelect = document.getElementById("departure-airport");
        const arrivalSelect = document.getElementById("arrival-airport");

        airports.data.forEach(airport => {
            const option = document.createElement("option");
            option.value = airport.id;
            option.textContent = airport.name;
            departureSelect.appendChild(option.cloneNode(true));
            arrivalSelect.appendChild(option);
        });

        // Initialize the map
        initMap();
        utils.showElement("airport-selection");
    } catch (error) {
        utils.handleError(error, ERROR_MESSAGES.CONNECTION_ERROR);
    }
}

function initMap() {
    const map = L.map('map').setView([37.0902, -95.7129], 4); // Centered on the US

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap'
    }).addTo(map);
}

document.getElementById("start-flight").addEventListener("click", async () => {
    const departureAirportId = document.getElementById("departure-airport").value;
    const arrivalAirportId = document.getElementById("arrival-airport").value;

    if (!departureAirportId || !arrivalAirportId) {
        alert(ERROR_MESSAGES.INVALID_INPUT);
        return;
    }

    try {
        const flightData = {
            departure_airport_id: departureAirportId,
            arrival_airport_id: arrivalAirportId,
            scheduled_departure_time: new Date().toISOString(),
            scheduled_arrival_time: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(), // 2 hours later
            level: 1 // Example level
        };

        const flightResponse = await api.scheduleFlight(flightData);
        if (flightResponse.status === "success") {
            alert(flightResponse.data.message);
            utils.showElement("game-play");
            loadHurdles(flightResponse.data.hurdles);
        } else {
            alert(flightResponse.message);
        }
    } catch (error) {
        utils.handleError(error, ERROR_MESSAGES.CONNECTION_ERROR);
    }
});

function loadHurdles(hurdles) {
    const hurdleContainer = document.getElementById("hurdle-container");
    hurdleContainer.innerHTML = ""; // Clear previous hurdles

    hurdles.forEach(hurdle => {
        const hurdleElement = document.createElement("div");
        hurdleElement.className = "hurdle";
        hurdleElement.innerHTML = `
            <div class="hurdle-description">${hurdle.description}</div>
            <div class="hurdle-options">
                <button onclick="handleHurdleOption(${hurdle.correct_option}, 1)">Option 1</button>
                <button onclick="handleHurdleOption(${hurdle.correct_option}, 2)">Option 2</button>
            </div>
        `;
        hurdleContainer.appendChild(hurdleElement);
    });
}

function handleHurdleOption(correctOption, selectedOption) {
    if (correctOption === selectedOption) {
        alert("Correct choice!");
        // Logic to increase fuel or score
    } else {
        alert("Wrong choice, try again!");
        // Logic to decrease fuel or score
    }
}

// Function to display leaderboard after game completion
async function displayLeaderboard() {
    try {
        const leaderboardData = await api.getLeaderboard(); // Assuming you have an endpoint for this
        const leaderboardList = document.getElementById("leaderboard-list");
        leaderboardList.innerHTML = ""; // Clear previous leaderboard

        leaderboardData.data.forEach(player => {
            const playerElement = document.createElement("div");
            playerElement.className = "leaderboard-player";
            playerElement.textContent = `${player.username}: ${player.score}`;

            // Highlight the user's score
            if (player.username === document.getElementById("username-display").textContent) {
                playerElement.style.fontWeight = "bold";
                playerElement.style.color = "gold"; // Highlight color
            }

            leaderboardList.appendChild(playerElement);
        });

        utils.showElement("leaderboard-section");
    } catch (error) {
        utils.handleError(error, ERROR_MESSAGES.CONNECTION_ERROR);
    }
}

// Call this function when the game ends
function endGame() {
    // Logic to determine the user's score
    // ...

    // Display the leaderboard
    displayLeaderboard();
}
