// js/main.js

// Wait for the layout (header/footer) to be injected before running scripts
document.addEventListener('layoutLoaded', () => {
    console.log("Layout Loaded. Initializing Scripts...");
    initApp();
});

function initApp() {
    // --- 1. Active Link Highlighter ---
    // Automatically adds 'active' class to the navbar link matching the current page
    const currentPath = window.location.pathname;
    const pageName = currentPath.split('/').pop(); // e.g., "about.html"
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const linkHref = link.getAttribute('href');
        // Check if link matches current page OR if it's the home link on root
        if (linkHref === pageName || 
           (linkHref === 'index.html' && (currentPath === '/' || currentPath.endsWith('/') || currentPath.endsWith('index.html')))) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    // --- 2. Navigation Toggle Functions ---
    // Attached to window so they can be called from HTML onclick attributes
    window.toggleMenu = function() { 
        const menu = document.getElementById('navMenu'); 
        const icon = document.querySelector('.mobile-toggle i'); 
        if (menu && icon) {
            menu.classList.toggle('active'); 
            if(menu.classList.contains('active')) { 
                icon.classList.remove('fa-bars'); 
                icon.classList.add('fa-xmark'); 
            } else { 
                icon.classList.remove('fa-xmark'); 
                icon.classList.add('fa-bars'); 
            } 
        }
    }
    
    window.toggleLang = function() { 
        const langMenu = document.getElementById('langMenu');
        if (langMenu) langMenu.classList.toggle('show'); 
    }
    
    window.changeLanguage = function(langCode) { 
        // Logic for Google Translate (if implemented) or just placeholder
        document.getElementById('langMenu').classList.remove('show'); 
        // Reload or redirect logic would go here
    }
    
    // Close language menu if clicking outside
    window.onclick = function(e) { 
        if (!e.target.closest('.lang-btn') && document.getElementById('langMenu')) {
            document.getElementById('langMenu').classList.remove('show'); 
        }
    }

    // --- 3. Scroll Progress & Sticky Navbar ---
    window.onscroll = function() {
        // Progress Bar
        let winScroll = document.body.scrollTop || document.documentElement.scrollTop;
        let height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        let scrolled = (winScroll / height) * 100;
        const progBar = document.getElementById("page-progress");
        if(progBar) progBar.style.width = scrolled + "%";
        
        // Sticky Navbar
        const nav = document.getElementById('navbar'); 
        if(nav) {
            if (window.scrollY > 50) nav.classList.add('scrolled'); 
            else nav.classList.remove('scrolled');
        }
    };

    // --- 4. Live Forex (with Fallback) ---
    async function fetchLiveForex() {
        try {
            // Using a free API (Frankfurter)
            const response = await fetch('https://api.frankfurter.app/latest?from=USD&to=INR,EUR,GBP'); 
            const data = await response.json();
            
            if(data && data.rates) {
                const usdInr = data.rates.INR; 
                
                // Fetch EUR to INR
                const resEur = await fetch('https://api.frankfurter.app/latest?from=EUR&to=INR'); 
                const dataEur = await resEur.json(); 
                const eurInr = dataEur.rates.INR; 
                
                // Fetch GBP to INR
                const resGbp = await fetch('https://api.frankfurter.app/latest?from=GBP&to=INR'); 
                const dataGbp = await resGbp.json(); 
                const gbpInr = dataGbp.rates.INR;

                updateTickerDOM('fx-usd', 'USD/INR', usdInr); 
                updateTickerDOM('fx-eur', 'EUR/INR', eurInr); 
                updateTickerDOM('fx-gbp', 'GBP/INR', gbpInr);
            }
        } catch (e) { 
            // Fallback if API fails
            const usd = document.getElementById('fx-usd');
            const eur = document.getElementById('fx-eur');
            if(usd) usd.innerHTML = 'USD/INR <span class="forex-up">84.10 ▲</span>'; 
            if(eur) eur.innerHTML = 'EUR/INR <span class="forex-up">90.50 ▲</span>';
        }
    }
    
    function updateTickerDOM(id, label, value) { 
        const el = document.getElementById(id);
        if(el && value) el.innerHTML = `${label} <span class="forex-up">${value.toFixed(2)} ▲</span>`; 
    }

    fetchLiveForex();
    
    // Date & Ticker Init
    const dateOptions = { day: 'numeric', month: 'short', year: 'numeric' }; 
    const today = new Date();
    const dateSpan = document.getElementById('forex-date'); 
    if(dateSpan) dateSpan.innerText = "RATES AS OF " + today.toLocaleDateString('en-GB', dateOptions);
    
    const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    const tickerContainer = document.getElementById('dynamic-ticker');
    if(tickerContainer) {
        let dailyHeadline = "Global Markets Steady";
        if(today.getDay() === 1) dailyHeadline = "Market Opening: Strong Demand in Asia"; 
        else if(today.getDay() === 5) dailyHeadline = "Weekly Wrap: Rice Exports Surge 15%";
        
        const fullNews = [ 
            `<div class="t-item daily-flash"><i class="fa-solid fa-calendar-day"></i><span>${days[today.getDay()]}, ${today.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}:</span> ${dailyHeadline}</div>`, 
            `<div class="t-item"><i class="fa-solid fa-ship"></i><span>RICE:</span> Non-Basmati Export Quota Increased for ${today.getFullYear()}</div>`, 
            `<div class="t-item"><i class="fa-solid fa-leaf"></i><span>SPICES:</span> Fresh Cardamom Arrivals in Kerala Auctions</div>`, 
            `<div class="t-item"><i class="fa-solid fa-wheat"></i><span>WHEAT:</span> Global Price Index Stabilizing</div>`, 
            `<div class="t-item"><i class="fa-solid fa-cube"></i><span>SUGAR:</span> Indian Production Outlook Positive</div>`, 
            `<div class="t-item"><i class="fa-solid fa-bowl-food"></i><span>LOGISTICS:</span> Freight Rates to Red Sea Normalizing</div>` 
        ];
        tickerContainer.innerHTML = fullNews.join('') + fullNews.join(''); 
    }

    // --- 5. Certification Slider Logic ---
    const track = document.getElementById('certTrack'); 
    const container = document.getElementById('certSlider');
    if(track && container) {
        // Clone items for infinite loop
        Array.from(track.children).forEach(item => { const clone = item.cloneNode(true); track.appendChild(clone); });
        
        let position = 0, speed = 0.5, isDragging = false, startX, prevTranslate = 0, animationID;
        
        function animate() { 
            if(!isDragging) { 
                position -= speed; 
                // Reset when half way (since we duplicated items)
                if (Math.abs(position) >= (track.scrollWidth / 2)) { position = 0; } 
                track.style.transform = `translateX(${position}px)`; 
            } 
            animationID = requestAnimationFrame(animate); 
        }
        animate();
        
        // Touch/Drag Events for Cert Slider
        const startDrag = (e) => { isDragging = true; startX = getPositionX(e); const style = window.getComputedStyle(track); const matrix = new WebKitCSSMatrix(style.transform); position = matrix.m41; prevTranslate = position; cancelAnimationFrame(animationID); }
        const drag = (e) => { if(isDragging) { const currentPosition = getPositionX(e); const diff = currentPosition - startX; position = prevTranslate + diff; track.style.transform = `translateX(${position}px)`; } }
        const endDrag = () => { if(isDragging) { isDragging = false; animate(); } }
        const getPositionX = (event) => { return event.type.includes('mouse') ? event.pageX : event.touches[0].clientX; }
        
        container.addEventListener('mousedown', startDrag); container.addEventListener('touchstart', startDrag);
        container.addEventListener('mouseup', endDrag); container.addEventListener('mouseleave', endDrag); container.addEventListener('touchend', endDrag); 
        container.addEventListener('mousemove', drag); container.addEventListener('touchmove', drag);
    }

    // --- 6. Stats Counter ---
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => { 
            if(entry.isIntersecting) { 
                const counter = entry.target.querySelector('h3');
                if(counter && !counter.classList.contains('counted')) {
                    const target = +entry.target.getAttribute('data-count'); 
                    const inc = target / 100; 
                    let count = 0;
                    const updateCount = () => { 
                        count += inc; 
                        if (count < target) { 
                            counter.innerText = Math.ceil(count); 
                            requestAnimationFrame(updateCount); 
                        } else { 
                            counter.innerText = target + "+"; 
                        } 
                    };
                    updateCount(); 
                    counter.classList.add('counted');
                }
            } 
        });
    }, { threshold: 0.5 });
    
    // Wait slightly for DOM to settle before observing
    setTimeout(() => { 
        document.querySelectorAll('.stat-item').forEach(el => statsObserver.observe(el)); 
    }, 500);

    // --- 7. Initial Load & Preloader ---
    const welcomeText = document.getElementById('welcome-msg');
    
    // Only fetch IP if on the Home/Index page (where welcome-msg exists)
    if(welcomeText) {
        fetch('https://ipapi.co/json/')
            .then(response => response.json())
            .then(data => { 
                if (data.city) { welcomeText.innerHTML = `Connecting with <span style="color:#eebf45;">${data.city}</span>...`; } 
                else { welcomeText.innerText = "Establishing Global Trade Links..."; } 
            })
            .catch(() => {})
            .finally(() => { 
                // Fade out preloader
                setTimeout(() => { 
                    const preloader = document.getElementById('preloader'); 
                    if(preloader) {
                        preloader.style.opacity = '0'; 
                        setTimeout(() => { preloader.style.display = 'none'; }, 1000);
                    } 
                }, 2500); 
            });
    } else {
        // Generic fallback for other pages (faster load)
        const preloader = document.getElementById('preloader');
        if(preloader) {
             setTimeout(() => { 
                preloader.style.opacity = '0'; 
                setTimeout(() => { preloader.style.display = 'none'; }, 1000);
            }, 1000);
        }
    }

    // --- 8. Hero Slider (Index Only) ---
    let slideIndex = 0; 
    window.setSlide = function(n) { slideIndex = n; updateSlider(); resetTimer(); } 
    
    function nextSlide() { 
        const slides = document.querySelectorAll('.hero-slide'); 
        if(slides.length > 0) { 
            slideIndex = (slideIndex + 1) % slides.length; 
            updateSlider(); 
        } 
    } 
    
    function updateSlider() { 
        const slides = document.querySelectorAll('.hero-slide'); 
        const dots = document.querySelectorAll('.control-dot'); 
        if(slides.length === 0) return; 
        
        slides.forEach(s => s.classList.remove('active')); 
        dots.forEach(d => d.classList.remove('active')); 
        
        slides[slideIndex].classList.add('active'); 
        dots[slideIndex].classList.add('active'); 
    } 
    
    // Only start slider if slides exist
    if(document.querySelectorAll('.hero-slide').length > 0) {
        let slideTimer = setInterval(nextSlide, 5000); 
        function resetTimer() { clearInterval(slideTimer); slideTimer = setInterval(nextSlide, 5000); }
    }

    // --- 9. Scroll Animations (Reveal) ---
    const revealObserver = new IntersectionObserver((entries) => { 
        entries.forEach(entry => { 
            if (entry.isIntersecting) { 
                entry.target.classList.add('active'); 
                // Specific check for Process Timeline animation
                if (entry.target.classList.contains('timeline-wrapper')) { 
                    const line = document.getElementById('progressLine');
                    if(line) line.style.width = '100%'; 
                } 
            } 
        }); 
    }, { threshold: 0.15 }); 
    document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));
    
    // --- 10. Network Map Logic (Index Only) ---
    const netContainer = document.getElementById('jft_nodes_container'); 
    const svgLayer = document.getElementById('jft_svg_lines'); 
    
    if(netContainer && svgLayer) { 
        const networkNodes = [ 
            { region: "African Continent", icon: "fa-ship", desc: "Bulk rice supplier to 15+ African nations.", countries: [{name:"Benin",type:"Parboiled"},{name:"Togo",type:"Rice"}] }, 
            { region: "Europe (EU)", icon: "fa-euro-sign", desc: "Certified Organic Spices & Grains.", countries: [{name:"UK",type:"Basmati"},{name:"Germany",type:"Spices"}] }, 
            { region: "Middle East", icon: "fa-mosque", desc: "Premier exporter of Basmati and Spices.", countries: [{name:"UAE",type:"1121 Rice"},{name:"Saudi",type:"Basmati"}] }, 
            { region: "Russia & CIS", icon: "fa-snowflake", desc: "Supply partner for Northern markets.", countries: [{name:"Moscow",type:"Rice"},{name:"St. Petersburg",type:"Spices"}] }, 
            { region: "Sri Lanka", icon: "fa-anchor", desc: "Direct supply route to Colombo Hub.", countries: [{name:"Colombo",type:"Rice"}] }, 
            { region: "SE Asia", icon: "fa-map-location-dot", desc: "Expanding footprint in Asian markets.", countries: [{name:"Vietnam",type:"Grains"}] } 
        ];
        
        const hubX = 500; const hubY = 325; 
        const nodeCoords = [{x:100,y:50}, {x:900,y:50}, {x:50,y:310}, {x:950,y:310}, {x:100,y:580}, {x:900,y:580}];

        networkNodes.forEach((node, index) => { 
            const div = document.createElement('div'); 
            div.className = `export-node node-${index} reveal`; 
            
            // Mobile tap interaction
            div.onclick = function(e) { 
                if(window.innerWidth <= 1024) { 
                    if(e.target.closest('.country-list-reveal')) return; 
                    const isActive = this.classList.contains('active-mobile'); 
                    document.querySelectorAll('.export-node').forEach(n => n.classList.remove('active-mobile')); 
                    if(!isActive) this.classList.add('active-mobile'); 
                } 
            }; 
            
            let listHTML = ""; 
            if(node.countries) { 
                listHTML = `<div class="country-list-reveal">`; 
                node.countries.forEach(c => { listHTML += `<div class="country-item">${c.name} <span>${c.type}</span></div>`; }); 
                listHTML += `</div>`; 
            } 
            
            div.innerHTML = `<div class="node-portal"><i class="fa-solid ${node.icon}"></i></div><div class="node-info"><h3>${node.region}</h3><p>${node.desc}</p></div>${listHTML}`; 
            netContainer.appendChild(div); 
            
            // Draw lines for desktop
            if(window.innerWidth > 1024) { 
                const coords = nodeCoords[index]; 
                const path = document.createElementNS("http://www.w3.org/2000/svg", "path"); 
                path.setAttribute("d", `M${hubX},${hubY} Q${(hubX+coords.x)/2},${hubY-50} ${coords.x},${coords.y}`); 
                path.setAttribute("class", "trade-path"); 
                svgLayer.appendChild(path); 
            } 
        }); 
        
        // Observe new nodes for animation
        document.querySelectorAll('.export-node').forEach(el => revealObserver.observe(el)); 
    }
}
