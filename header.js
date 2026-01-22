// header.js

const headerHTML = `
<div id="page-progress" style="position:fixed; top:0; left:0; height:3px; background:#eebf45; z-index:2001; width:0%;"></div>

<div class="top-dashboard">
    <div class="td-row-1">
        <div class="td-social">
            <span>Follow Us:</span>
            <a href="#"><i class="fa-brands fa-linkedin"></i></a>
            <a href="#"><i class="fa-brands fa-instagram"></i></a>
            <a href="#"><i class="fa-brands fa-facebook"></i></a>
        </div>
        <div class="td-news-ticker">
            <div class="ticker-label"><div class="live-dot"></div> MARKET FEED</div>
            <div class="ticker-track" id="dynamic-ticker"></div>
        </div>
        <div class="td-utilities desktop-only">
             <button class="lang-btn"><i class="fa-solid fa-globe"></i> Global (EN)</button>
        </div>
    </div>
    <div class="td-row-2">
        <div class="forex-group">
            <span id="forex-date" style="font-size:0.7rem; color:rgba(255,255,255,0.8); text-transform:uppercase; margin-right:10px;"></span>
            <div class="forex-item" id="fx-usd">USD/INR <span>..</span></div>
            <div class="forex-item desktop-only" id="fx-eur" style="margin-left:15px;">EUR/INR <span>..</span></div>
        </div>
        <a href="contact.html" class="visit-plan"><i class="fa-solid fa-plane-departure"></i> MEET US AT GULFOOD DUBAI</a>
    </div>
</div>

<div id="preloader">
    <img src="https://jftagro.com/wp-content/uploads/2023/01/jft-final-02-scaled.png" alt="Loading..." style="width:120px; margin-bottom:20px;">
    <div style="width:200px; height:3px; background:#eee; border-radius:3px;"><div class="loader-fill"></div></div>
    <div style="margin-top:10px; color:#888; font-size:0.9rem;">Connecting Global Markets...</div>
</div>

<nav class="jft-navbar" id="navbar">
    <div class="jft-wide-container nav-flex">
        <a href="index.html" class="nav-logo-link">
            <img src="https://jftagro.com/wp-content/uploads/2023/01/jft-final-02-scaled.png" alt="JFT Agro" class="nav-logo-img">
        </a>
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

// --- LOGIC ---

document.addEventListener("DOMContentLoaded", function() {
    
    // 1. Highlight Active Link
    const currentPage = window.location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPage) link.classList.add('active');
    });

    // 2. Preloader
    setTimeout(() => { 
        const pl = document.getElementById('preloader'); 
        if(pl) { pl.style.opacity='0'; setTimeout(()=>{ pl.style.display='none'; }, 500); }
    }, 1500);

    // 3. Populate Ticker
    const ticker = document.getElementById('dynamic-ticker');
    if(ticker) {
        const news = [
            '<div class="t-item"><i class="fa-solid fa-ship"></i> RICE: Export Quota Increased 15%</div>',
            '<div class="t-item"><i class="fa-solid fa-leaf"></i> SPICES: New Cardamom Arrivals in Kerala</div>',
            '<div class="t-item"><i class="fa-solid fa-wheat"></i> WHEAT: Global Price Index Stabilizing</div>',
            '<div class="t-item"><i class="fa-solid fa-cubes"></i> SUGAR: Indian Production Outlook Positive</div>'
        ];
        ticker.innerHTML = news.join('') + news.join(''); // Duplicate for infinite scroll
    }

    // 4. Forex Simulation
    document.getElementById('forex-date').innerText = new Date().toLocaleDateString('en-GB', {day:'numeric', month:'short', year:'numeric'});
    document.getElementById('fx-usd').innerHTML = `USD/INR <span class="forex-up">84.10 ▲</span>`;
    document.getElementById('fx-eur').innerHTML = `EUR/INR <span class="forex-up">90.50 ▲</span>`;
});

// Helper Functions
function toggleMenu() {
    const menu = document.getElementById('navMenu');
    const icon = document.querySelector('.mobile-toggle i');
    menu.classList.toggle('active');
    if(menu.classList.contains('active')) {
        icon.classList.remove('fa-bars'); icon.classList.add('fa-xmark');
    } else {
        icon.classList.remove('fa-xmark'); icon.classList.add('fa-bars');
    }
}

window.onscroll = function() {
    // Progress Bar
    let winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    let height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    let scrolled = (winScroll / height) * 100;
    document.getElementById("page-progress").style.width = scrolled + "%";
    
    // Sticky Nav
    const nav = document.getElementById('navbar');
    if (window.scrollY > 50) nav.classList.add('scrolled');
    else nav.classList.remove('scrolled');
};
