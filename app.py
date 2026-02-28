import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Mapa LATAM Interactivo", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0rem; }
    iframe { border: none; }
    </style>
    """, unsafe_allow_html=True)

html_mapa_real = r"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@600&family=Quicksand:wght@500;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
        body {
            font-family: 'Quicksand', sans-serif;
            background: #e0f7fa;
            padding-top: 100px; /* Evita que el título se corte */
            display: flex; flex-direction: column; align-items: center;
            min-height: 100vh;
        }
        header { text-align: center; margin-bottom: 20px; }
        h1 { font-family: 'Fredoka', sans-serif; color: #00695c; font-size: 2.8rem; text-shadow: 2px 2px white; }
        
        .game-layout {
            display: grid; grid-template-columns: 260px 1fr;
            gap: 20px; width: 95%; max-width: 1100px;
            background: white; padding: 25px; border-radius: 25px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        }

        .sidebar {
            display: flex; flex-direction: column; gap: 8px;
            max-height: 650px; overflow-y: auto; padding: 10px;
            background: #f1f8e9; border-radius: 15px;
        }
        .country-chip {
            background: #ff7043; color: white; padding: 10px;
            border-radius: 10px; cursor: grab; text-align: center;
            font-weight: bold; box-shadow: 0 4px 0 #d84315; transition: 0.2s;
        }
        .country-chip:active { transform: translateY(3px); box-shadow: none; }
        .country-chip.hidden { opacity: 0; pointer-events: none; }

        .map-area {
            background: #bbdefb; border-radius: 20px;
            position: relative; display: flex; justify-content: center; align-items: center;
            border: 4px solid white;
        }
        svg { width: 100%; height: auto; max-height: 700px; }
        
        /* Estilo real para los países */
        path { fill: #f5f5f5; stroke: #455a64; stroke-width: 0.5; transition: 0.3s; cursor: pointer; }
        path:hover { fill: #fff9c4; }
        path.correct { fill: #4caf50 !important; stroke: #1b5e20; stroke-width: 1; }

        #alert {
            position: fixed; top: 150px; left: 50%; transform: translateX(-50%) scale(0);
            padding: 15px 40px; border-radius: 50px; color: white;
            font-size: 2rem; font-weight: bold; z-index: 1000;
            transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        #alert.show { transform: translateX(-50%) scale(1); }

        /* Final con Cumbia */
        #final-screen {
            position: fixed; inset: 0; background: rgba(255,255,255,0.95);
            display: none; flex-direction: column; align-items: center; justify-content: center;
            z-index: 2000; text-align: center;
        }
        #final-screen.active { display: flex; }
        .dancer-container { display: flex; gap: 50px; margin: 30px; }
        .dancer { font-size: 7rem; animation: jump 0.5s infinite alternate; }
        @keyframes jump { from { transform: translateY(0); } to { transform: translateY(-30px); } }
        
        .restart-btn {
            background: #00c853; color: white; border: none; padding: 20px 40px;
            font-size: 1.8rem; border-radius: 50px; cursor: pointer; font-family: 'Fredoka';
        }
    </style>
</head>
<body>

    <header>
        <h1>Mapa Interactivo - América Latina</h1>
        <p style="color: #00796b; font-weight: bold;">Pau Spanish Teacher</p>
    </header>

    <div class="game-layout">
        <div class="sidebar" id="list"></div>
        <div class="map-area">
            <svg viewBox="0 0 1000 1200" xmlns="http://www.w3.org/2000/svg">
                <path id="México" d="M110,143 L142,143 L162,159 L221,178 L265,225 L292,238 L296,256 L273,284 L204,271 L151,234 L121,215 Z" />
                <path id="Cuba" d="M295,188 L355,208 L348,220 L290,205 Z" />
                <path id="República Dominicana" d="M400,215 L435,215 L435,230 L400,230 Z" />
                <path id="Guatemala" d="M290,270 L315,270 L310,295 L285,295 Z" />
                <path id="Honduras" d="M318,275 L355,275 L355,295 L320,300 Z" />
                <path id="El Salvador" d="M315,302 L335,302 L332,312 L315,312 Z" />
                <path id="Nicaragua" d="M345,305 L375,315 L370,345 L340,340 Z" />
                <path id="Costa Rica" d="M365,350 L390,360 L385,380 L360,375 Z" />
                <path id="Panamá" d="M395,365 L435,365 L440,385 L400,395 Z" />
                <path id="Colombia" d="M415,410 L480,420 L495,520 L440,540 L410,480 Z" />
                <path id="Venezuela" d="M485,415 L585,425 L580,510 L495,510 Z" />
                <path id="Ecuador" d="M405,535 L450,535 L445,590 L410,580 Z" />
                <path id="Perú" d="M435,595 L530,595 L570,780 L490,830 L440,680 Z" />
                <path id="Bolivia" d="M550,715 L650,730 L640,860 L570,850 Z" />
                <path id="Paraguay" d="M645,865 L720,875 L715,960 L650,950 Z" />
                <path id="Chile" d="M565,855 L600,855 L630,1200 L590,1200 Z" />
                <path id="Argentina" d="M610,860 L670,860 L730,1190 L640,1190 Z" />
                <path id="Uruguay" d="M730,965 L780,975 L775,1020 L730,1010 Z" />
                <path id="Brasil" d="M510,520 L610,515 L820,620 L810,950 L680,860 L545,720 Z" />
            </svg>
        </div>
    </div>

    <div id="alert"></div>

    <div id="final-screen">
        <h1 style="color: #e91e63; font-size: 3.5rem;">¡Excelente! Sigue aprendiendo español.</h1>
        <div class="dancer-container">
            <div class="dancer">💃</div>
            <div class="dancer">🕺</div>
        </div>
        <p style="font-size: 1.5rem; margin-bottom: 20px;">¡Felicidades por completar el mapa!</p>
        <button class="restart-btn" onclick="location.reload()">Jugar otra vez</button>
    </div>

    <audio id="s-ok" src="https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3"></audio>
    <audio id="s-no" src="https://assets.mixkit.co/active_storage/sfx/2571/2571-preview.mp3"></audio>
    <audio id="s-cumbia" loop></audio>

    <script>
        const paises = ["México", "Guatemala", "Honduras", "El Salvador", "Nicaragua", "Costa Rica", "Panamá", "Cuba", "República Dominicana", "Colombia", "Venezuela", "Ecuador", "Perú", "Bolivia", "Chile", "Argentina", "Paraguay", "Uruguay", "Brasil"];
        let correctos = 0;
        let arrastrando = "";

        function iniciar() {
            const lista = document.getElementById('list');
            [...paises].sort(() => Math.random() - 0.5).forEach(p => {
                const item = document.createElement('div');
                item.className = 'country-chip';
                item.textContent = p;
                item.draggable = true;
                item.id = "tag-" + p;
                item.ondragstart = (e) => { arrastrando = p; e.dataTransfer.setData('text', p); };
                lista.appendChild(item);
            });

            document.querySelectorAll('path').forEach(path => {
                path.ondragover = (e) => e.preventDefault();
                path.ondrop = (e) => {
                    if (arrastrando === path.id) {
                        path.classList.add('correct');
                        document.getElementById("tag-" + arrastrando).classList.add('hidden');
                        document.getElementById('s-ok').play();
                        notificar("¡Excelente!", "#4caf50");
                        correctos++;
                        if(correctos === paises.length) celebrar();
                    } else {
                        document.getElementById('s-no').play();
                        notificar("Intenta otra vez", "#f44336");
                    }
                };
            });
        }

        function notificar(txt, color) {
            const div = document.getElementById('alert');
            div.textContent = txt;
            div.style.background = color;
            div.classList.add('show');
            setTimeout(() => div.classList.remove('show'), 1000);
        }

        function celebrar() {
            const m = document.getElementById('s-cumbia');
            m.src = "https://www.chosic.com/wp-content/uploads/2021/07/The-Joy-of-Success-Cumbia.mp3";
            m.play();
            document.getElementById('final-screen').classList.add('active');
            confetti({ particleCount: 150, spread: 70, origin: { y: 0.6 } });
        }

        iniciar();
    </script>
</body>
</html>
"""

components.html(html_mapa_real, height=950, scrolling=False)
