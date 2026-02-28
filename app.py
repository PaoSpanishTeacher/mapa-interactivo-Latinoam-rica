import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Mapa Interactivo Latinoamérica", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0rem; }
    iframe { border: none; }
    </style>
    """, unsafe_allow_html=True)

html_mapa_latam = r"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mapa Interactivo - América Latina</title>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600&family=Quicksand:wght@500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #ff4757;
            --secondary: #2f3542;
            --success: #2ed573;
            --bg: #f0f2f5;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }

        body {
            font-family: 'Quicksand', sans-serif;
            background: #fff9e6;
            background-image: radial-gradient(#ff475711 2px, transparent 2px);
            background-size: 30px 30px;
            display: flex; flex-direction: column; align-items: center;
            min-height: 100vh; overflow-x: hidden;
            padding: 20px;
        }

        header { text-align: center; margin-bottom: 20px; }
        h1 { font-family: 'Fredoka', sans-serif; color: #d35400; font-size: 2.5rem; text-shadow: 2px 2px white; }
        .brand { color: #2d6a4f; font-weight: bold; font-size: 1.2rem; }

        .game-container {
            display: grid; grid-template-columns: 250px 1fr;
            gap: 20px; width: 95%; max-width: 1200px;
            background: rgba(255,255,255,0.8); padding: 20px;
            border-radius: 30px; box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px); border: 5px solid #fff;
        }

        /* Panel de Países */
        .countries-panel {
            display: flex; flex-direction: column; gap: 8px;
            max-height: 700px; overflow-y: auto; padding-right: 10px;
        }
        .country-tag {
            background: white; border: 2px solid #e0e0e0;
            padding: 10px 15px; border-radius: 12px;
            cursor: grab; font-weight: 700; color: #444;
            transition: 0.2s; text-align: center;
            box-shadow: 0 4px 0 #ddd;
        }
        .country-tag:active { cursor: grabbing; transform: translateY(2px); box-shadow: none; }
        .country-tag.placed { opacity: 0; pointer-events: none; }

        /* Mapa SVG */
        .map-wrapper {
            position: relative; display: flex; justify-content: center; align-items: center;
            background: #e3f2fd; border-radius: 20px; border: 3px solid #bbdefb;
            padding: 10px; min-height: 600px;
        }
        svg { width: 100%; height: auto; max-height: 750px; filter: drop-shadow(0 5px 15px rgba(0,0,0,0.1)); }
        
        path {
            fill: #ffffff; stroke: #666; stroke-width: 0.8;
            transition: 0.3s; cursor: pointer;
        }
        path.highlight { fill: #fffde7; stroke-width: 2; stroke: #ff4757; }
        path.correct { fill: var(--success) !important; stroke: #1b5e20; stroke-width: 1; }

        /* Mensajes Pop-up */
        #status-msg {
            position: fixed; top: 100px; left: 50%; transform: translateX(-50%) scale(0);
            padding: 20px 50px; border-radius: 50px; color: white;
            font-size: 2.5rem; font-weight: 900; z-index: 1000;
            transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            font-family: 'Fredoka', sans-serif; pointer-events: none;
        }
        #status-msg.show { transform: translateX(-50%) scale(1); }

        /* Pantalla Final */
        #final-overlay {
            position: fixed; inset: 0; background: rgba(255,255,255,0.98);
            z-index: 2000; display: none; flex-direction: column;
            justify-content: center; align-items: center; text-align: center;
        }
        #final-overlay.active { display: flex; animation: fadeIn 0.5s; }

        .dancers { font-size: 100px; display: flex; gap: 50px; margin: 20px 0; }
        .dancer { animation: dance 0.6s infinite alternate ease-in-out; }
        @keyframes dance { from { transform: translateY(0) rotate(-5deg); } to { transform: translateY(-20px) rotate(5deg); } }

        .btn-restart {
            background: #ff4757; color: white; border: none;
            padding: 15px 40px; border-radius: 50px; font-size: 1.5rem;
            cursor: pointer; margin-top: 20px; font-weight: bold;
            box-shadow: 0 6px 0 #b33939;
        }

        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    </style>
</head>
<body>

    <header>
        <h1>Mapa Interactivo - América Latina</h1>
        <div class="brand">PaoSpanishTeacher</div>
    </header>

    <div class="game-container">
        <div class="countries-panel" id="external-list">
            </div>

        <div class="map-wrapper" id="drop-area">
            <svg id="latam-svg" viewBox="250 50 600 900" xmlns="http://www.w3.org/2000/svg">
                <path id="México" d="M305,252 L315,245 L346,243 L377,262 L411,310 L448,318 L460,344 L440,366 L400,345 L350,340 L310,290 Z" />
                <path id="Guatemala" d="M465,350 L480,350 L485,365 L470,375 Z" />
                <path id="Honduras" d="M485,355 L510,355 L510,370 L490,375 Z" />
                <path id="El Salvador" d="M485,378 L498,378 L495,385 L485,385 Z" />
                <path id="Nicaragua" d="M505,375 L525,385 L520,405 L500,400 Z" />
                <path id="Costa Rica" d="M520,410 L535,420 L528,430 L515,425 Z" />
                <path id="Panamá" d="M540,425 L565,425 L570,435 L545,445 Z" />
                <path id="Cuba" d="M460,280 L520,295 L515,305 L460,290 Z" />
                <path id="República Dominicana" d="M560,305 L590,305 L590,315 L560,315 Z" />
                <path id="Colombia" d="M575,445 L625,455 L630,510 L590,520 L570,480 Z" />
                <path id="Venezuela" d="M630,445 L700,455 L705,495 L635,505 Z" />
                <path id="Ecuador" d="M575,525 L610,525 L605,555 L580,555 Z" />
                <path id="Perú" d="M585,565 L660,565 L690,670 L640,700 L590,620 Z" />
                <path id="Bolivia" d="M680,630 L745,645 L755,715 L705,735 L675,690 Z" />
                <path id="Paraguay" d="M755,730 L800,740 L805,785 L760,795 Z" />
                <path id="Chile" d="M675,745 L705,745 L740,950 L720,955 Z" />
                <path id="Argentina" d="M710,750 L755,735 L810,790 L815,950 L745,950 Z" />
                <path id="Uruguay" d="M815,795 L845,805 L840,830 L815,825 Z" />
                <path id="Brasil" d="M650,515 L710,465 L810,500 L880,620 L860,780 L760,720 L665,630 Z" />
            </svg>
        </div>
    </div>

    <div id="status-msg"></div>

    <div id="final-overlay">
        <h1>¡Excelente! Sigue aprendiendo español.</h1>
        <div class="dancers">
            <span class="dancer">💃</span>
            <span class="dancer">🕺</span>
        </div>
        <p style="font-size: 1.5rem; color: #d35400;">¡Dominas la geografía de Latinoamérica!</p>
        <button class="btn-restart" onclick="location.reload()">Jugar otra vez</button>
    </div>

    <audio id="snd-success" src="https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3"></audio>
    <audio id="snd-error" src="https://assets.mixkit.co/active_storage/sfx/2571/2571-preview.mp3"></audio>
    <audio id="snd-party" src="https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3" loop></audio>

    <script>
        const countries = [
            "México", "Guatemala", "Honduras", "El Salvador", "Nicaragua", 
            "Costa Rica", "Panamá", "Cuba", "República Dominicana", "Colombia", 
            "Venezuela", "Ecuador", "Perú", "Bolivia", "Chile", "Argentina", 
            "Paraguay", "Uruguay", "Brasil"
        ];

        let completed = 0;
        let draggedName = null;

        function init() {
            const list = document.getElementById('external-list');
            const shuffled = [...countries].sort(() => Math.random() - 0.5);

            shuffled.forEach(c => {
                const div = document.createElement('div');
                div.className = 'country-tag';
                div.textContent = c;
                div.draggable = true;
                div.id = 'tag-' + c;
                div.addEventListener('dragstart', (e) => {
                    draggedName = c;
                    e.dataTransfer.setData('text', c);
                });
                list.appendChild(div);
            });

            // Configurar interactividad del mapa
            document.querySelectorAll('path').forEach(p => {
                p.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    if (!p.classList.contains('correct')) p.classList.add('highlight');
                });

                p.addEventListener('dragleave', () => {
                    p.classList.remove('highlight');
                });

                p.addEventListener('drop', (e) => {
                    e.preventDefault();
                    p.classList.remove('highlight');
                    const droppedOn = p.id;
                    handleDrop(droppedOn, p);
                });
            });
        }

        function handleDrop(targetId, element) {
            if (draggedName === targetId) {
                // ACIERTO
                element.classList.add('correct');
                document.getElementById('tag-' + draggedName).classList.add('placed');
                document.getElementById('snd-success').play();
                showPopup("¡Excelente!", "#2ed573");
                completed++;
                
                if (completed === countries.length) showFinal();
            } else {
                // ERROR
                document.getElementById('snd-error').play();
                showPopup("Intenta otra vez", "#ff4757");
            }
        }

        function showPopup(txt, color) {
            const m = document.getElementById('status-msg');
            m.textContent = txt;
            m.style.background = color;
            m.classList.add('show');
            setTimeout(() => m.classList.remove('show'), 1000);
        }

        function showFinal() {
            document.getElementById('snd-party').play();
            document.getElementById('final-overlay').classList.add('active');
            confetti({
                particleCount: 200,
                spread: 100,
                origin: { y: 0.6 }
            });
            // Globos
            for(let i=0; i<15; i++) {
                setTimeout(createBalloon, i * 200);
            }
        }

        function createBalloon() {
            const b = document.createElement('div');
            b.style.position = 'fixed';
            b.style.bottom = '-50px';
            b.style.left = Math.random() * 100 + 'vw';
            b.style.fontSize = '3rem';
            b.textContent = '🎈';
            b.style.transition = 'transform 6s linear';
            b.style.zIndex = '2001';
            document.body.appendChild(b);
            setTimeout(() => b.style.transform = 'translateY(-120vh)', 50);
            setTimeout(() => b.remove(), 6000);
        }

        init();
    </script>
</body>
</html>
"""

components.html(html_mapa_latam, height=900, scrolling=False)
