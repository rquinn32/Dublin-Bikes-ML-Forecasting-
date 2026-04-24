function findNearestStation(pointLatLng, stationFilterFn) {
    if (!window.appState.stationsData || window.appState.stationsData.length === 0) {
        return null;
    }

    let nearestStation = null;
    let nearestDistance = Infinity;

    window.appState.stationsData.forEach((station) => {
        if (!stationFilterFn(station)) {
            return;
        }

        const stationLatLng = new google.maps.LatLng(
            station.position.lat,
            station.position.lng
        );

        const distance = google.maps.geometry.spherical.computeDistanceBetween(
            pointLatLng,
            stationLatLng
        );

        if (distance < nearestDistance) {
            nearestDistance = distance;
            nearestStation = station;
        }
    });

    return nearestStation;
}

function findNearestStartStation(originLatLng) {
    return findNearestStation(originLatLng, (station) => station.available_bikes > 0);
}

function findNearestEndStation(destinationLatLng) {
    return findNearestStation(destinationLatLng, (station) => station.available_bike_stands > 0);
}

function hideAllStationMarkers() {
    window.appState.markers.forEach(marker => marker.setMap(null));
}

function showOnlySelectedStationMarkers(startStation, endStation) {
    hideAllStationMarkers();

    const startMarker = window.appState.markersByNumber[startStation.number];
    const endMarker = window.appState.markersByNumber[endStation.number];

    if (startMarker) {
        startMarker.setMap(window.appState.map);
    }

    if (endMarker) {
        endMarker.setMap(window.appState.map);
    }
}


function clearRenderedRoutes() {
    if (window.appState.walkingRenderer1) window.appState.walkingRenderer1.setMap(null);
    if (window.appState.walkingRenderer2) window.appState.walkingRenderer2.setMap(null);

    if (window.appState.bikePolyline) {
        window.appState.bikePolyline.setMap(null);
        window.appState.bikePolyline = null;
    }

    window.appState.walkingRenderer1 = new google.maps.DirectionsRenderer({
        map: window.appState.map,
        suppressMarkers: true,
        polylineOptions: {
            strokeColor: "#43A047",
            strokeWeight: 5,
            strokeOpacity: 1
        }
    });

    window.appState.walkingRenderer2 = new google.maps.DirectionsRenderer({
        map: window.appState.map,
        suppressMarkers: true,
        polylineOptions: {
            strokeColor: "#43A047",
            strokeWeight: 5,
            strokeOpacity: 1
        }
    });
}

function drawBikePolyline(directionResult) {
    if (window.appState.bikePolyline) {
        window.appState.bikePolyline.setMap(null);
    }

    const route = directionResult.routes[0];
    const path = route.overview_path;

    window.appState.bikePolyline = new google.maps.Polyline({
        path: path,
        geodesic: true,
        strokeColor: "#1E88E5",
        strokeOpacity: 1.0,
        strokeWeight: 5,
        map: window.appState.map
    });
}

function requestRoute(request) {
    return new Promise((resolve, reject) => {
        window.appState.directionsService.route(request, (result, status) => {
            if (status === "OK") {
                resolve(result);
            } else {
                reject(status);
            }
        });
    });
}

function startRouteSelection() {
    window.appState.routingMode = true;
    window.appState.selectedRoutePoints = [];
    clearRouteMarkers();
    clearBikeRouteStationMarkers();
    clearRenderedRoutes();
    hideStationMarkers();

    const routeStatus = document.getElementById("route-status");
    const routeInfo = document.getElementById("route-info");

    if (routeStatus) {
        routeStatus.textContent = "Click your starting point, then click your destination. We’ll route you via Dublin Bikes stations.";
    }

    if (routeInfo) {
        routeInfo.innerHTML = "";
    }

    window.appState.infoWindow.close();
    closeSidebar();
}

function clearRoute() {
    window.appState.routingMode = false;
    window.appState.selectedRoutePoints = [];
    clearRouteMarkers();
    clearBikeRouteStationMarkers();
    clearRenderedRoutes();
    showAllStationMarkers();

    const routeStatus = document.getElementById("route-status");
    const routeInfo = document.getElementById("route-info");

    if (routeStatus) {
        routeStatus.textContent = 'Click "Start Route", then click your start and destination.';
    }

    if (routeInfo) {
        routeInfo.innerHTML = "";
    }
}

function sumDistanceText(legs) {
    const totalMeters = legs.reduce((sum, leg) => sum + (leg.distance?.value || 0), 0);

    if (totalMeters < 1000) {
        return `${totalMeters} m`;
    }

    return `${(totalMeters / 1000).toFixed(1)} km`;
}

function sumDurationText(legs) {
    const totalSeconds = legs.reduce((sum, leg) => sum + (leg.duration?.value || 0), 0);

    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.round((totalSeconds % 3600) / 60);

    if (hours > 0) {
        return `${hours} hr ${minutes} min`;
    }

    return `${minutes} min`;
}

function clearRouteMarkers() {
    window.appState.routeClickMarkers.forEach(marker => marker.setMap(null));
    window.appState.routeClickMarkers = [];
}

function hideStationMarkers() {
    window.appState.markers.forEach(marker => marker.setMap(null));
}

function showAllStationMarkers() {
    window.appState.markers.forEach(marker => marker.setMap(window.appState.map));
}

function handleRouteMapClick(latLng) {
    if (window.appState.selectedRoutePoints.length >= 2) {
        clearRoute();
        window.appState.routingMode = true;
    }

    window.appState.selectedRoutePoints.push(latLng);

    const marker = new google.maps.Marker({
        position: latLng,
        map: window.appState.map,
        label: window.appState.selectedRoutePoints.length === 1 ? "A" : "B"
    });

    window.appState.routeClickMarkers.push(marker);

    const routeStatus = document.getElementById("route-status");

    if (window.appState.selectedRoutePoints.length === 1) {
        if (routeStatus) {
            routeStatus.textContent = "Now click the destination.";
        }
        return;
    }

    if (window.appState.selectedRoutePoints.length === 2) {
        if (routeStatus) {
            routeStatus.textContent = "Calculating route...";
        }
        calculateRoute();
    }
}

function clearBikeRouteStationMarkers() {
    window.appState.bikeRouteStationMarkers.forEach(marker => marker.setMap(null));
    window.appState.bikeRouteStationMarkers = [];
}

function getNearestStations(pointLatLng, stationFilterFn, limit = 1) {
    if (!window.appState.stationsData || window.appState.stationsData.length === 0) {
        return [];
    }

    return window.appState.stationsData
        .filter(stationFilterFn)
        .map((station) => {
            const stationLatLng = new google.maps.LatLng(
                station.position.lat,
                station.position.lng
            );

            const distance = google.maps.geometry.spherical.computeDistanceBetween(
                pointLatLng,
                stationLatLng
            );

            return { station, distance };
        })
        .sort((a, b) => a.distance - b.distance)
        .slice(0, limit)
        .map(item => item.station);
}

function getCandidateStartStations(originLatLng) {
    return getNearestStations(
        originLatLng,
        (station) => station.available_bikes > 0,
        2
    );
}

function getCandidateEndStations(destinationLatLng) {
    return getNearestStations(
        destinationLatLng,
        (station) => station.available_bike_stands > 0,
        2
    );
}

function getLegDurationSeconds(result) {
    return result.routes[0].legs[0].duration.value;
}

function getLegDistanceMeters(result) {
    return result.routes[0].legs[0].distance.value;
}

async function evaluateStationPair(origin, destination, startStation, endStation) {
    const startStationLatLng = {
        lat: startStation.position.lat,
        lng: startStation.position.lng
    };

    const endStationLatLng = {
        lat: endStation.position.lat,
        lng: endStation.position.lng
    };

    const walkToBike = await requestRoute({
        origin: origin,
        destination: startStationLatLng,
        travelMode: google.maps.TravelMode.WALKING
    });

    const bikeLeg = await requestRoute({
        origin: startStationLatLng,
        destination: endStationLatLng,
        travelMode: google.maps.TravelMode.BICYCLING
    });

    const walkToDestination = await requestRoute({
        origin: endStationLatLng,
        destination: destination,
        travelMode: google.maps.TravelMode.WALKING
    });

    const totalDuration =
        getLegDurationSeconds(walkToBike) +
        getLegDurationSeconds(bikeLeg) +
        getLegDurationSeconds(walkToDestination);

    const totalDistance =
        getLegDistanceMeters(walkToBike) +
        getLegDistanceMeters(bikeLeg) +
        getLegDistanceMeters(walkToDestination);

    return {
        startStation,
        endStation,
        walkToBike,
        bikeLeg,
        walkToDestination,
        totalDuration,
        totalDistance
    };
}

async function findBestStationPair(origin, destination) {
    const candidateStartStations = getCandidateStartStations(origin);
    const candidateEndStations = getCandidateEndStations(destination);

    if (candidateStartStations.length === 0 || candidateEndStations.length === 0) {
        return null;
    }

    let bestOption = null;

    for (const startStation of candidateStartStations) {
        for (const endStation of candidateEndStations) {
            if (startStation.number === endStation.number) {
                continue;
            }

            try {
                const option = await evaluateStationPair(
                    origin,
                    destination,
                    startStation,
                    endStation
                );

                if (!bestOption || option.totalDuration < bestOption.totalDuration) {
                    bestOption = option;
                }
            } catch (errorStatus) {
                console.warn(`Skipping pair ${startStation.name} -> ${endStation.name}:`, errorStatus);
            }
        }
    }

    return bestOption;
}

async function calculateRoute() {
    if (window.appState.selectedRoutePoints.length < 2) {
        return;
    }

    const origin = window.appState.selectedRoutePoints[0];
    const destination = window.appState.selectedRoutePoints[1];

    const routeStatus = document.getElementById("route-status");
    const routeInfo = document.getElementById("route-info");

    try {
        if (routeStatus) {
            routeStatus.textContent = "Finding the best bike stations for your trip...";
        }

        const bestOption = await findBestStationPair(origin, destination);

        if (!bestOption) {
            if (routeStatus) {
                routeStatus.textContent = "Could not find suitable bike stations for this route.";
            }
            if (routeInfo) {
                routeInfo.innerHTML = "";
            }
            return;
        }

        window.appState.walkingRenderer1.setDirections(bestOption.walkToBike);
        drawBikePolyline(bestOption.bikeLeg);
        window.appState.walkingRenderer2.setDirections(bestOption.walkToDestination);

        showOnlySelectedStationMarkers(bestOption.startStation, bestOption.endStation);

        window.appState.routingMode = false;

        const walkLeg1 = bestOption.walkToBike.routes[0].legs[0];
        const cycleLeg = bestOption.bikeLeg.routes[0].legs[0];
        const walkLeg2 = bestOption.walkToDestination.routes[0].legs[0];

        if (routeStatus) {
            routeStatus.textContent = "Best route ready.";
        }

        if (routeInfo) {
            routeInfo.innerHTML = `
                <p><strong>Pick up bike at:</strong> ${bestOption.startStation.name}</p>
                <p><strong>Drop off bike at:</strong> ${bestOption.endStation.name}</p>

                <p><strong>Walk to station:</strong> ${walkLeg1.distance.text} • ${walkLeg1.duration.text}</p>
                <p><strong>Cycle segment:</strong> ${cycleLeg.distance.text} • ${cycleLeg.duration.text}</p>
                <p><strong>Walk to destination:</strong> ${walkLeg2.distance.text} • ${walkLeg2.duration.text}</p>

                <hr>

                <p><strong>Total distance:</strong> ${sumDistanceText([walkLeg1, cycleLeg, walkLeg2])}</p>
                <p><strong>Total duration:</strong> ${sumDurationText([walkLeg1, cycleLeg, walkLeg2])}</p>
            `;
        }

    } catch (error) {
        console.error("Smart routing failed:", error);

        if (routeStatus) {
            routeStatus.textContent = "Could not calculate full route.";
        }

        if (routeInfo) {
            routeInfo.innerHTML = `<p>Error: ${error}</p>`;
        }
    }
}

function useCurrentLocation() {
    if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser.");
        return;
    }

    const routeStatus = document.getElementById("route-status");

    if (routeStatus) {
        routeStatus.textContent = "Getting your location...";
    }

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const userLatLng = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };

            window.appState.map.panTo(userLatLng);
            window.appState.map.setZoom(15);

            window.appState.routingMode = true;
            window.appState.selectedRoutePoints = [userLatLng];

            clearRouteMarkers();
            clearBikeRouteStationMarkers();
            clearRenderedRoutes();
            hideStationMarkers();

            const marker = new google.maps.Marker({
                position: userLatLng,
                map: window.appState.map,
                label: "A",
                title: "Your location"
            });

            window.appState.routeClickMarkers.push(marker);

            if (routeStatus) {
                routeStatus.textContent = "Now click your destination.";
            }
        },
        (error) => {
            console.error("Geolocation error:", error);
            alert("Unable to retrieve your location.");
        }
    );
}

function searchStations() {
    const query = document.getElementById("station-search").value.trim();

    if (!query) {
        return;
    }

    fetch(`/api/search?q=${encodeURIComponent(query)}`)
        .then((response) => response.json())
        .then((data) => {
            console.log("Search results:", data);

            clearMarkers();
            const newMarkers = addMarkers(data);

            if (data.length > 0) {
                window.appState.map.setCenter({
                    lat: data[0].position.lat,
                    lng: data[0].position.lng
                });
                window.appState.map.setZoom(15);
                google.maps.event.trigger(newMarkers[0], "click");
            } else {
                alert("No matching stations found.");
            }
        })
        .catch((error) => {
            console.error("Error searching stations:", error);
        });
}

function clearSearch() {
    document.getElementById("station-search").value = "";

    clearMarkers();
    getStations();

    window.appState.map.setCenter({ lat: 53.35014, lng: -6.266155 });
    window.appState.map.setZoom(14);

    window.appState.infoWindow.close();
    closeSidebar();
}