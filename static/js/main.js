console.log("NEUROTRACK frontend loaded");

/**
 * Global Utility for Neurotrack
 * Handles data collection and redirection between games
 */
const NeuroTrack = {
    // Current state of collected data
    data: JSON.parse(localStorage.getItem('neuro_results')) || {},

    // Save a specific metric and move to next page
    saveAndNext: function(key, value, nextUrl) {
        this.data[key] = value;
        localStorage.setItem('neuro_results', JSON.stringify(this.data));
        if (nextUrl) window.location.href = nextUrl;
    },

    // Submit all data to the backend
    submitResults: async function() {
        const payload = {
            user_name: localStorage.getItem('user_name') || 'Participant',
            ...this.data
        };

        try {
            const response = await fetch('/analyze_all', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const results = await response.json();
            localStorage.setItem('final_analysis', JSON.stringify(results));
            window.location.href = '/results';
        } catch (error) {
            console.error("Submission failed:", error);
            alert("Error saving results. Please check your connection.");
        }
    }
};

/**
 * Logic for Tapping Speed Game
 */
function initTappingGame() {
    let taps = 0;
    let timer = 10;
    let active = false;
    const btn = document.getElementById('tap-zone');
    const display = document.getElementById('tap-count');

    if (!btn) return;

    btn.addEventListener('pointerdown', (e) => {
        e.preventDefault();
        if (!active && timer === 10) {
            active = true;
            let countdown = setInterval(() => {
                timer--;
                document.getElementById('timer').innerText = timer;
                if (timer <= 0) {
                    clearInterval(countdown);
                    active = false;
                    NeuroTrack.saveAndNext('tapping_count', taps, '/trail_making');
                }
            }, 1000);
        }
        if (active) {
            taps++;
            display.innerText = taps;
        }
    });
}

/**
 * Logic for Trail Making Test
 */
function initTrailMaking() {
    const canvas = document.getElementById('trail-canvas');
    if (!canvas) return;
    
    const startTime = Date.now();
    let currentTarget = 1;
    // Points are predefined or randomly generated in the template
    
    canvas.addEventListener('click', (e) => {
        // Logic to detect if currentTarget was clicked
        // If 1-5 connected, calculate duration and move on
        // NeuroTrack.saveAndNext('trail_time', duration, '/gonogo');
    });
}

/**
 * Logic for Go/No-Go Game
 */
function initGoNoGo() {
    let rounds = 0;
    let correct = 0;
    const target = document.getElementById('gng-target');
    
    if (!target) return;

    function nextRound() {
        if (rounds >= 20) {
            NeuroTrack.saveAndNext('gonogo_accuracy', correct / 20, '/digit_span');
            return;
        }
        
        const isGo = Math.random() > 0.3; // 70% chance of "Go" (Green)
        target.className = isGo ? 'target green' : 'target red';
        target.innerText = isGo ? 'CLICK!' : 'WAIT';
        
        let clicked = false;
        target.onclick = () => {
            clicked = true;
            if (isGo) correct++;
            else correct--; // Penalty for false alarm
            target.onclick = null;
        };

        setTimeout(() => {
            if (!clicked && !isGo) correct++; // Correctly waited
            rounds++;
            nextRound();
        }, 1200);
    }
    
    nextRound();
}

/**
 * Logic for Digit Span Test
 */
function initDigitSpan() {
    const submitBtn = document.getElementById('submit-btn');
    if (!submitBtn) return;

    submitBtn.onclick = () => {
        // Logic to check answer against sequence
        // If wrong, save final length and move on
        // NeuroTrack.saveAndNext('digit_span_length', length, '/flanker');
    };
}

/**
 * Logic for Flanker Task
 */
function initFlanker() {
    let totalRt = 0;
    let trials = 0;
    // logic to show arrows and record response time
    // After 10 trials, save avg RT and move on
    // NeuroTrack.saveAndNext('flanker_avg_rt', totalRt/10, '/visual_search');
}

/**
 * Logic for Visual Search
 */
function initVisualSearch() {
    let vsRt = 0;
    let vsTrials = 0;
    // Logic to find target among distractors
    // After 5 trials, finalize and submit all results
    // NeuroTrack.saveAndNext('visual_search_rt', vsRt/5, null);
    // NeuroTrack.submitResults();
}

// Auto-init based on URL path
document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;
    if (path.includes('tapping')) initTappingGame();
    if (path.includes('trail_making')) initTrailMaking();
    if (path.includes('gonogo')) initGoNoGo();
    if (path.includes('digit_span')) initDigitSpan();
    if (path.includes('flanker')) initFlanker();
    if (path.includes('visual_search')) initVisualSearch();
});