document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const categorySelect = document.getElementById('category-select');
    const englishWordEl = document.getElementById('english-word');
    const tamilWordEl = document.getElementById('tamil-word');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const speakBtn = document.getElementById('speak-btn');
    const timerEl = document.getElementById('timer');
    const cardEl = document.querySelector('.card');

    // State
    let currentCategory = "";
    let currentIndex = 0;
    let timerInterval;
    let seconds = 0;

    // Initialize
    function init() {
        populateCategories();
        // Select first category by default
        currentCategory = Object.keys(slideData)[0];
        updateDisplay();
        restartTimer();
        setupSpeechSynthesis();
    }

    // Populate Category Dropdown
    function populateCategories() {
        if (typeof slideData === 'undefined') {
            console.error("Data not found. Make sure data.js is loaded.");
            englishWordEl.textContent = "Error";
            tamilWordEl.textContent = "Data not loaded";
            return;
        }

        const categories = Object.keys(slideData);
        categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat;
            option.textContent = cat;
            categorySelect.appendChild(option);
        });

        // Event Listener for Category Change
        categorySelect.addEventListener('change', (e) => {
            currentCategory = e.target.value;
            currentIndex = 0;
            updateDisplay();
            restartTimer();
        });
    }

    // Update Slide Display
    function updateDisplay(direction = 'none') {
        const words = slideData[currentCategory];
        const currentWord = words[currentIndex];

        // Animate transition
        cardEl.classList.remove('slide-anim-right', 'slide-anim-left');
        void cardEl.offsetWidth; // Trigger reflow

        if (direction === 'next') {
            cardEl.classList.add('slide-anim-right');
        } else if (direction === 'prev') {
            cardEl.classList.add('slide-anim-left');
        }

        englishWordEl.textContent = currentWord.en;
        tamilWordEl.textContent = currentWord.ta;

        // Auto-pronounce (optional - uncomment if desired to auto-speak on navigation)
        // speakTwice(currentWord);
    }

    // Navigation Logic
    function nextSlide() {
        const words = slideData[currentCategory];
        if (currentIndex < words.length - 1) {
            currentIndex++;
        } else {
            currentIndex = 0; // Loop back to start
        }
        updateDisplay('next');
        restartTimer();
    }

    function prevSlide() {
        const words = slideData[currentCategory];
        if (currentIndex > 0) {
            currentIndex--;
        } else {
            currentIndex = words.length - 1; // Loop to end
        }
        updateDisplay('prev');
        restartTimer();
    }

    // Timer Logic
    function restartTimer() {
        clearInterval(timerInterval);
        seconds = 0;
        timerEl.textContent = seconds;
        timerInterval = setInterval(() => {
            seconds++;
            timerEl.textContent = seconds;
        }, 1000);
    }

    // Speech Synthesis Logic
    function speakTwice(text) {
        // Cancel any current speech
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'ta-IN'; // Tamil India
        utterance.rate = 0.9;     // Slightly slower for kids

        // Check if Tamil voice is available
        const voices = window.speechSynthesis.getVoices();
        const tamilVoice = voices.find(v => v.lang.includes('ta') || v.name.toLowerCase().includes('tamil'));

        if (tamilVoice) {
            utterance.voice = tamilVoice;
        }

        window.speechSynthesis.speak(utterance);
    }

    function setupSpeechSynthesis() {
        // Voices load asynchronously in some browsers
        window.speechSynthesis.onvoiceschanged = () => {
            console.log("Voices loaded");
        };
    }

    // Event Listeners
    nextBtn.addEventListener('click', nextSlide);
    prevBtn.addEventListener('click', prevSlide);

    speakBtn.addEventListener('click', () => {
        const word = slideData[currentCategory][currentIndex].ta;
        speakTwice(word);
    });

    // Keyboard Navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight') {
            nextSlide();
        } else if (e.key === 'ArrowLeft') {
            prevSlide();
        } else if (e.key === ' ' || e.key === 'Enter') {
            const word = slideData[currentCategory][currentIndex].ta;
            speakTwice(word);
        }
    });

    // Start App
    init();
});
