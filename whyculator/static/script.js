// WHYculator – Frontend logic for classic calculator UI
// Handles button inputs, builds expression, calls Flask backend, and updates UI.

(() => {
    // ----- Element references -----
    const display = document.getElementById('calc-display');
    const chaosToggle = document.getElementById('chaos-mode');
    const soundToggle = document.getElementById('sound-toggle');
    const resultSection = document.getElementById('result-section');
    const resultText = document.getElementById('result-text');
    const confidenceText = document.getElementById('confidence-text');
    const explanationText = document.getElementById('explanation-text');
    const chaosText = document.getElementById('chaos-text');
    const statsList = {
        total: document.getElementById('stat-total'),
        ignored: document.getElementById('stat-ignored'),
        useless: document.getElementById('stat-useless')
    };
    const historyList = document.getElementById('history-list');
    const excuseBtn = document.getElementById('excuse-button');
    const excuseText = document.getElementById('excuse-text');

    // ----- Sound (optional) – generate a short beep using Web Audio API -----
    const playSound = () => {
        if (!soundToggle.checked) return;
        try {
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioCtx.createOscillator();
            const gainNode = audioCtx.createGain();
            oscillator.type = 'sine';
            oscillator.frequency.setValueAtTime(440, audioCtx.currentTime); // A4 note
            oscillator.connect(gainNode);
            gainNode.connect(audioCtx.destination);
            gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime); // volume
            oscillator.start();
            oscillator.stop(audioCtx.currentTime + 0.1); // 100ms beep
        } catch (e) {
            console.error('Audio error', e);
        }
    };

    // ----- Helper state -----
    let firstNumber = null;   // number before operator
    let operation = null;     // '+', '-', '*', '/' as string

    // ----- UI helpers -----
    const appendToDisplay = (val) => {
        if (val === '.' && display.value.includes('.')) return; // prevent multiple dots
        // Replace leading zero unless it's a decimal point
        if (display.value === '0' && val !== '.') {
            display.value = val;
        } else {
            display.value += val;
        }
    };

    const clearAll = () => {
        display.value = '';
        firstNumber = null;
        operation = null;
    };

    const showLoader = () => {
        const loader = document.createElement('div');
        loader.className = 'loader';
        resultSection.innerHTML = '';
        resultSection.appendChild(loader);
        resultSection.classList.remove('hidden');
    };

    const hideLoader = () => {
        const loader = resultSection.querySelector('.loader');
        if (loader) loader.remove();
    };

    const updateStatsUI = (stats) => {
        statsList.total.textContent = stats.total_calculations;
        statsList.ignored.textContent = stats.ignored_requests;
        statsList.useless.textContent = `${stats.uselessness}%`;
    };

    const addHistoryEntry = (entry) => {
        const li = document.createElement('li');
        const opName = {
            '+': 'Addition',
            '-': 'Subtraction',
            '*': 'Multiplication',
            '/': 'Division'
        }[entry.actual_operation];
        li.textContent = `${entry.original_first} ${entry.requested_operation} ${entry.original_second} → ${entry.calculated_first} ${entry.actual_operation} ${entry.calculated_second} = ${entry.result} (${opName})`;
        historyList.prepend(li);
    };

    const displayResult = (data) => {
        hideLoader();
        if (!data.success) {
            display.value = 'Error';
            return;
        }
        if (data.easter_egg) {
            display.value = data.explanation || data.easter_egg;
            return;
        }
        const { result, original_first, original_second, requested_operation } = data;
        // Update input summary
        const inputSummary = document.getElementById('input-summary');
        if (inputSummary) {
            inputSummary.textContent = `${original_first} ${requested_operation} ${original_second}`;
        }
        display.value = result !== null ? result : 'Error';
        // Refresh stats and add history entry
        fetch('/stats')
            .then(r => r.json())
            .then(updateStatsUI)
            .catch(console.error);
        addHistoryEntry(data);
    };

    const calculate = async () => {
        if (firstNumber === null || operation === null) {
            alert('Please complete an operation before pressing =');
            return;
        }
        const secondNumber = parseFloat(display.value);
        if (isNaN(secondNumber)) {
            alert('Invalid second number');
            return;
        }
        const payload = {
            first_number: firstNumber,
            second_number: secondNumber,
            operation: operation,
            chaos_mode: chaosToggle.checked
        };
        playSound();
        showLoader();
        try {
            const resp = await fetch('/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await resp.json();
            displayResult(data);
        } catch (e) {
            console.error(e);
            hideLoader();
            resultText.textContent = '❌ Network error.';
            resultSection.classList.remove('hidden');
        }
        // After sending, reset internal state for next calculation
        firstNumber = null;
        operation = null;
    };

    const generateExcuse = async () => {
        try {
            const resp = await fetch('/excuse');
            const { excuse } = await resp.json();
            excuseText.textContent = excuse;
        } catch (e) {
            console.error(e);
            excuseText.textContent = 'Failed to fetch excuse.';
        }
    };

    const init = () => {
        // Number buttons
        document.querySelectorAll('.btn[data-value]').forEach(btn => {
            btn.addEventListener('click', () => {
                appendToDisplay(btn.dataset.value);
            });
        });
        // Operator buttons
        document.querySelectorAll('.btn.op').forEach(btn => {
            btn.addEventListener('click', () => {
                if (display.value === '') return; // nothing to store
                firstNumber = parseFloat(display.value);
                operation = btn.dataset.op;
                display.value = '';
            });
        });
        // Equals
        document.getElementById('equals').addEventListener('click', calculate);
        // Clear
        document.getElementById('clear').addEventListener('click', () => {
            clearAll();
            resultSection.classList.add('hidden');
        });
        // Excuse button
        excuseBtn.addEventListener('click', generateExcuse);
        // Load initial stats
        fetch('/stats')
            .then(r => r.json())
            .then(updateStatsUI)
            .catch(console.error);
        // Hidden reset on double‑click header (same as before)
        document.querySelector('header.header').addEventListener('dblclick', async () => {
            if (!confirm('Reset all stats and history?')) return;
            try {
                await fetch('/reset', { method: 'POST' });
                resultSection.classList.add('hidden');
                historyList.innerHTML = '';
                statsList.total.textContent = '0';
                statsList.ignored.textContent = '0';
                statsList.useless.textContent = '0%';
                clearAll();
            } catch (e) {
                console.error(e);
            }
        });
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
