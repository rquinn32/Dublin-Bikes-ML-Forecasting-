document.addEventListener("DOMContentLoaded", () => {
    const dateInput = document.getElementById("date");
    const timeInput = document.getElementById("time");
    const form = document.getElementById("predict-form");
    const resultCard = document.getElementById("result-card");

    const resStation = document.getElementById("res-station");
    const resDate = document.getElementById("res-date");
    const resTime = document.getElementById("res-time");
    const resStatus = document.getElementById("res-status");

    const predictionSearch = document.getElementById("prediction-search");
    const predictionResults = document.getElementById("prediction-results");
    const selectedStation = document.getElementById("selected-station");

    const toggleBtn = document.getElementById("toggle-advanced-prediction");
    const advancedFields = document.getElementById("advanced-prediction-fields");

    //Limit long term predictions to 5 days ahead (max range for weather forecast)
    const today = new Date();
    const maxDate = new Date();
    maxDate.setDate(today.getDate() + 5);

    if (dateInput) {
        dateInput.min = today.toISOString().split("T")[0];
        dateInput.max = maxDate.toISOString().split("T")[0];
    }

    if (resultCard) {
        resultCard.classList.add("hidden");
    }

    //Toggle advanced prediction inputs
    if (toggleBtn && advancedFields) {
        toggleBtn.addEventListener("click", () => {
            advancedFields.classList.toggle("hidden");
            toggleBtn.textContent = advancedFields.classList.contains("hidden")
                ? "Further in advance?"
                : "Hide advanced options";
        });
    }
    //Store selected station and sync the prediction
    function setSelectedStation(station) {
        const stationId = station.number ?? station.station_id ?? station.id;
        const stationName = station.name ?? `Station ${stationId}`;

        window.selectedStationId = String(stationId);
        window.selectedStationName = stationName;

        if (selectedStation) {
            selectedStation.textContent = `Selected: ${stationName} (ID: ${stationId})`;
        }

        if (predictionSearch) {
            predictionSearch.value = stationName;
        }

        if (predictionResults) {
            predictionResults.innerHTML = "";
        }

        if (resultCard) {
            resultCard.classList.add("hidden");
        }
    }

    // Marker clicks also update prediction panel
    window.setPredictionStation = setSelectedStation;

    //Prediction station search
    if (predictionSearch && predictionResults) {
        predictionSearch.addEventListener("input", async () => {
            const query = predictionSearch.value.trim();
            predictionResults.innerHTML = "";

            if (!query) {
                return;
            }

            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }

                const stations = await response.json();

                stations.slice(0, 6).forEach((station) => {
                    const item = document.createElement("button");
                    item.type = "button";
                    item.className = "search-item";
                    item.textContent = station.name;

                    item.addEventListener("click", () => {
                        setSelectedStation(station);
                    });

                    predictionResults.appendChild(item);
                });
            } catch (error) {
                console.error("Prediction search error:", error);
            }
        });

        // Close when click outside the search area
        document.addEventListener("click", (event) => {
            if (!event.target.closest(".prediction-search")) {
                predictionResults.innerHTML = "";
            }
        });
    }

    //Run long term prediction and update
    async function runPrediction(date, time, stationId) {
        if (!date || !time || !stationId) {
            if (resultCard) {
                resultCard.classList.add("hidden");
            }
            return;
        }

        if (resStation) {
            resStation.textContent = window.selectedStationName || stationId;
        }

        if (resDate) {
            resDate.textContent = date;
        }

        if (resTime) {
            resTime.textContent = time;
        }

        if (resStatus) {
            resStatus.textContent = "Loading...";
        }

        if (resultCard) {
            resultCard.classList.remove("hidden");
        }

        const params = new URLSearchParams({
            date: date,
            time: time,
            station_id: stationId
        });

        try {
            const response = await fetch(`/api/longterm_model?${params.toString()}`);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }

            const data = await response.json();
            console.log("Prediction response:", data);

            if (resStatus) {
                resStatus.textContent =
                    data.status ??
                    data.availability ??
                    data.result ??
                    "Unknown";
            }
        } catch (error) {
            console.error("Prediction error:", error);

            if (resStatus) {
                resStatus.textContent = "Could not load status";
            }
        }
    }

    //Run short term prediction for selected station
    async function runShorttermPrediction(minutes, stationId) {
        if (!minutes || !stationId) {
            if (resultCard) {
                resultCard.classList.add("hidden");
            }
            return;
        }

        if (resStation) {
            resStation.textContent = window.selectedStationName || stationId;
        }

        if (resDate) {
            resDate.textContent = "Soon";
        }

        if (resTime) {
            resTime.textContent = `In ${minutes} minutes`;
        }

        if (resStatus) {
            resStatus.textContent = "Loading...";
        }

        if (resultCard) {
            resultCard.classList.remove("hidden");
        }

        const params = new URLSearchParams({
            minutes: minutes,
            station_id: stationId
        });

        try {
            const response = await fetch(`/api/shortterm_model?${params.toString()}`);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }

            const data = await response.json();

            if (resStatus) {
                resStatus.textContent = `Estimated bikes: ${data.predicted_bikes}`;
            }
        } catch (error) {
            console.error("Short-term prediction error:", error);

            if (resStatus) {
                resStatus.textContent = "Could not load estimate";
            }
        }
    }

    // Form submission for long term prediction
    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const date = dateInput ? dateInput.value : "";
            const time = timeInput ? timeInput.value : "";
            const stationId = window.selectedStationId;

            if (!stationId) {
                alert("Please choose a station first.");
                return;
            }

            await runPrediction(date, time, stationId);
        });

        form.addEventListener("input", () => {
            if (resultCard) {
                resultCard.classList.add("hidden");
            }
        });
    }

    // Quick prediction buttons for 10/30/60 min forecasts
    document.querySelectorAll(".quick-predict-btn").forEach((button) => {
        button.addEventListener("click", async () => {
            const stationId = window.selectedStationId;

            if (!stationId) {
                alert("Please choose a station first.");
                return;
            }

            const minutes = parseInt(button.dataset.minutes, 10);
            await runShorttermPrediction(minutes, stationId);
        });
    });
});