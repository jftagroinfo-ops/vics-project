// footer.js

const footerHTML = `
<footer class="footer-section">
    <div class="jft-wide-container">
        <div class="footer-grid">
            
            <div class="f-col">
                <img src="https://jftagro.com/wp-content/uploads/2023/01/jft-final-02-scaled.png" alt="JFT Agro" style="width: 160px; filter: brightness(0) invert(1); margin-bottom: 25px;">
                <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; line-height: 1.6;">
                    Government Recognized <strong>Star Export House</strong>. Bridging the gap between fertile Indian farms and global markets with integrity and trust.
                </p>
                <div class="td-social" style="margin-top: 20px;">
                    <a href="#" style="color:#fff;"><i class="fa-brands fa-linkedin"></i></a>
                    <a href="#" style="color:#fff;"><i class="fa-brands fa-instagram"></i></a>
                    <a href="#" style="color:#fff;"><i class="fa-brands fa-twitter"></i></a>
                </div>
            </div>

            <div class="f-col">
                <h4>Quick Links</h4>
                <ul class="f-links">
                    <li><a href="index.html">Home</a></li>
                    <li><a href="about.html">About Us</a></li>
                    <li><a href="products.html">Our Products</a></li>
                    <li><a href="infrastructure.html">Infrastructure</a></li>
                    <li><a href="contact.html">Contact Us</a></li>
                </ul>
            </div>

            <div class="f-col">
                <h4>Reach Us</h4>
                <ul class="f-contact">
                    <li><i class="fa-solid fa-location-dot"></i> <span>123, Commodity Exchange,<br>Sector 19, Vashi, Mumbai</span></li>
                    <li><i class="fa-solid fa-envelope"></i> <span>export@jftagro.com<br>sales@jftagro.com</span></li>
                    <li><i class="fa-solid fa-phone"></i> <span>+91 98960 55555</span></li>
                </ul>
            </div>

            <div class="f-col">
                <h4>Export Inquiry</h4>
                <p style="color: rgba(255,255,255,0.6); font-size: 0.85rem; margin-bottom: 15px;">Get our latest product catalogue.</p>
                <form class="f-newsletter" onsubmit="event.preventDefault(); alert('Thank you! Export Manager will contact you.');">
                    <input type="email" class="f-input" placeholder="Enter Official Email ID" required>
                    <button type="submit" class="f-btn-full">Request Price List</button>
                </form>
            </div>

        </div>

        <div class="footer-bottom">
            <span>&copy; ${new Date().getFullYear()} JFT Agro Overseas LLP. All Rights Reserved. | <a href="#">Privacy</a> | <a href="#">Terms</a></span>
        </div>
    </div>
</footer>
`;

document.write(footerHTML);
