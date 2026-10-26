/* =========================================================
   STHALA PURANA — MAIN.JS (ORCHIDS AI VERSION)
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    /* =====================================================
       ACTIVE NAVBAR LINK
    ===================================================== */

    const navLinks = document.querySelectorAll(".nav-links a");

    navLinks.forEach(link => {

        if (link.href === window.location.href) {
            link.classList.add("active");
        }
    });

    /* =====================================================
       HERO PARTICLES
    ===================================================== */

    const particlesContainer = document.getElementById("particles");

    if (particlesContainer) {

        for (let i = 0; i < 45; i++) {

            const particle = document.createElement("span");

            particle.classList.add("particle");

            const size = Math.random() * 6 + 2;

            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;

            particle.style.left = `${Math.random() * 100}%`;

            particle.style.animationDuration =
                `${Math.random() * 10 + 8}s`;

            particle.style.animationDelay =
                `${Math.random() * 5}s`;

            particle.style.opacity =
                Math.random() * 0.5 + 0.2;

            particlesContainer.appendChild(particle);
        }
    }

    /* =====================================================
       SCROLL REVEAL ANIMATION
    ===================================================== */

    const revealItems = document.querySelectorAll(`
        .category-card,
        .temple-card,
        .feature-item,
        .about-section,
        .about-hero-stat,
        .contact-card,
        .reset-card,
        .error-card
    `);

    const revealOnScroll = () => {

        const triggerBottom = window.innerHeight * 0.88;

        revealItems.forEach(item => {

            const rect = item.getBoundingClientRect();

            if (rect.top < triggerBottom) {
                item.classList.add("show");
            }
        });
    };

    window.addEventListener("scroll", revealOnScroll);

    revealOnScroll();

    /* =====================================================
       SMOOTH SCROLL
    ===================================================== */

    const smoothLinks = document.querySelectorAll('a[href^="#"]');

    smoothLinks.forEach(link => {

        link.addEventListener("click", e => {

            const targetId = link.getAttribute("href");

            if (targetId.length > 1) {

                e.preventDefault();

                const target =
                    document.querySelector(targetId);

                if (target) {

                    target.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });
                }
            }
        });
    });

    /* =====================================================
       COUNTER ANIMATION
    ===================================================== */

    const counters = document.querySelectorAll(".stat-num, .stat-big");

    const animateCounter = (counter) => {

        const text = counter.innerText.trim();

        if (text.includes("∞")) return;

        const target =
            parseInt(text.replace(/\D/g, ""));

        if (isNaN(target)) return;

        let count = 0;

        const speed = Math.ceil(target / 60);

        const updateCounter = () => {

            count += speed;

            if (count >= target) {

                counter.innerText =
                    text.includes("+")
                    ? `${target}+`
                    : target;

            } else {

                counter.innerText = count;

                requestAnimationFrame(updateCounter);
            }
        };

        updateCounter();
    };

    counters.forEach(counter => {

        animateCounter(counter);
    });

    /* =====================================================
       TEMPLE CARD MOUSE GLOW
    ===================================================== */

    const templeCards =
        document.querySelectorAll(".temple-card");

    templeCards.forEach(card => {

        card.addEventListener("mousemove", e => {

            const rect = card.getBoundingClientRect();

            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            card.style.setProperty("--x", `${x}px`);
            card.style.setProperty("--y", `${y}px`);
        });
    });

    /* =====================================================
       BACK TO TOP BUTTON
    ===================================================== */

    const topBtn = document.createElement("button");

    topBtn.className = "back-to-top";

    topBtn.innerHTML =
        '<i class="fas fa-chevron-up"></i>';

    document.body.appendChild(topBtn);

    window.addEventListener("scroll", () => {

        if (window.scrollY > 500) {

            topBtn.classList.add("visible");

        } else {

            topBtn.classList.remove("visible");
        }
    });

    topBtn.addEventListener("click", () => {

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    });

    /* =====================================================
       MOBILE MENU
    ===================================================== */

    const navInner =
        document.querySelector(".nav-inner");

    const navLinksContainer =
        document.querySelector(".nav-links");

    if (navInner && navLinksContainer) {

        const mobileBtn =
            document.createElement("button");

        mobileBtn.className = "mobile-menu-btn";

        mobileBtn.innerHTML =
            '<i class="fas fa-bars"></i>';

        navInner.appendChild(mobileBtn);

        mobileBtn.addEventListener("click", () => {

            navLinksContainer.classList.toggle(
                "mobile-active"
            );

            if (
                navLinksContainer.classList.contains(
                    "mobile-active"
                )
            ) {

                mobileBtn.innerHTML =
                    '<i class="fas fa-times"></i>';

            } else {

                mobileBtn.innerHTML =
                    '<i class="fas fa-bars"></i>';
            }
        });
    }

    /* =====================================================
       FLASH AUTO HIDE
    ===================================================== */

    const flashMessages =
        document.querySelectorAll(".flash");

    flashMessages.forEach(flash => {

        setTimeout(() => {

            flash.style.opacity = "0";

            flash.style.transform =
                "translateY(-10px)";

            setTimeout(() => {

                flash.remove();

            }, 400);

        }, 4500);
    });

    /* =====================================================
       LOADING EFFECT
    ===================================================== */

    window.addEventListener("load", () => {

        document.body.classList.add("loaded");
    });

});


/* =========================================================
   EXTRA STYLES INJECTED VIA JS
========================================================= */

const style = document.createElement("style");

style.innerHTML = `

/* =====================================================
   REVEAL ANIMATION
===================================================== */

.category-card,
.temple-card,
.feature-item,
.about-section,
.about-hero-stat,
.contact-card,
.reset-card,
.error-card{

    opacity:0;
    transform:translateY(40px);
    transition:all .8s ease;
}

.category-card.show,
.temple-card.show,
.feature-item.show,
.about-section.show,
.about-hero-stat.show,
.contact-card.show,
.reset-card.show,
.error-card.show{

    opacity:1;
    transform:translateY(0);
}

/* =====================================================
   HERO PARTICLES
===================================================== */

.hero-particles{
    position:absolute;
    inset:0;
    overflow:hidden;
    z-index:1;
}

.particle{
    position:absolute;
    bottom:-20px;
    border-radius:50%;

    background:rgba(255,255,255,.25);

    animation:floatParticle linear infinite;
}

@keyframes floatParticle{

    from{
        transform:translateY(0);
        opacity:0;
    }

    10%{
        opacity:1;
    }

    to{
        transform:translateY(-120vh);
        opacity:0;
    }
}

/* =====================================================
   BACK TO TOP BUTTON
===================================================== */

.back-to-top{

    position:fixed;

    right:24px;
    bottom:24px;

    width:52px;
    height:52px;

    border:none;

    border-radius:50%;

    background:
        linear-gradient(
            135deg,
            #E8500A,
            #F5C842
        );

    color:white;

    font-size:1rem;

    cursor:pointer;

    z-index:999;

    opacity:0;
    visibility:hidden;

    transition:.3s ease;

    box-shadow:0 10px 25px rgba(0,0,0,.2);
}

.back-to-top.visible{

    opacity:1;
    visibility:visible;
}

.back-to-top:hover{

    transform:translateY(-4px);
}

/* =====================================================
   MOBILE MENU
===================================================== */

.mobile-menu-btn{

    display:none;

    background:transparent;

    border:none;

    color:white;

    font-size:1.4rem;

    margin-left:auto;

    cursor:pointer;
}

@media(max-width:768px){

    .mobile-menu-btn{
        display:block;
    }

    .nav-links{

        position:absolute;

        top:70px;
        left:0;

        width:100%;

        background:#2C2416;

        flex-direction:column;

        padding:1rem;

        display:none;

        border-top:
            1px solid rgba(255,255,255,.08);
    }

    .nav-links.mobile-active{
        display:flex;
    }

    .nav-links a{

        width:100%;

        padding:.9rem 1rem;
    }
}

/* =====================================================
   ACTIVE NAV LINK
===================================================== */

.nav-links a.active{

    color:#F5C842 !important;
}

/* =====================================================
   TEMPLE CARD GLOW EFFECT
===================================================== */

.temple-card{

    position:relative;
}

.temple-card::before{

    content:'';

    position:absolute;
    inset:0;

    background:
        radial-gradient(
            circle at var(--x) var(--y),
            rgba(255,255,255,.16),
            transparent 30%
        );

    opacity:0;

    transition:opacity .3s;

    pointer-events:none;
}

.temple-card:hover::before{
    opacity:1;
}

`;

document.head.appendChild(style);