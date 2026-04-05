/* ============================================================
   Projeto M.U.R.I.L.O. — Script principal
   Dependências (carregadas via CDN no HTML antes deste arquivo):
     - GSAP 3.12.2 + ScrollTrigger
     - Lucide
     - Chart.js
   ============================================================ */

/* ── Inicialização de ícones Lucide ── */
lucide.createIcons();

/* ── Registro do plugin GSAP ── */
gsap.registerPlugin(ScrollTrigger);

/* ── Typewriter no ticker ── */
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

/* ── Limita o campo de data ao dia de hoje ── */
document.getElementById('data').setAttribute(
    'max',
    new Date().toISOString().split('T')[0]
);

/* ── Filtro de risco (botão Radar) ── */
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

/* ── Gráfico de barras (só renderiza quando há dados) ── */
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

    /* Rola suavemente para o dashboard após a busca */
    setTimeout(() => {
        document.querySelector('.dashboard-section')
                .scrollIntoView({ behavior: 'smooth' });
    }, 500);
}

/* ── Animações GSAP de entrada ── */
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

/* ── Efeito de luz radial ao passar o mouse nas glass panels ── */
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
