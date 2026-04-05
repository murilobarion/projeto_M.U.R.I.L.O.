lucide.createIcons();

gsap.registerPlugin(ScrollTrigger);

const tickerText =
    "[SYSTEM_OK] SCANNING SECTOR 7G... | DEEP SPACE NETWORK: ONLINE | NEOWISE-2 DETECTED... | WAITING FOR UPLINK...";
let charIndex = 0;

function typeWriter() {
    if (charIndex < tickerText.length) {
        document.getElementById("typewriter-ticker").innerHTML +=
            tickerText.charAt(charIndex);
        charIndex++;
        setTimeout(typeWriter, 50);
    }
}
typeWriter();

document.getElementById('data').setAttribute(
    'max',
    new Date().toISOString().split('T')[0]
);

let isFilterActive = false;

function toggleHazardous() {
    isFilterActive = !isFilterActive;
    const btn = document.getElementById('filterBtn');
    btn.innerText = `Filtro de Risco: ${isFilterActive ? 'ON' : 'OFF'}`;
    document.querySelectorAll('.asteroid-row').forEach(row => {
        row.classList.toggle(
            'hidden-row',
            isFilterActive && row.dataset.hazardous === 'false'
        );
    });
}

const labelsEl = document.getElementById('data-labels');
if (labelsEl) {
    const chartLabels = JSON.parse(labelsEl.textContent);
    const chartSizes  = JSON.parse(document.getElementById('data-sizes').textContent);
    const ctx         = document.getElementById('sizeChart').getContext('2d');

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartLabels,
            datasets: [{
                label: 'Diâmetro (m)',
                data: chartSizes,
                backgroundColor: 'rgba(56, 189, 248, 0.4)',
                borderColor: '#38bdf8',
                borderWidth: 1,
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    grid:  { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#64748b' }
                },
                x: {
                    grid:  { display: false },
                    ticks: { color: '#64748b', font: { size: 9 } }
                }
            }
        }
    });

    setTimeout(() => {
        document.querySelector('.dashboard-section')
            .scrollIntoView({ behavior: 'smooth' });
    }, 500);
}

gsap.from(".hero-content > *", {
    y: 30, opacity: 0, duration: 1, stagger: 0.2, ease: "power3.out"
});

gsap.utils.toArray('.gs-reveal').forEach(elem => {
    ScrollTrigger.create({
        trigger: elem,
        start: "top 85%",
        once: true,
        onEnter() {
            gsap.fromTo(
                elem,
                { y: 50, opacity: 0 },
                { duration: 0.8, y: 0, opacity: 1, ease: "power3.out", overwrite: "auto" }
            );
        }
    });
});

document.querySelectorAll('.glass-panel').forEach(card => {
    card.addEventListener('mousemove', e => {
        const rect = card.getBoundingClientRect();
        card.style.background =
            `radial-gradient(circle at ${e.clientX - rect.left}px ${e.clientY - rect.top}px,
             rgba(56,189,248,0.1) 0%, rgba(15, 23, 42, 0.7) 50%)`;
    });
    card.addEventListener('mouseleave', () => {
        card.style.background = 'rgba(15, 23, 42, 0.7)';
    });
});

const quakeSection = document.querySelector('.quake-section');
if (quakeSection) {
    console.log("%c[ASTROQUAKE] Sismógrafos online. Buscando correlações caóticas... ✓", "color: #f97316; font-weight: bold; background: #2a1205; padding: 4px; border-radius: 4px;");

    gsap.to("#icone-sismico", {
        scale: 1.15,
        opacity: 0.7,
        duration: 0.6,
        repeat: -1,
        yoyo: true,
        ease: "power1.inOut"
    });
}