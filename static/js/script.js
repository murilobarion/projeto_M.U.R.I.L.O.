lucide.createIcons();
gsap.registerPlugin(ScrollTrigger);

const tickerText = "[SYSTEM_OK] SCANNING SECTOR 7G... | DEEP SPACE NETWORK: ONLINE | NEOWISE-2 DETECTED... | WAITING FOR UPLINK...";
let charIndex = 0;

function typeWriter() {
    if (charIndex < tickerText.length) {
        document.getElementById("typewriter-ticker").innerHTML += tickerText.charAt(charIndex);
        charIndex++;
        setTimeout(typeWriter, 50);
    }
}
typeWriter();

document.getElementById('data').setAttribute('max', new Date().toISOString().split('T')[0]);

let isFilterActive = false;
function toggleHazardous() {
    isFilterActive = !isFilterActive;
    const btn = document.getElementById('filterBtn');
    btn.innerText = `Filtro de Risco: ${isFilterActive ? 'ON' : 'OFF'}`;
    document.querySelectorAll('.asteroid-row').forEach(row => {
        row.classList.toggle('hidden-row', isFilterActive && row.dataset.hazardous === 'false');
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
                y: { grid:  { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#64748b' } },
                x: { grid:  { display: false }, ticks: { color: '#64748b', font: { size: 9 } } }
            }
        }
    });

    setTimeout(() => {
        document.querySelector('.dashboard-section').scrollIntoView({ behavior: 'smooth' });
    }, 500);
}

gsap.from(".hero-content > *", { y: 30, opacity: 0, duration: 1, stagger: 0.2, ease: "power3.out" });

gsap.utils.toArray('.gs-reveal').forEach(elem => {
    ScrollTrigger.create({
        trigger: elem,
        start: "top 85%",
        once: true,
        onEnter() {
            gsap.fromTo(elem, { y: 50, opacity: 0 }, { duration: 0.8, y: 0, opacity: 1, ease: "power3.out", overwrite: "auto" });
        }
    });
});

document.querySelectorAll('.glass-panel').forEach(card => {
    card.addEventListener('mousemove', e => {
        const rect = card.getBoundingClientRect();
        card.style.background = `radial-gradient(circle at ${e.clientX - rect.left}px ${e.clientY - rect.top}px, rgba(56,189,248,0.1) 0%, rgba(15, 23, 42, 0.7) 50%)`;
    });
    card.addEventListener('mouseleave', () => { card.style.background = 'rgba(15, 23, 42, 0.7)'; });
});

const quakeSection = document.querySelector('.quake-section');
if (quakeSection) {
    console.log("%c[ASTROQUAKE] Sismógrafos online. Buscando correlações caóticas... ✓", "color: #f97316; font-weight: bold; background: #2a1205; padding: 4px; border-radius: 4px;");
    gsap.to("#icone-sismico", { scale: 1.15, opacity: 0.7, duration: 0.6, repeat: -1, yoyo: true, ease: "power1.inOut" });
}

function createAsteroidLabel(text) {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = 256;
    canvas.height = 64;

    context.clearRect(0, 0, canvas.width, canvas.height);

    context.font = "Bold 24px 'JetBrains Mono', monospace";
    context.fillStyle = "#38bdf8"; 
    context.textAlign = "center";
    context.fillText(text, 128, 40);

    const texture = new THREE.CanvasTexture(canvas);
    const spriteMaterial = new THREE.SpriteMaterial({ map: texture, transparent: true });
    const sprite = new THREE.Sprite(spriteMaterial);

    sprite.scale.set(12, 3, 1); 
    return sprite;
}

function initOrbitalViewer() {
    const container = document.getElementById('canvas-container');
    if (!container) return;

    const asteroidsDataEl = document.getElementById('data-3d-asteroids');
    let asteroids3D = [];
    if (asteroidsDataEl) {
        try { asteroids3D = JSON.parse(asteroidsDataEl.textContent); } 
        catch (e) { console.error("Erro ao ler dados 3D:", e); }
    }

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.domElement.style.margin = "0 auto";
    renderer.domElement.style.cursor = "grab";
    container.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true; 
    controls.dampingFactor = 0.05;
    controls.enableZoom = true;    
    controls.enablePan = false;    
    controls.autoRotate = true;    
    controls.autoRotateSpeed = 0.5;
    controls.minDistance = 40;
    controls.maxDistance = 570;

    const earthGeometry = new THREE.SphereGeometry(30, 32, 32);
    const earthMaterial = new THREE.MeshBasicMaterial({ color: 0x38bdf8, wireframe: true, transparent: true, opacity: 0.4 });
    const earth = new THREE.Mesh(earthGeometry, earthMaterial);
    scene.add(earth);
    const debrisCount = 2500;
    const debrisGeom = new THREE.BufferGeometry();
    const debrisPoss = new Float32Array(debrisCount * 3);
    for(let i=0; i<debrisCount*3; i+=3) {
        const r = 30.5 + Math.random() * 2.5; 
        const theta = Math.random() * 2 * Math.PI;
        const phi = Math.acos(Math.random() * 2 - 1);
        debrisPoss[i] = r * Math.sin(phi) * Math.cos(theta);
        debrisPoss[i+1] = r * Math.sin(phi) * Math.sin(theta);
        debrisPoss[i+2] = r * Math.cos(phi);
    }

    debrisGeom.setAttribute('position', new THREE.BufferAttribute(debrisPoss, 3));
    const debrisMat = new THREE.PointsMaterial({ color: 0xff003c, size: 0.15, transparent: true, opacity: 0.8 });
    const debrisSystem = new THREE.Points(debrisGeom, debrisMat);
    scene.add(debrisSystem);

    const orbitalGroup = new THREE.Group();
    scene.add(orbitalGroup);

    const orbitColor = 0x818cf8; 
    const asteroideColor = 0xc084fc; 
    const pivots = [];

    let mouseX = 0, mouseY = 0;

    asteroids3D.forEach((astData, index) => {
        const radius = (astData.radius_km.m_km * 3.0) + 45;

        const astSystem = new THREE.Group();
        astSystem.rotation.x = Math.random() * Math.PI;
        astSystem.rotation.y = Math.random() * Math.PI;

        const orbitGeom = new THREE.RingGeometry(radius, radius + 0.04, 128);
        const orbitMat = new THREE.MeshBasicMaterial({ 
            color: 0xa8b1ff,
            side: THREE.DoubleSide, 
            transparent: true, 
            opacity: 0.65
        });

        const orbitMesh = new THREE.Mesh(orbitGeom, orbitMat);

        orbitMesh.rotation.x = Math.PI / 2;
        astSystem.add(orbitMesh);

        const pivot = new THREE.Group();
        pivot.rotation.y = Math.random() * Math.PI * 2;
        pivot.userData.speed = 0.001 + (Math.random() * 0.002);
        astSystem.add(pivot);

        let rawScale = (astData.diameter / 1000.0) * 1.5; 
        let minChecked = Math.max(rawScale, 0.4);
        const scaledRadius = Math.min(minChecked, 3.0);
        const astGeometry = new THREE.SphereGeometry(scaledRadius, 16, 16);
        const astMaterial = new THREE.MeshLambertMaterial({ 
            color: asteroideColor,
            emissive: asteroideColor,
            emissiveIntensity: 0.2
        });
        const astPoint = new THREE.Mesh(astGeometry, astMaterial);
        const label = createAsteroidLabel(astData.name);
        label.position.set(0, scaledRadius + 1.5, 0); 
        astPoint.add(label);

        astPoint.position.set(radius, 0, 0);
        pivot.add(astPoint); 

        pivots.push(pivot); 
        orbitalGroup.add(astSystem);
    });


    const ambientLight = new THREE.AmbientLight(0x404040, 3); 
    scene.add(ambientLight);

    camera.position.set(0, 120, 250);

    renderer.domElement.addEventListener('mousedown', () => renderer.domElement.style.cursor = "grabbing");
    renderer.domElement.addEventListener('mouseup', () => renderer.domElement.style.cursor = "grab");

    window.addEventListener('resize', () => {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    });

    function animate() {
        requestAnimationFrame(animate);
        earth.rotation.y += 0.003;

        if(typeof debrisSystem !== 'undefined') {
            debrisSystem.rotation.y += 0.002;
            debrisSystem.rotation.x += 0.0005;
        }
        
        pivots.forEach(pivot => {
            pivot.rotation.y += pivot.userData.speed; 
        });

        controls.update();
        renderer.render(scene, camera);
    }

    animate();
}

function scrambleEffect(element) {
    const originalValue = element.dataset.value;
    const chars = "!<>-_\\/[]{}—=+*^?#________";
    let iteration = 0;
    const interval = setInterval(() => {
        element.innerText = originalValue.split("").map((char, index) => {
            if(index < iteration) return originalValue[index];
            return chars[Math.floor(Math.random() * chars.length)];
        }).join("");
        if(iteration >= originalValue.length) clearInterval(interval);
        iteration += 1 / 3;
    }, 30);
}

function generateDossier() {
    const modal = document.getElementById('dossier-template');
    const content = document.getElementById('dossier-content');
    modal.classList.remove('hidden');
    
    const dangerousRows = document.querySelectorAll('.asteroid-row[data-hazardous="true"]');
    let html = "<p>NENHUMA AMEAÇA IMINENTE DETECTADA NESTA DATA.</p>";
    
    if(dangerousRows.length > 0) {
        html = `<p class='text-red-600 font-bold font-terminal'>AVISO: ${dangerousRows.length} OBJETOS DE ALTO RISCO IDENTIFICADOS.</p><ul class='list-disc pl-5 font-tactical'>`;
        dangerousRows.forEach(row => {
            const name = row.querySelector('.font-apple').innerText;
            const size = row.querySelectorAll('.font-mono-data')[1].innerText;
            html += `<li class='mb-2'>OBJETO: ${name} | DIÂMETRO EST.: ${size} - Escala de Impacto Crítica.</li>`;
        });
        html += "</ul>";
    }
    content.innerHTML = html;
}

function simularImpacto() {
    const btn = document.getElementById('btn-cratera');
    btn.innerHTML = `<i data-lucide="loader" class="w-4 h-4 animate-spin"></i> Hackeando Satélites...`;
    if (typeof lucide !== 'undefined') lucide.createIcons();
    
    setTimeout(() => {
        const asteroidsDataEl = document.getElementById('data-3d-asteroids');
        let maiorDiametro = 100; // Padrão caso dê erro
        if (asteroidsDataEl) {
            const asteroids = JSON.parse(asteroidsDataEl.textContent);
            if (asteroids.length > 0) {
                maiorDiametro = Math.max(...asteroids.map(a => a.diameter));
            }
        }
        
        // 1. Lista de 12 clássicos de filmes de alien/meteoro nos EUA
        const locations = [
            "KANSAS CITY, KANSAS",
            "OMAHA, NEBRASKA",
            "OKLAHOMA CITY, OKLAHOMA",
            "ROSWELL, NEW MEXICO",
            "DALLAS, TEXAS",
            "DENVER, COLORADO",
            "CHEYENNE, WYOMING",
            "SALT LAKE CITY, UTAH",
            "WICHITA, KANSAS",
            "SIOUX FALLS, SOUTH DAKOTA",
            "ÁREA 51, NEVADA",
            "DES MOINES, IOWA"
        ];

        const randomLocation = locations[Math.floor(Math.random() * locations.length)];

        const crateraKm = (maiorDiametro * 0.05).toFixed(1); 
        const blastRadius = (crateraKm * 3.5).toFixed(1); 
        const quakeMag = (Math.log10(maiorDiametro) * 3.2).toFixed(1); 

        const casualties = Math.floor(maiorDiametro * 1850).toLocaleString('pt-BR');

        document.getElementById('crater-location').innerText = randomLocation;
        document.getElementById('crater-obj-size').innerText = maiorDiametro.toFixed(1) + " metros";
        document.getElementById('crater-size').innerText = crateraKm + " km";
        document.getElementById('crater-blast').innerText = blastRadius + " km de cinzas";
        document.getElementById('crater-quake').innerText = quakeMag + " Richter";
        document.getElementById('crater-casualties').innerText = casualties + " almas";

        document.getElementById('custom-crater-modal').classList.remove('hidden');
        btn.innerHTML = `<i data-lucide="map-pin" class="w-4 h-4"></i> Calcular Estrago Local`;
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }, 1500);
}

function gerarContratoMineracao() {
    const asteroidesData = document.getElementById('data-3d-asteroids');
    let valorTrilhoes = (Math.random() * 90 + 10).toFixed(2); 
    let nomeMina = "Asteroid-X";
    
    if (asteroidesData) {
        const asteroids = JSON.parse(asteroidesData.textContent);
        if (asteroids.length > 0) {
            nomeMina = asteroids[0].name;
            valorTrilhoes = ((asteroids[0].diameter * 100) / 1000).toFixed(2);
        }
    }

    document.getElementById('mine-target').innerText = nomeMina;
    document.getElementById('mine-value').innerText = "$" + valorTrilhoes + " Trilhões de Dólares";

    document.getElementById('custom-mining-modal').classList.remove('hidden');
}

function closeDossierAndShowAlert() {
    document.getElementById('dossier-template').classList.add('hidden');
    document.getElementById('custom-alert-modal').classList.remove('hidden');

    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
        }
    }

function closeCustomAlert() {
    document.getElementById('custom-alert-modal').classList.add('hidden');
    }

document.addEventListener('DOMContentLoaded', () => {
    initOrbitalViewer();
    document.querySelectorAll('.scramble-text').forEach(scrambleEffect);
});