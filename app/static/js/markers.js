function addMarkers(stations) {
    const createdMarkers = [];

    for (const station of stations) {
        let icon;
        
        // Choose marker colour based on current bike availability
        if (station.available_bikes === 0) {
            icon = "/static/images/red_wheel.png";
        } else if (station.available_bikes < 5) {
            icon = "/static/images/orange_wheel.png";
        } else {
            icon = "/static/images/green_wheel.png";
        }

        const marker = new google.maps.Marker({
            position: {
                lat: station.position.lat,
                lng: station.position.lng,
            },
            map: window.appState.map,
            title: station.name,
            station_number: station.number,
            icon: icon
        });

        window.appState.markers.push(marker);
        createdMarkers.push(marker);
        window.appState.markersByNumber[station.number] = marker;

        marker.addListener("click", () => {

            if (window.setPredictionStation) {
                window.setPredictionStation(station);
            }
            window.selectedStationId = station.number;

            const selectedStationDiv = document.getElementById("selected-station");
            if (selectedStationDiv) {
                selectedStationDiv.textContent = `Selected: ${station.name} (ID: ${station.number})`;
            }
            // Escape apostrophes before injecting the station
            const safeName = station.name.replace(/'/g, "\\'");

            // Only show fabourites button for logged in users
            const favouriteButton = window.IS_AUTHENTICATED
                ? `<button class="station-popup-button" onclick="addFavouriteByNumber(${station.number})">Add to favourites</button>`
            : "";

            const content = `
                <div class="station-popup">
                    <h3>${station.name}</h3>
                    <div class="station-popup-details">
                    <p><strong>Station Number:</strong> ${station.number ?? "N/A"}</p>
                    <p><strong>Address:</strong> ${station.address ?? "N/A"}</p>
                    <p><strong>Available Bike Stands:</strong> ${station.available_bike_stands ?? "N/A"}</p>
                    <p><strong>Available Bikes:</strong> ${station.available_bikes ?? "N/A"}</p>
                    </div>
                    <button class="station-popup-button" onclick="showGraph(${station.number}, '${safeName}', ${station.available_bikes}, ${station.available_bike_stands})">
                        More info
                    </button>

                    ${favouriteButton}
                </div>
            `;

            window.appState.infoWindow.setContent(content);
            window.appState.infoWindow.open(window.appState.map, marker);
        });
    }

    return createdMarkers;
}

function showGraph(stationNumber, stationName, availableBikes, emptyStands) {
    const sidebar = document.getElementById("sidebar");
    const sidebarContent = document.getElementById("sidebar-content");

    sidebarContent.innerHTML = `
        <div class="graph-panel">
        <h2>${stationName}</h2>
        <p>Station Number: ${stationNumber}</p>
        <div class="chart-card">
        <div id="piechart_side"></div>
        </div>
        <div class="chart-card">
        <div id="chart_div_side"></div>
        </div>
        </div>
    `;

    sidebar.classList.remove("hidden");

    //Load historiccal data then render the charts
    fetch(`/api/stations/${stationNumber}`)
        .then((response) => response.json())
        .then((data) => {
            google.charts.load("current", { packages: ["corechart"] });
            google.charts.setOnLoadCallback(() => {
                drawChart(data.available, stationNumber);
                drawPieChart(availableBikes, emptyStands);
            });
        })
        .catch((error) => {
            console.error(`Error fetching data for station ${stationNumber}:`, error);
            sidebarContent.innerHTML += `<p>Error loading chart data.</p>`;
        });
}

function closeSidebar() {
    document.getElementById("sidebar").classList.add("hidden");
}

window.showGraph = showGraph;
window.closeSidebar = closeSidebar;