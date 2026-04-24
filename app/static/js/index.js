
function loadWeather() {
    fetch("/api/live/weather")
        .then(response => response.json())
        .then(data => {
            console.log("Weather data:", data);

            const summary = document.querySelector(".weather-summary");
            const cardTemp = document.querySelector(".weather-card p");
            const cardDetails = document.querySelector(".weather-card small");
            
        // Show placeholder values if weather is missing
            if (!data || Object.keys(data).length === 0) {
                if (summary) summary.textContent = "Weather unavailable";
                if (cardTemp) cardTemp.textContent = "--°C";
                if (cardDetails) cardDetails.textContent = "Wind: -- km/h • Rain: --%";
                return;
            }

            if (summary) {
                summary.textContent = `${data.temperature}°C • Wind: ${data.wind_speed} km/h • Rain: ${data.rain}%`;
            }

            if (cardTemp) {
                cardTemp.textContent = `${data.temperature}°C`;
            }

            if (cardDetails) {
                cardDetails.textContent = `Wind: ${data.wind_speed} km/h • Rain: ${data.rain}%`;
            }
        })
        .catch(error => {
            console.error("Weather fetch error:", error);

            const summary = document.querySelector(".weather-summary");
            if (summary) summary.textContent = "Weather error";
        });
}

function drawPieChart(availableBikes, emptyStands) {
    const data = google.visualization.arrayToDataTable([
        ["Type", "Count"],
        ["Available Bikes", availableBikes],
        ["Empty Stands", emptyStands]
    ]);

    const options = {
        title: "Current Bike Availability",
        pieHole: 0.3,
        chartArea: {
            width: "90%",
            height: "80%"
        },
        legend: {
            position: "bottom"
        },
        height: 260,
        colors: ["#8CD47E", "#FF6961"]
    };

    const chart = new google.visualization.PieChart(
        document.getElementById("piechart_side")
    );

    chart.draw(data, options);
}

function drawChart(data, stationId) {
    const chartData = new google.visualization.DataTable();

    chartData.addColumn("datetime", "Time");
    chartData.addColumn("number", "Available Bikes");

    data.forEach((entry) => {
        chartData.addRow([
            new Date(entry.last_update),
            entry.available_bikes,
        ]);
    });

    const options = {
        title: `Bike Availability Trend: Station ${stationId}`,
        hAxis: {
            title: "Time",
            format: "HH:mm",
        },
        vAxis: {
            title: "Available Bikes",
        },
        curveType: "function",
        legend: { position: "bottom" },
        height: 300
    };

    const chart = new google.visualization.LineChart(
        document.getElementById("chart_div_side")
    );

    chart.draw(chartData, options);
}

// Main page interactions - search, routing controls
document.addEventListener("DOMContentLoaded", () => {
    loadWeather();

    const searchButton = document.getElementById("search-button");
    const stationSearch = document.getElementById("station-search");
    const clearButton = document.getElementById("clear-button");
    const startRouteButton = document.getElementById("start-route-button");
    const clearRouteButton = document.getElementById("clear-route-button");
    const useLocationButton = document.getElementById("use-location-button");

    if (useLocationButton) {
        useLocationButton.addEventListener("click", useCurrentLocation);
    }

    if (searchButton) {
        searchButton.addEventListener("click", searchStations);
    }

    if (stationSearch) {
        stationSearch.addEventListener("keypress", (event) => {
            if (event.key === "Enter") {
                searchStations();
            }
        });
    }

    if (clearButton) {
        clearButton.addEventListener("click", clearSearch);
    }

    if (startRouteButton) {
        startRouteButton.addEventListener("click", startRouteSelection);
    }

    if (clearRouteButton) {
        clearRouteButton.addEventListener("click", clearRoute);
    }
});

function closePopup() {
    const popup = document.getElementById("paymentPopup");
    if (popup) {
        popup.style.display = "none";
    }
}

// Pricing pop ups
document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll(".pricing-card button");

    buttons.forEach(button => {
        button.addEventListener("click", () => {
            const popup = document.getElementById("paymentPopup");
            if (popup) {
                popup.style.display = "flex";
            }
        });
    });

    const popup = document.getElementById("paymentPopup");
    if (popup) {
        popup.addEventListener("click", (event) => {
            if (event.target === popup) {
                closePopup();
            }
        });
    }
});



window.drawChart = drawChart;
window.drawPieChart = drawPieChart;


// Discover Dublin popup
document.addEventListener("DOMContentLoaded", () => {
    const cards = document.querySelectorAll(".discover .card");
    const popup = document.getElementById("popup");
    const popupText = document.getElementById("popupText");
    const closeButton = document.getElementById("closeButton");

    if (!cards || !popup || !popupText) return;

    cards.forEach(card => {
        card.addEventListener("click", () => {
            const content = card.querySelector(".card-content");

            if (content) {
                popupText.innerHTML = content.innerHTML;
                popup.style.display = "flex";
            }
        });
    });

    if (closeButton) {
        closeButton.addEventListener("click", () => {
            popup.style.display = "none";
        });
    }

    // close when clicking outside
    popup.addEventListener("click", (e) => {
        if (e.target === popup) {
            popup.style.display = "none";
        }
    });
});
