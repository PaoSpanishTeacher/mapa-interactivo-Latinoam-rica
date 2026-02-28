import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Mapa Interactivo Latinoamérica", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0rem; }
    iframe { border: none; }
    </style>
    """, unsafe_allow_html=True)

html_mapa_perfecto = r"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600&family=Quicksand:wght@500;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
        
        body {
            font-family: 'Quicksand', sans-serif;
            background: #fff9e6;
            display: flex; flex-direction: column; align-items: center;
            padding-top: 80px; /* Espacio para que el título no se corte */
            min-height: 100vh;
        }

        header { text-align: center; margin-bottom: 30px; }
        h1 { font-family: 'Fredoka', sans-serif; color: #d35400; font-size: 3rem; text-shadow: 2px 2px white; }
        
        .main-container {
            display: grid; grid-template-columns: 280px 1fr;
            gap: 30px; width: 95%; max-width: 1200px;
            background: white; padding: 30px; border-radius: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }

        /* Lista de Países */
        .countries-list {
            display: flex; flex-direction: column; gap: 10px;
            max-height: 700px; overflow-y: auto; padding-right: 10px;
        }
        .country-item {
            background: #ff7675; color: white; padding: 12px;
            border-radius: 12px; cursor: grab; text-align: center;
            font-weight: bold; font-size: 1.1rem; transition: 0.3s;
            box-shadow: 0 4px 0 #d63031;
        }
        .country-item.placed { opacity: 0; pointer-events: none; }

        /* Mapa */
        .map-container { position: relative; background: #e3f2fd; border-radius: 20px; overflow: hidden; border: 2px solid #74b9ff; }
        svg { width: 100%; height: 750px; }
        path { fill: #f9f9f9; stroke: #636e72; stroke-width: 1; transition: 0.3s; cursor: pointer; }
        path:hover { fill: #ffeaa7; }
        path.correct { fill: #55efc4 !important; stroke: #00b894; }

        /* Popups */
        #msg {
            position: fixed; top: 120px; left: 50%; transform: translateX(-50%) scale(0);
            padding: 15px 40px; border-radius: 50px; color: white; font-size: 2rem;
            font-weight: bold; z-index: 1000; transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        #msg.show { transform: translateX(-50%) scale(1); }

        /* Pantalla Final */
        #final-screen {
            position: fixed; inset: 0; background: rgba(255,255,255,0.98);
            display: none; flex-direction: column; align-items: center; justify-content: center; z-index: 2000;
        }
        #final-screen.active { display: flex; }
        .celebration-box { text-align: center; }
        .dancers { display: flex; gap: 40px; justify-content: center; margin: 30px; }
        .dancer { font-size: 8rem; animation: bailoteo 0.6s infinite alternate; }
        @keyframes bailoteo { from { transform: rotate(-10deg) translateY(0); } to { transform: rotate(10deg) translateY(-20px); } }
        
        .btn-restart {
            background: #00b894; color: white; border: none; padding: 20px 50px;
            font-size: 2rem; border-radius: 50px; cursor: pointer; font-family: 'Fredoka', sans-serif;
        }
    </style>
</head>
<body>

    <header>
        <h1>Mapa Interactivo - América Latina</h1>
        <p style="font-weight: bold; color: #2d3436;">Pau Spanish Teacher</p>
    </header>

    <div class="main-container">
        <div class="countries-list" id="list"></div>
        <div class="map-container">
            <svg id="latam-map" viewBox="200 150 600 800" xmlns="http://www.w3.org/2000/svg">
                <path id="México" d="M210,210 L250,215 L320,300 L380,350 L350,380 L250,350 Z" />
                <path id="Cuba" d="M400,300 L460,320 L450,330 L400,310 Z" />
                <path id="República Dominicana" d="M500,330 L540,330 L540,345 L500,345 Z" />
                <path id="Guatemala" d="M385,385 L410,385 L410,410 L385,410 Z" />
                <path id="Honduras" d="M415,390 L450,390 L450,410 L415,410 Z" />
                <path id="El Salvador" d="M415,415 L435,415 L435,425 L415,425 Z" />
                <path id="Nicaragua" d="M440,415 L475,415 L475,445 L440,445 Z" />
                <path id="Costa Rica" d="M465,455 L485,455 L485,475 L465,475 Z" />
                <path id="Panamá" d="M490,465 L530,465 L530,485 L490,485 Z" />
                <path id="Colombia" d="M515,495 L580,500 L590,580 L540,590 L510,540 Z" />
                <path id="Venezuela" d="M585,495 L680,505 L675,580 L595,580 Z" />
                <path id="Ecuador" d="M510,595 L550,595 L545,640 L515,630 Z" />
                <path id="Perú" d="M540,645 L620,645 L650,780 L580,820 L540,700 Z" />
                <path id="Bolivia" d="M630,730 L720,740 L710,850 L640,840 Z" />
                <path id="Paraguay" d="M710,860 L770,860 L770,920 L710,920 Z" />
                <path id="Chile" d="M635,850 L670,850 L690,1200 L660,1200 Z" />
                <path id="Argentina" d="M675,850 L725,850 L800,1200 L720,1200 Z" />
                <path id="Uruguay" d="M780,930 L820,930 L820,970 L780,970 Z" />
                <path id="Brasil" d="M600,585 L680,585 L850,650 L850,900 L730,850 L630,750 Z" />
            </svg>
        </div>
    </div>

    <div id="msg"></div>

    <div id="final-screen">
        <div class="celebration-box">
            <h1>¡Excelente! Sigue aprendiendo español.</h1>
            <div class="dancers">
                <div class="dancer">💃</div>
                <div class="dancer">🕺</div>
            </div>
            <button class="btn-restart" onclick="location.reload()">Jugar otra vez</button>
        </div>
    </div>

    <audio id="audio-win" src="https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3"></audio>
    <audio id="audio-error" src="https://assets.mixkit.co/active_storage/sfx/2571/2571-preview.mp3"></audio>
    <audio id="audio-cumbia" loop src="https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3"></audio>

    <script>
        const countries = [
            "México", "Guatemala", "Honduras", "El Salvador", "Nicaragua", 
            "Costa Rica", "Panamá", "Cuba", "República Dominicana", "Colombia", 
            "Venezuela", "Ecuador", "Perú", "Bolivia", "Chile", "Argentina", 
            "Paraguay", "Uruguay", "Brasil"
        ];

        let completed = 0;
        let selectedName = "";

        function init() {
            const listDiv = document.getElementById('list');
            [...countries].sort(() => Math.random() - 0.5).forEach(c => {
                const item = document.createElement('div');
                item.className = 'country-item';
                item.textContent = c;
                item.draggable = true;
                item.id = "tag-" + c;
                item.onselectstart = () => false;
                item.ondragstart = (e) => {
                    selectedName = c;
                    e.dataTransfer.setData('text', c);
                };
                listDiv.appendChild(item);
            });

            document.querySelectorAll('path').forEach(path => {
                path.ondragover = (e) => e.preventDefault();
                path.ondrop = (e) => {
                    e.preventDefault();
                    const targetId = path.id;
                    if (selectedName === targetId) {
                        path.classList.add('correct');
                        document.getElementById("tag-" + selectedName).classList.add('placed');
                        document.getElementById('audio-win').play();
                        showMsg("¡Excelente!", "#00b894");
                        completed++;
                        if(completed === countries.length) finishGame();
                    } else {
                        document.getElementById('audio-error').play();
                        showMsg("Intenta otra vez", "#ff7675");
                    }
                };
            });
        }

        function showMsg(txt, color) {
            const m = document.getElementById('msg');
            m.textContent = txt;
            m.style.background = color;
            m.classList.add('show');
            setTimeout(() => m.classList.remove('show'), 1000);
        }

        function finishGame() {
            // Reproducir música colombiana (Cumbia)
            const cumbia = document.getElementById('audio-cumbia');
            cumbia.src = "https://www.chosic.com/wp-content/uploads/2021/07/The-Joy-of-Success-Cumbia.mp3"; 
            cumbia.play();

            document.getElementById('final-screen').classList.add('active');
            confetti({ particleCount: 200, spread: 100, origin: { y: 0.6 } });
            
            // Efecto de globos
            for(let i=0; i<20; i++) {
                setTimeout(createBalloon, i * 150);
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
            document.body.appendChild(b);
            setTimeout(() => b.style.transform = 'translateY(-120vh)', 50);
            setTimeout(() => b.remove(), 6500);
        }

        init();
    </script>
</body>
</html>
"""

components.html(html_mapa_perfecto, height=950, scrolling=False)
