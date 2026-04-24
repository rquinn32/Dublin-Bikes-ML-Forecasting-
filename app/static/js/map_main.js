// Global app state across map, routing, UI
window.appState = {
    markers: [],
    markersByNumber: {},
    favourites: [],
    stationsData: [],
    bikePolyline: null,

    directionsService: null,
    directionsRenderer: null,

    routingMode: false,
    selectedRoutePoints: [],
    routeClickMarkers: [],

    map: null,
    infoWindow: null,

    walkingRenderer1: null,
    bikingRenderer: null,
    walkingRenderer2: null,
    bikeRouteStationMarkers: []
};

//Remove all markers from the map and reset marker state
function clearMarkers() {
    for (const marker of window.appState.markers) {
        marker.setMap(null);
    }
    window.appState.markers = [];
    window.appState.markersByNumber = {};
}

//Fetch live bike station data and render markers on the app
function getStations() {
    fetch("/api/live/bikes")
        .then((response) => response.json())
        .then((data) => {
            console.log("fetch response", typeof data);
            window.appState.stationsData = data;
            addMarkers(data);
        })
        .catch((error) => {
            console.error("Error fetching stations data:", error);
        });
}

//Initialise Googe Map 
function initMap() {
    const dublin = { lat: 53.35014, lng: -6.266155 };

    window.appState.map = new google.maps.Map(document.getElementById("map"), {
        zoom: 14,
        center: dublin,
    });

    window.appState.infoWindow = new google.maps.InfoWindow();
    window.appState.directionsService = new google.maps.DirectionsService();

    window.appState.walkingRenderer1 = new google.maps.DirectionsRenderer({
        map: window.appState.map,
        suppressMarkers: true,
        polylineOptions: {
            strokeColor: "#43A047",
            strokeWeight: 5
        }
    });

    window.appState.walkingRenderer2 = new google.maps.DirectionsRenderer({
        map: window.appState.map,
        suppressMarkers: true,
        polylineOptions: {
            strokeColor: "#43A047",
            strokeWeight: 5
        }
    });

    window.appState.map.addListener("click", (event) => {
        window.appState.infoWindow.close();

        if (window.appState.routingMode) {
            handleRouteMapClick(event.latLng);
        }
    });

    getStations();

    // Force map resize after load 
    setTimeout(() => {
        google.maps.event.trigger(window.appState.map, "resize");
        window.appState.map.setCenter(dublin);
    }, 300);
}

window.initMap = initMap;