// Add station to favourites list if not already present
function addFavourite(station) {
    const alreadyExists = window.appState.favourites.some(
        fav => fav.number === station.number
    );

    if (alreadyExists) return;

    window.appState.favourites.push(station);
    renderFavourites();
}

function addFavouriteByNumber(stationNumber) {
    const station = window.appState.stationsData.find(
        s => s.number === stationNumber
    );

    if (!station) {
        console.log("Station not found:", stationNumber);
        return;
    }

    addFavourite(station);
}

function removeFavourite(stationNumber) {
    window.appState.favourites = window.appState.favourites.filter(
        station => station.number !== stationNumber
    );
    renderFavourites();
}

function renderFavourites() {
    const favouritesList = document.getElementById("favourites-list");
    if (!favouritesList) return;

    favouritesList.innerHTML = "";

    if (window.appState.favourites.length === 0) {
        updateFavouritesVisibility();
        return;
    }

    window.appState.favourites.forEach(station => {
        const li = document.createElement("li");
        li.innerHTML = `
            <div class="favourite-item-main">
                <strong>${station.name}</strong><br>
                Bikes available: ${station.available_bikes}<br>
                Stands available: ${station.available_bike_stands}
            </div>
            <button type="button" onclick="removeFavourite(${station.number})">Remove</button>
        `;
        
        li.querySelector(".favourite-item-main").addEventListener("click", () => {
            const marker = window.appState.markersByNumber[station.number];
            if (!marker) return;

            window.appState.map.panTo(marker.getPosition());
            window.appState.map.setZoom(15);
            google.maps.event.trigger(marker, "click");
        });

        favouritesList.appendChild(li);
    });

    updateFavouritesVisibility();
}

// Show favourites panel if it has items, hide otherwise
function updateFavouritesVisibility() {
    const panel = document.getElementById("favourites-panel");
    const list = document.getElementById("favourites-list");

    if (!panel || !list) return;

    const hasFavourites = list.children.length > 0;
    panel.classList.toggle("hidden-panel", !hasFavourites);
}

window.addFavouriteByNumber = addFavouriteByNumber;
window.removeFavourite = removeFavourite;