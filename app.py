import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Mapa interactivo latinoamérica", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0rem; }
    iframe { border: none; }
    </style>
    """, unsafe_allow_html=True)

html_mapa_musica_fix = r"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://unpkg.com/topojson@3"></script>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@600&family=Quicksand:wght@500;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
        body {
            font-family: 'Quicksand', sans-serif;
            background: #e0f7fa;
            padding-top: 80px;
            display: flex; flex-direction: column; align-items: center;
            min-height: 100vh; overflow: hidden;
        }
        header { text-align: center; margin-bottom: 10px; z-index: 10; }
        h1 { font-family: 'Fredoka', sans-serif; color: #00695c; font-size: 2.2rem; text-shadow: 2px 2px white; }
        
        .game-layout {
            display: grid; grid-template-columns: 260px 1fr;
            gap: 20px; width: 95%; max-width: 1200px; height: 720px;
            background: white; padding: 20px; border-radius: 30px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1); border: 4px solid #fff;
        }

        .sidebar {
            background: #f1f8e9; border-radius: 20px; padding: 15px;
            display: flex; flex-direction: column; gap: 8px;
            overflow-y: auto; border: 2px solid #dcedc8;
        }
        .country-chip {
            background: #ff7043; color: white; padding: 10px;
            border-radius: 12px; cursor: grab; text-align: center;
            font-weight: bold; font-size: 0.9rem; box-shadow: 0 4px 0 #d84315;
            transition: 0.2s;
        }
        .country-chip:active { transform: translateY(2px); box-shadow: none; }
        .country-chip.correct { display: none; }

        .map-wrapper {
            background: #b3e5fc; border-radius: 20px; position: relative;
            overflow: hidden; border: 3px solid #81d4fa;
        }
        svg { width: 100%; height: 100%; }
        
        path.country {
            fill: #ffffff; stroke: #455a64; stroke-width: 0.6;
            transition: 0.3s; cursor: pointer;
        }
        path.highlight { fill: #fff9c4; stroke-width: 1.5; stroke: #00695c; }
        path.correct-fill { fill: #4caf50 !important; stroke: #1b5e20; }

        #alert {
            position: fixed; top: 120px; left: 50%; transform: translateX(-50%) scale(0);
            padding: 12px 40px; border-radius: 50px; color: white; font-size: 1.8rem;
            font-weight: bold; z-index: 3000; transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        #alert.show { transform: translateX(-50%) scale(1); }

        #final-screen {
            position: fixed; inset: 0; background: rgba(255,255,255,0.98);
            display: none; flex-direction: column; align-items: center; justify-content: center;
            z-index: 4000; text-align: center;
        }
        #final-screen.active { display: flex; animation: slideIn 0.5s ease-out; }
        @keyframes slideIn { from { transform: translateY(100%); } to { transform: translateY(0); } }

        .dancer-box { display: flex; gap: 40px; margin: 20px; }
        .dancer { font-size: 8rem; animation: cumbiaStep 0.6s infinite alternate ease-in-out; }
        @keyframes cumbiaStep { 
            0% { transform: rotate(-10deg) translateY(0); } 
            100% { transform: rotate(10deg) translateY(-25px); } 
        }
        
        .restart-btn {
            background: #ff4757; color: white; border: none; padding: 15px 40px;
            font-size: 2rem; border-radius: 60px; cursor: pointer; font-family: 'Fredoka';
            box-shadow: 0 6px 0 #b33939; transition: 0.2s;
        }
    </style>
</head>
<body onmousedown="prepararAudio()" ontouchstart="prepararAudio()">

    <header>
        <h1>Mapa Interactivo - América Latina</h1>
        <p style="color: #00796b; font-weight: bold;">PaoSpanishTeacher</p>
    </header>

    <div class="game-layout">
        <div class="sidebar" id="list"></div>
        <div class="map-wrapper">
            <svg id="latam-svg"></svg>
        </div>
    </div>

    <div id="alert"></div>

    <div id="final-screen">
        <h1 style="color: #ff4757; font-size: 3rem;">¡Excelente!</h1>
        <h2 style="color: #00695c; font-size: 1.8rem;">Sigue aprendiendo español</h2>
        <div class="dancer-box">
            <div class="dancer">💃</div>
            <div class="dancer">🕺</div>
        </div>
        <button class="restart-btn" onclick="location.reload()">Jugar otra vez</button>
    </div>

    <audio id="s-ok" preload="auto" src="https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3"></audio>
    <audio id="s-no" preload="auto" src="https://assets.mixkit.co/active_storage/sfx/2571/2571-preview.mp3"></audio>
    <audio id="s-cumbia" loop preload="auto">
        <source src="https://www.chosic.com/wp-content/uploads/2021/07/The-Joy-of-Success-Cumbia.mp3" type="audio/mpeg">
    </audio>

    <script>
        const targetCountries = ["Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Costa Rica", "Cuba", "Ecuador", "El Salvador", "Guatemala", "Honduras", "Mexico", "Nicaragua", "Panama", "Paraguay", "Peru", "Uruguay", "Venezuela"];
        const nameMap = { "Argentina": "Argentina", "Bolivia": "Bolivia", "Brazil": "Brasil", "Chile": "Chile", "Colombia": "Colombia", "Costa Rica": "Costa Rica", "Cuba": "Cuba", "Ecuador": "Ecuador", "El Salvador": "El Salvador", "Guatemala": "Guatemala", "Honduras": "Honduras", "Mexico": "México", "Nicaragua": "Nicaragua", "Panama": "Panamá", "Paraguay": "Paraguay", "Peru": "Perú", "Uruguay": "Uruguay", "Venezuela": "Venezuela" };

        let completed = 0;
        let draggedName = "";
        let audioContextUnlocked = false;

        // Esta función desbloquea el audio en cuanto el usuario toca cualquier parte de la pantalla
        function prepararAudio() {
            if (!audioContextUnlocked) {
                const cumbia = document.getElementById('s-cumbia');
                const ok = document.getElementById('s-ok');
                const no = document.getElementById('s-no');
                
                // Reproducimos y pausamos inmediatamente para ganar el permiso del navegador
                [cumbia, ok, no].forEach(a => {
                    a.play().then(() => { a.pause(); a.currentTime = 0; }).catch(e => {});
                });
                audioContextUnlocked = true;
            }
        }

        const svg = d3.select("#latam-svg");
        const projection = d3.geoMercator().center([-72, -18]).scale(370).translate([350, 400]);
        const path = d3.geoPath().projection(projection);

        async function init() {
            const world = await d3.json("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json");
            const countries = topojson.feature(world, world.objects.countries).features;
            const latamData = countries.filter(d => targetCountries.includes(d.properties.name));

            svg.selectAll("path")
                .data(latamData)
                .enter().append("path")
                .attr("d", path)
                .attr("class", "country")
                .attr("id", d => nameMap[d.properties.name])
                .on("dragover", function(e) { e.preventDefault(); d3.select(this).classed("highlight", true); })
                .on("dragleave", function() { d3.select(this).classed("highlight", false); })
                .on("drop", function(e, d) {
                    e.preventDefault();
                    prepararAudio(); // Re-asegurar audio en cada drop
                    d3.select(this).classed("highlight", false);
                    const targetName = nameMap[d.properties.name];
                    if (draggedName === targetName) {
                        d3.select(this).classed("correct-fill", true).style("pointer-events", "none");
                        document.getElementById("chip-"+draggedName).classList.add("correct");
                        document.getElementById('s-ok').play();
                        showAlert("¡Excelente!", "#4caf50");
                        completed++;
                        if(completed === targetCountries.length) finish();
                    } else {
                        document.getElementById('s-no').play();
                        showAlert("Intenta otra vez", "#ff4757");
                    }
                });

            const list = document.getElementById('list');
            Object.values(nameMap).sort().forEach(name => {
                const chip = document.createElement('div');
                chip.className = 'country-chip';
                chip.textContent = name;
                chip.draggable = true;
                chip.id = "chip-" + name;
                chip.ondragstart = (e) => { 
                    prepararAudio(); 
                    draggedName = name; 
                };
                list.appendChild(chip);
            });
        }

        function showAlert(txt, color) {
            const el = document.getElementById('alert');
            el.textContent = txt; el.style.background = color;
            el.classList.add('show');
            setTimeout(() => el.classList.remove('show'), 1000);
        }

        function finish() {
            const cumbia = document.getElementById('s-cumbia');
            cumbia.volume = 0.8;
            // Forzamos el play con un pequeño delay para asegurar la transición visual
            setTimeout(() => {
                cumbia.play().catch(e => console.log("Error de audio:", e));
            }, 100);
            
            document.getElementById('final-screen').classList.add('active');
            var duration = 6 * 1000;
            var end = Date.now() + duration;
            (function frame() {
                confetti({ particleCount: 5, angle: 60, spread: 60, origin: { x: 0 } });
                confetti({ particleCount: 5, angle: 120, spread: 60, origin: { x: 1 } });
                if (Date.now() < end) requestAnimationFrame(frame);
            }());
        }

        init();
    </script>
</body>
</html>
"""

components.html(html_mapa_musica_fix, height=920, scrolling=False)
