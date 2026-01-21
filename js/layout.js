// js/layout.js

const JFT_HEADER = `
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
                <span id="forex-date" style="font-size:0.7rem; color:#888; text-transform:uppercase;"></span>
                <div class="forex-item" id="fx-usd">USD/INR <span>..</span></div>
                <div class="forex-item" id="fx-eur">EUR/INR <span>..</span></div>
                <div class="forex-item desktop-only" id="fx-gbp">GBP/INR <span>..</span></div>
            </div>
            <a href="contact.html" class="visit-plan"><i class="fa-solid fa-plane-departure"></i> MEET US AT GULFOOD DUBAI</a>
        </div>
    </div>

    <div id="preloader">
        <img src="https://jftagro.com/wp-content/uploads/2023/01/jft-final-02-scaled.png" alt="JFT Loading" class="loader-logo-img">
        <div class="loader-text" id="welcome-msg">Connecting Global Markets...</div>
        <div class="loader-track"><div class="loader-fill"></div></div>
    </div>

    <nav class="jft-navbar" id="navbar">
        <div class="jft-wide-container nav-flex">
            <a href="index.html" class="nav-logo-link"><img src="https://jftagro.com/wp-content/uploads/2023/01/jft-final-02-scaled.png" alt="JFT Agro Overseas" class="nav-logo-img"></a>
            <div class="nav-menu" id="navMenu">
                <a href="index.html" class="nav-link" onclick="toggleMenu()">Home</a>
                <a href="about.html" class="nav-link" onclick="toggleMenu()">About</a>
                <a href="products.html" class="nav-link" onclick="toggleMenu()">Products</a>
                <a href="infrastructure.html" class="nav-link" onclick="toggleMenu()">Infra</a>
                <a href="index.html#global-reach" class="nav-link" onclick="toggleMenu()">Network</a>
                <a href="contact.html" class="nav-link" onclick="toggleMenu()">Contact</a>
                <a href="contact.html" class="nav-btn-action desktop-only" onclick="toggleMenu()">Get Quote</a>
            </div>
            <div class="mobile-toggle" onclick="toggleMenu()"><i class="fa-solid fa-bars"></i></div>
        </div>
    </nav>

    <a href="https://wa.me/919800000000" class="whatsapp-float" target="_blank"><i class="fa-brands fa-whatsapp"></i></a>
    <div class="sticky-quote"><a href="contact.html" class="sticky-btn">Request Export Quote</a></div>
`;

const JFT_FOOTER = `
    <footer class="footer-section" id="contact">
        <div class="jft-wide-container">
            <div class="footer-grid">
                <div class="f-col">
                    <img src="https://jftagro.com/wp-content/uploads/2023/01/jft-final-02-scaled.png" alt="JFT Agro" style="width: 180px; filter: brightness(0) invert(1); margin-bottom: 25px;">
                    <p style="color: rgba(255,255,255,0.7); font-size: 0.95rem; margin-bottom: 25px; line-height: 1.6;">Government Recognized <strong>Star Export House</strong>. Bridging the gap between fertile Indian farms and global markets with integrity, quality, and trust.</p>
                    <div class="td-social" style="padding: 0; background: none; justify-content: flex-start;">
                        <a href="#"><i class="fa-brands fa-linkedin"></i></a>
                        <a href="#"><i class="fa-brands fa-instagram"></i></a>
                        <a href="#"><i class="fa-brands fa-twitter"></i></a>
                    </div>
                </div>

                <div class="f-col">
                    <h4>Quick Links</h4>
                    <ul class="f-links">
                        <li><a href="index.html">Home</a></li>
                        <li><a href="about.html">About Us</a></li>
                        <li><a href="products.html">Our Products</a></li>
                        <li><a href="infrastructure.html">Infrastructure</a></li>
                        <li><a href="contact.html">Contact</a></li>
                    </ul>
                </div>

                <div class="f-col">
                    <h4>Reach Us</h4>
                    <ul class="f-contact">
                        <li><i class="fa-solid fa-location-dot"></i> <span><strong>Head Office:</strong><br>123, Commodity Exchange, Sector 19, Vashi, Mumbai - 400705</span></li>
                        <li><i class="fa-solid fa-envelope"></i> <span>export@jftagro.com<br>sales@jftagro.com</span></li>
                        <li><i class="fa-solid fa-phone"></i> <span>+91 98960 55555<br>+91 22 4545 6767</span></li>
                    </ul>
                </div>

                <div class="f-col">
                    <h4>Export Inquiry</h4>
                    <p style="color: rgba(255,255,255,0.6); font-size: 0.85rem; margin-bottom: 15px;">Get our latest product catalogue and export price list directly to your inbox.</p>
                    <form class="f-newsletter" action="thank-you.html">
                        <input type="email" class="f-input" placeholder="Enter Official Email ID" required>
                        <button type="submit" class="f-btn-full">Request Price List</button>
                    </form>
                </div>
            </div>

            <div class="footer-bottom">
                <span>&copy; <script>document.write(new Date().getFullYear())</script> JFT Agro Overseas LLP. All Rights Reserved. | <a href="legal.html" style="color: var(--jft-gold);">Privacy Policy</a> | <a href="legal.html" style="color: var(--jft-gold);">Terms of Trade</a> | <a href="sitemap.html" style="color: var(--jft-gold);">Sitemap</a></span>
            </div>
        </div>
    </footer>
`;

// Inject Header and Footer if the containers exist
const headerContainer = document.getElementById('jft-header-container');
if (headerContainer) headerContainer.innerHTML = JFT_HEADER;

const footerContainer = document.getElementById('jft-footer-container');
if (footerContainer) footerContainer.innerHTML = JFT_FOOTER;

// Dispatch event to signal layout is ready so main.js can run
document.dispatchEvent(new Event('layoutLoaded'));
