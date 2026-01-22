// header.js

const headerHTML = `
<div id="page-progress"></div>

<div class="top-dashboard">
    <div class="td-row-1">
        <div class="td-social">
            <span>Follow Us:</span>
            <a href="#" target="_blank"><i class="fa-brands fa-linkedin"></i></a>
            <a href="#" target="_blank"><i class="fa-brands fa-instagram"></i></a>
            <a href="#" target="_blank"><i class="fa-brands fa-facebook"></i></a>
        </div>
        <div class="td-news-ticker">
            <div class="ticker-label"><div class="live-dot"></div> MARKET FEED</div>
            <div class="ticker-track" id="dynamic-ticker"></div>
        </div>
        <div class="td-utilities desktop-only">
            <div class="lang-dropdown">
                <button onclick="toggleLang()" class="lang-btn"><i class="fa-solid fa-globe"></i> Global (EN) <i class="fa-solid fa-caret-down"></i></button>
                <div class="lang-menu" id="langMenu">
                    <a onclick="changeLanguage('en')">English</a>
                    <a onclick="changeLanguage('hi')">हिन्दी (Hindi)</a>
                    <a onclick="changeLanguage('zh-CN')">中文 (Mandarin)</a>
                    <a onclick="changeLanguage('es')">Español (Spanish)</a>
                    <a onclick="changeLanguage('ar')">العربية (Arabic)</a>
                </div>
            </div>
        </div>
    </div>
    <div class="td-row-2">
        <div class="forex-group">
            <span id="forex-date" style="font-size:0.7rem; color:rgba(255,255,255,0.8); text-transform:uppercase;"></span>
            <div class="forex-item" id="fx-usd">USD/INR <span>..</span></div>
            <div class="forex-item" id="fx-eur">EUR/INR <span>..</span></div>
            <div class="forex-item desktop-only" id="fx-gbp">GBP/INR <span>..</span></div>
        </div>
        <a href="contact.html" class="visit-plan"><i class="fa-solid fa-plane-departure"></i> MEET US AT GULFOOD DUBAI</a>
    </div>
</div>

<div id="google_translate_element" style="display:none;"></div>

<div id="preloader">
    <img src="https://jftagro.com/wp-content/uploads/2023/01/jft-final-02-scaled.png" alt="JFT Loading" class="loader-logo-img">
    <div class="loader-text" id="welcome-msg">Connecting Global Markets...</div>
    <div class="loader-track"><div class="loader-fill"></div></div>
</div>

<nav class="jft-navbar" id="navbar">
    <div class="jft-wide-container nav-flex">
        <a href="index.html" class="nav-logo-link"><img src="https://jftagro.com/wp-content/uploads/2023/01/jft-final-02-scaled.png" alt="JFT Agro Overseas" class="nav-logo-img"></a>
        <div class="nav-menu" id="navMenu">
            <a href="index.html" class="nav-link">Home</a>
            <a href="about.html" class="nav-link">About</a>
            <a href="products.html" class="nav-link">Products</a>
            <a href="infrastructure.html" class="nav-link">Infra</a>
            <a href="network.html" class="nav-link">Network</a>
            <a href="contact.html" class="nav-link">Contact</a>
            <a href="contact.html" class="nav-btn-action desktop-only">Get Quote</a>
        </div>
        <div class="mobile-toggle" onclick="toggleMenu()"><i class="fa-solid fa-bars"></i></div>
    </div>
</nav>

<a href="https://wa.me/919800000000" class="whatsapp-float" target="_blank"><i class="fa-brands fa-whatsapp"></i></a>
<div class="sticky-quote"><a href="contact.html" class="sticky-btn">Request Export Quote</a></div>
`;

document.write(headerHTML);

// --- LOGIC & FUNCTIONALITY ---

document.addEventListener("DOMContentLoaded", function() {
    
    // 1. Highlight Active Link based on URL
    const currentPage = window.location.pathname.split("/").pop() || "index.html";
    const links = document.querySelectorAll('.nav-link');
    links.forEach(link => {
        const linkHref = link.getAttribute('href');
        if (linkHref === currentPage || (currentPage === "" && linkHref === "index.html")) {
            link.classList.add('active');
            link.style.color = "var(--jft-primary)";
        }
    });

    // 2. Initialize Features
    fetchLiveForex();
    initTicker();
    
    // 3. Preloader Logic
    const welcomeText = document.getElementById('welcome-msg');
    fetch('https://ipapi.co/json/')
        .then(response => response.json())
        .then(data => { 
            if (data.city) { welcomeText.innerHTML = `Connecting with <span style="color:#eebf45;">${data.city}</span>...`; } 
            else { welcomeText.innerText = "Establishing Global Trade Links..."; } 
        })
        .catch(() => {})
        .finally(() => { 
            setTimeout(() => { 
                const preloader = document.getElementById('preloader'); 
                if(preloader) {
                    preloader.style.opacity = '0'; 
                    setTimeout(() => { preloader.style.display = 'none'; }, 1000); 
                }
            }, 2000); 
        });
});

// --- HELPER FUNCTIONS ---

function toggleMenu() { 
    const menu = document.getElementById('navMenu'); 
    const icon = document.querySelector('.mobile-toggle i'); 
    menu.classList.toggle('active'); 
    if(menu.classList.contains('active')) { 
        icon.classList.remove('fa-bars'); 
        icon.classList.add('fa-xmark'); 
    } else { 
        icon.classList.remove('fa-xmark'); 
        icon.classList.add('fa-bars'); 
    } 
}

function toggleLang() { document.getElementById('langMenu').classList.toggle('show'); }
function changeLanguage(langCode) { 
    var selectField = document.querySelector(".goog-te-combo"); 
    if(selectField) { 
        selectField.value = langCode; 
        selectField.dispatchEvent(new Event("change")); 
    } 
    document.getElementById('langMenu').classList.remove('show'); 
}
window.onclick = function(e) { if (!e.target.closest('.lang-btn')) {
    const lm = document.getElementById('langMenu');
    if(lm) lm.classList.remove('show'); 
}}

window.onscroll = function() {
    let winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    let height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    let scrolled = (winScroll / height) * 100;
    
    const progressBar = document.getElementById("page-progress");
    if(progressBar) progressBar.style.width = scrolled + "%";
    
    const nav = document.getElementById('navbar'); 
    if(nav) {
        if (window.scrollY > 50) nav.classList.add('scrolled'); 
        else nav.classList.remove('scrolled');
    }
};

async function fetchLiveForex() {
    try {
        const response = await fetch('https://api.frankfurter.app/latest?from=USD&to=INR'); 
        const data = await response.json();
        if(data && data.rates) {
            updateTickerDOM('fx-usd', 'USD/INR', data.rates.INR); 
            // Mocking others for demo as API might limit calls
            updateTickerDOM('fx-eur', 'EUR/INR', data.rates.INR * 1.08); 
            updateTickerDOM('fx-gbp', 'GBP/INR', data.rates.INR * 1.25);
        }
    } catch (e) { 
        if(document.getElementById('fx-usd')) document.getElementById('fx-usd').innerHTML = 'USD/INR <span class="forex-up">84.10 ▲</span>'; 
    }
}
function updateTickerDOM(id, label, value) { 
    const el = document.getElementById(id);
    if(el) el.innerHTML = `${label} <span class="forex-up">${value.toFixed(2)} ▲</span>`; 
}

function initTicker() {
    const tickerContainer = document.getElementById('dynamic-ticker');
    const dateSpan = document.getElementById('forex-date');
    const today = new Date();
    
    if(dateSpan) {
        const dateOptions = { day: 'numeric', month: 'short', year: 'numeric' }; 
        dateSpan.innerText = "RATES: " + today.toLocaleDateString('en-GB', dateOptions);
    }

    if(tickerContainer) {
        const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
        const fullNews = [ 
            `<div class="t-item daily-flash"><i class="fa-solid fa-calendar-day"></i><span>${days[today.getDay()]}:</span> Global Markets Active</div>`, 
            `<div class="t-item"><i class="fa-solid fa-ship"></i><span>RICE:</span> Non-Basmati Export Quota Increased for ${today.getFullYear()}</div>`, 
            `<div class="t-item"><i class="fa-solid fa-leaf"></i><span>SPICES:</span> Fresh Cardamom Arrivals in Kerala Auctions</div>`, 
            `<div class="t-item"><i class="fa-solid fa-wheat"></i><span>WHEAT:</span> Global Price Index Stabilizing</div>`
        ];
        tickerContainer.innerHTML = fullNews.join('') + fullNews.join(''); 
    }
}

function googleTranslateElementInit() { new google.translate.TranslateElement({pageLanguage: 'en', includedLanguages: 'en,hi,zh-CN,es,ar', layout: google.translate.TranslateElement.InlineLayout.SIMPLE}, 'google_translate_element'); }
(function() {
    var gtScript = document.createElement('script');
    gtScript.type = 'text/javascript';
    gtScript.src = '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
    document.body.appendChild(gtScript);
})();
