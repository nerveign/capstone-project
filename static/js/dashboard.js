// =========================================================
// DASHBOARD CONFIGURATION
// =========================================================

// 10 detik
const DASHBOARD_REFRESH_MS = 10000;

let powerChart = null;
let loadChart = null;


// =========================================================
// HELPER
// =========================================================

function setText(id, value) {
    const element = document.getElementById(id);

    if (element) {
        element.textContent = value ?? "--";
    }
}


function formatNumber(value, decimals = 1) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "--";
    }

    return number.toFixed(decimals);
}


function formatInterval(seconds) {
    const value = Number(seconds);

    if (!Number.isFinite(value)) {
        return "--";
    }

    if (value >= 60) {
        const minutes = value / 60;

        if (Number.isInteger(minutes)) {
            return `${minutes} min`;
        }

        return `${minutes.toFixed(1)} min`;
    }

    return `${value} s`;
}


// =========================================================
// PHASE DATA
// =========================================================

function updatePhases(data) {

    // PHASE R
    setText("voltage-r", formatNumber(data.voltage_r, 1));
    setText("current-r", formatNumber(data.current_r, 1));
    setText(
    "power-r",
    formatNumber(Number(data.power_r || 0) / 1000, 3)
);
    setText("pf-r", formatNumber(data.pf_r, 2));


    // PHASE S
    setText("voltage-s", formatNumber(data.voltage_s, 1));
    setText("current-s", formatNumber(data.current_s, 1));
    setText(
    "power-s",
    formatNumber(Number(data.power_s || 0) / 1000, 3))
    setText("pf-s", formatNumber(data.pf_s, 2));


    // PHASE T
    setText("voltage-t", formatNumber(data.voltage_t, 1));
    setText("current-t", formatNumber(data.current_t, 1));
    setText(
    "power-t",
    formatNumber(Number(data.power_t || 0) / 1000, 3)
);
    setText("pf-t", formatNumber(data.pf_t, 2));
}


// =========================================================
// KPI
// =========================================================

function updateKPI(data) {

    // =====================================================
    // TOTAL POWER
    // Data PZEM dalam Watt
    // Dashboard menampilkan kW
    // =====================================================

    const totalPowerKW =
        Number(data.total_power || 0) / 1000;

    setText(
        "total-power",
        formatNumber(totalPowerKW, 3)
    );


    // =====================================================
    // AVERAGE POWER FACTOR
    // Hanya menggunakan phase yang valid
    // =====================================================

    const pfValues = [];

    if (data.valid_r && Number.isFinite(Number(data.pf_r))) {
        pfValues.push(Number(data.pf_r));
    }

    if (data.valid_s && Number.isFinite(Number(data.pf_s))) {
        pfValues.push(Number(data.pf_s));
    }

    if (data.valid_t && Number.isFinite(Number(data.pf_t))) {
        pfValues.push(Number(data.pf_t));
    }


    const avgPF =
        pfValues.length > 0
            ? pfValues.reduce((a, b) => a + b, 0) / pfValues.length
            : null;


    setText(
        "avg-pf",
        avgPF !== null
            ? formatNumber(avgPF, 2)
            : "--"
    );


    // =====================================================
    // FREQUENCY
    // Rata-rata phase yang valid
    // =====================================================

    const frequencyValues = [];

    if (
        data.valid_r &&
        Number.isFinite(Number(data.frequency_r))
    ) {
        frequencyValues.push(Number(data.frequency_r));
    }

    if (
        data.valid_s &&
        Number.isFinite(Number(data.frequency_s))
    ) {
        frequencyValues.push(Number(data.frequency_s));
    }

    if (
        data.valid_t &&
        Number.isFinite(Number(data.frequency_t))
    ) {
        frequencyValues.push(Number(data.frequency_t));
    }


    const avgFrequency =
        frequencyValues.length > 0
            ? frequencyValues.reduce((a, b) => a + b, 0)
              / frequencyValues.length
            : null;


    setText(
        "frequency",
        avgFrequency !== null
            ? formatNumber(avgFrequency, 1)
            : "--"
    );


    // =====================================================
    // ENERGY
    // Jumlah energi tiga phase
    // =====================================================

    const energyR =
        Number(data.energy_r_kwh || 0);

    const energyS =
        Number(data.energy_s_kwh || 0);

    const energyT =
        Number(data.energy_t_kwh || 0);


    const totalEnergy =
        energyR + energyS + energyT;


    setText(
        "energy-today",
        formatNumber(totalEnergy, 3)
    );
}


// =========================================================
// OPERATION STATUS
// =========================================================

function updateOperation(data) {

    setText(
        "operation-status",
        data.operation_status
    );

    setText(
        "sampling-interval",
        formatInterval(data.sampling_interval)
    );

    setText(
        "last-packet",
        data.last_packet
    );

    setText(
        "load-state",
        data.load_state
    );

    setText(
        "shift",
        data.shift
    );
}


// =========================================================
// SYSTEM STATUS
// =========================================================

function updateSystem(data, events) {

    setText(
        "system-status",
        data.system_status
    );

    setText(
        "device-status",
        data.device_status
    );

    setText(
        "last-update",
        data.timestamp
    );

    setText(
        "data-interval",
        formatInterval(data.sampling_interval)
    );


    // Header
    setText(
        "header-last-update",
        data.timestamp
    );


    // Anomali terakhir
    if (Array.isArray(events) && events.length > 0) {

        const latestEvent = events[0];

        setText(
            "last-anomaly",
            latestEvent.time ||
            latestEvent.timestamp ||
            latestEvent.date ||
            "Ada"
        );

    } else {

        setText(
            "last-anomaly",
            "Belum ada"
        );
    }
}


// =========================================================
// AI ANALYTICS STATUS
// =========================================================

function updateAIStatus(ai) {

    if (!ai) {

        setText(
            "ai-system-status",
            "✓ SYSTEM READY"
        );

        setText(
            "ai-anomaly-status",
            "Waiting Model"
        );

        setText(
            "ai-load-status",
            "Waiting Model"
        );

        setText(
            "ai-energy-status",
            "Waiting Model"
        );

        return;
    }


    // System AI
    const systemStatus =
        ai.system_status || "Ready";

    setText(
        "ai-system-status",
        `✓ SYSTEM ${String(systemStatus).toUpperCase()}`
    );


    // Anomaly Detection
    const anomaly =
        ai.anomaly_detection || {};

    setText(
        "ai-anomaly-status",
        anomaly.status || "Waiting Model"
    );


    // Load Prediction
    const load =
        ai.load_prediction || {};

    setText(
        "ai-load-status",
        load.status || "Waiting Model"
    );


    // Energy Forecast
    const energy =
        ai.energy_forecast || {};

    setText(
        "ai-energy-status",
        energy.status || "Waiting Model"
    );
}


// =========================================================
// ENERGY SUMMARY
// =========================================================

function updateEnergySummary(summary) {

    if (!summary) {
        return;
    }


    setText(
        "summary-energy",
        `${formatNumber(summary.energy, 2)} kWh`
    );

    setText(
        "summary-power",
        `${formatNumber(summary.active_power, 2)} kW`
    );

    setText(
        "summary-pf",
        formatNumber(summary.power_factor, 2)
    );

    setText(
        "summary-frequency",
        `${formatNumber(summary.frequency, 2)} Hz`
    );
}


// =========================================================
// SYSTEM EVENT LOG
// =========================================================

function renderEvents(events) {

    const container =
        document.getElementById("event-log");

    if (!container) {
        return;
    }


    container.innerHTML = "";


    // Tidak ada event
    if (
        !Array.isArray(events) ||
        events.length === 0
    ) {

        const empty =
            document.createElement("div");

        empty.className = "event-empty";

        empty.textContent =
            "Tidak ada event atau anomali terbaru.";

        container.appendChild(empty);

        return;
    }


    // Maksimal tampilkan 5 event terbaru
    events.slice(0, 5).forEach(event => {

        const row =
            document.createElement("div");

        row.className = "alarm-row";


        // Dot
        const dot =
            document.createElement("div");

        dot.className = "alarm-dot";


        // Text
        const text =
            document.createElement("div");

        text.className = "alarm-text";


        const time =
            document.createElement("small");

        time.textContent =
            event.time ||
            event.timestamp ||
            event.date ||
            "--";


        const message =
            document.createElement("p");

        message.textContent =
            event.message ||
            event.event ||
            event.type ||
            "System Event";


        // Badge
        const badge =
            document.createElement("span");

        badge.className = "alarm-badge";

        badge.textContent =
            event.severity ||
            event.status ||
            "Info";


        // Warna berdasarkan severity
        const severity =
            String(
                event.severity ||
                event.status ||
                ""
            ).toLowerCase();


        if (severity === "warning") {

            dot.style.background = "#f59e0b";

            badge.style.background =
                "#fff3cd";

            badge.style.color =
                "#c17900";

        }

        else if (
            severity === "normal" ||
            severity === "info"
        ) {

            dot.style.background =
                "#22c55e";

            badge.style.background =
                "#dcfce7";

            badge.style.color =
                "#15803d";

        }

        else {

            dot.style.background =
                "#ef4444";
        }


        text.appendChild(time);
        text.appendChild(message);

        row.appendChild(dot);
        row.appendChild(text);
        row.appendChild(badge);

        container.appendChild(row);
    });
}


// =========================================================
// CHART
// =========================================================

function updateCharts(
    powerHistory,
    loadProfile
) {

    const powerCanvas =
        document.getElementById("powerChart");

    const loadCanvas =
        document.getElementById("loadChart");


    if (!powerCanvas || !loadCanvas) {
        return;
    }


    // -----------------------------------------
    // POWER HISTORY
    // -----------------------------------------

    const powerLabels =
        Array.isArray(powerHistory)
            ? powerHistory.map(item => item.time)
            : [];


    const powerValues =
        Array.isArray(powerHistory)
            ? powerHistory.map(item => item.value)
            : [];


    // -----------------------------------------
    // LOAD PROFILE
    // -----------------------------------------

    const loadLabels =
        Array.isArray(loadProfile)
            ? loadProfile.map(item => item.time)
            : [];


    const loadValues =
        Array.isArray(loadProfile)
            ? loadProfile.map(item => item.value)
            : [];


    // -----------------------------------------
    // POWER CHART
    // -----------------------------------------

    if (!powerChart) {

        powerChart =
            new Chart(
                powerCanvas.getContext("2d"),
                {
                    type: "line",

                    data: {
                        labels: powerLabels,

                        datasets: [{
                            label:
                                "Total Active Power",

                            data:
                                powerValues,

                            borderColor:
                                "#1267e8",

                            backgroundColor:
                                "rgba(18,103,232,0.08)",

                            tension: 0.35,

                            fill: true,

                            pointRadius: 3
                        }]
                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio: false,

                        plugins: {

                            legend: {
                                display: false
                            }
                        },

                        scales: {

                            y: {

                                beginAtZero: true,

                                title: {

                                    display: true,

                                    text: "kW"
                                }
                            }
                        }
                    }
                }
            );

    }

    else {

        powerChart.data.labels =
            powerLabels;

        powerChart.data.datasets[0].data =
            powerValues;

        powerChart.update();
    }


    // -----------------------------------------
    // LOAD CHART
    // -----------------------------------------

    if (!loadChart) {

        loadChart =
            new Chart(
                loadCanvas.getContext("2d"),
                {
                    type: "bar",

                    data: {

                        labels:
                            loadLabels,

                        datasets: [{

                            label: "Load",

                            data:
                                loadValues,

                            backgroundColor:
                                "#2783eb",

                            borderRadius: 3
                        }]
                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio: false,

                        plugins: {

                            legend: {
                                display: false
                            }
                        },

                        scales: {

                            y: {

                                beginAtZero: true,

                                title: {

                                    display: true,

                                    text: "kW"
                                }
                            }
                        }
                    }
                }
            );

    }

    else {

        loadChart.data.labels =
            loadLabels;

        loadChart.data.datasets[0].data =
            loadValues;

        loadChart.update();
    }
}


// =========================================================
// MAIN UPDATE
// =========================================================

async function updateDashboard() {
console.log(
    "Dashboard update:",
    new Date().toLocaleTimeString()
);

    try {

        const response =
            await fetch(
                "/api/latest",
                {
                    cache: "no-store"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Gagal mengambil data dari Flask"
            );
        }


        const data =
            await response.json();


        console.log(
            "Data dari Flask:",
            data
        );


        // -------------------------
        // UPDATE DASHBOARD
        // -------------------------

        updatePhases(data);

        updateKPI(data);

        updateOperation(data);


        // API kita menerima dua nama
        // agar kompatibel dengan app.py
        const ai =
            data.ai_status ||
            data["AI-status"];

        updateAIStatus(ai);


        updateSystem(
            data,
            data.events
        );


        updateEnergySummary(
            data.energy_summary
        );


        renderEvents(
            data.events
        );


        updateCharts(
            data.power_history,
            data.load_profile
        );


    }

    catch (error) {

        console.error(
            "Error update dashboard:",
            error
        );
    }
}


// =========================================================
// START
// =========================================================

// Update pertama kali
updateDashboard();

// Update setiap 5 menit
setInterval(
    updateDashboard,
    DASHBOARD_REFRESH_MS
);
// =========================================================
// SIDEBAR NAVIGATION
// =========================================================

document.addEventListener("DOMContentLoaded", function () {

    const menuItems = document.querySelectorAll(
        '.menu-item[href^="#"]'
    );

    menuItems.forEach(item => {

        item.addEventListener("click", function (event) {

            event.preventDefault();

            const targetId = this.getAttribute("href");
            const targetSection = document.querySelector(targetId);

            if (!targetSection) {
                console.error("Section tidak ditemukan:", targetId);
                return;
            }

            // Active menu
            menuItems.forEach(menu => {
                menu.classList.remove("active");
            });

            this.classList.add("active");

            // Hitung posisi section terhadap halaman
            const targetPosition =
                targetSection.getBoundingClientRect().top +
                window.pageYOffset -
                20;

            // Scroll halaman
            window.scrollTo({
                top: targetPosition,
                behavior: "smooth"
            });

            // Update URL tanpa reload
            history.replaceState(null, "", targetId);

        });

    });

});

