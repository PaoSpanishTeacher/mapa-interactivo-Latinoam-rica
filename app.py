import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Mapa Real LATAM", layout="wide")

st.markdown("""
    <style>
    .block-container { padding: 0rem; }
    iframe { border: none; }
    </style>
    """, unsafe_allow_html=True)

html_mapa_profesional = r"""
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
            padding-top: 120px; /* Espacio extra para el título */
            display: flex; flex-direction: column; align-items: center;
            min-height: 100vh; overflow-x: hidden;
        }
        header { text-align: center; margin-bottom: 20px; width: 100%; position: absolute; top: 20px; }
        h1 { font-family: 'Fredoka', sans-serif; color: #00695c; font-size: 2.5rem; text-shadow: 2px 2px white; }
        
        .game-layout {
            display: grid; grid-template-columns: 280px 1fr;
            gap: 20px; width: 95%; max-width: 1200px; height: 750px;
            background: white; padding: 20px; border-radius: 30px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        }

        .sidebar {
            background: #f1f8e9; border-radius: 20px; padding: 15px;
            display: flex; flex-direction: column; gap: 8px;
            overflow-y: auto; border: 2px solid #dcedc8;
        }
        .country-chip {
            background: #ff7043; color: white; padding: 12px;
            border-radius: 12px; cursor: grab; text-align: center;
            font-weight: bold; font-size: 1rem; box-shadow: 0 4px 0 #d84315;
            transition: 0.2s;
        }
        .country-chip:active { cursor: grabbing; transform: translateY(2px); box-shadow: none; }
        .country-chip.correct { opacity: 0; pointer-events: none; }

        .map-wrapper {
            background: #b3e5fc; border-radius: 20px; position: relative;
            overflow: hidden; border: 3px solid #81d4fa; display: flex; justify-content: center;
        }
        svg { width: 100%; height: 100%; }
        
        path.country {
            fill: #ffffff; stroke: #455a64; stroke-width: 0.5;
            transition: 0.3s; cursor: pointer;
        }
        path.highlight { fill: #fff9c4; stroke-width: 1.5; }
        path.correct-fill { fill: #4caf50 !important; stroke: #1b5e20; }

        /* Popups */
        #alert {
            position: fixed; top: 150px; left: 50%; transform: translateX(-50%) scale(0);
            padding: 15px 40px; border-radius: 50px; color: white; font-size: 2rem;
            font-weight: bold; z-index: 3000; transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        #alert.show { transform: translateX(-50%) scale(1); }

        /* Final con Cumbia */
        #final-screen {
            position: fixed; inset: 0; background: rgba(255,255,255,0.98);
            display: none; flex-direction: column; align-items: center; justify-content: center;
            z-index: 4000; text-align: center;
        }
        #final-screen.active { display: flex; }
        .dancer-box { display: flex; gap: 40px; margin: 30px; }
        .dancer { font-size: 8rem; animation: jump 0.6s infinite alternate ease-in-out; }
        @keyframes jump { from { transform: translateY(0) rotate(-5deg); } to { transform: translateY(-30px) rotate(5deg); } }
        
        .restart-btn {
            background: #ff4757; color: white; border: none; padding: 20px 45px;
            font-size: 2rem; border-radius: 60px; cursor: pointer; font-family: 'Fredoka';
            box-shadow: 0 8px 0 #b33939;
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
        <div class="map-wrapper" id="map">
            <svg id="latam-svg"></svg>
        </div>
    </div>

    <div id="alert"></div>

    <div id="final-screen">
        <h1 style="color: #ff4757; font-size: 3rem;">¡Excelente! Sigue aprendiendo español.</h1>
        <div class="dancer-box">
            <div class="dancer">💃</div>
            <div class="dancer">🕺</div>
        </div>
        <button class="restart-btn" onclick="location.reload()">Jugar otra vez</button>
    </div>

    <audio id="s-ok" src="https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3"></audio>
    <audio id="s-no" src="https://assets.mixkit.co/active_storage/sfx/2571/2571-preview.mp3"></audio>
    <audio id="s-cumbia" loop src="https://www.chosic.com/wp-content/uploads/2021/07/The-Joy-of-Success-Cumbia.mp3"></audio>

    <script>
        const targetCountries = ["Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Costa Rica", "Cuba", "Dominican Republic", "Ecuador", "El Salvador", "Guatemala", "Honduras", "Mexico", "Nicaragua", "Panama", "Paraguay", "Peru", "Uruguay", "Venezuela"];
        
        const nameMap = {
            "Argentina": "Argentina", "Bolivia": "Bolivia", "Brazil": "Brasil", "Chile": "Chile", 
            "Colombia": "Colombia", "Costa Rica": "Costa Rica", "Cuba": "Cuba", 
            "Dominican Republic": "República Dominicana", "Ecuador": "Ecuador", 
            "El Salvador": "El Salvador", "Guatemala": "Guatemala", "Honduras": "Honduras", 
            "Mexico": "México", "Nicaragua": "Nicaragua", "Panama": "Panamá", 
            "Paraguay": "Paraguay", "Peru": "Perú", "Uruguay": "Uruguay", "Venezuela": "Venezuela"
        };

        let completed = 0;
        let draggedName = "";

        const svg = d3.select("#latam-svg");
        const projection = d3.geoMercator().center([-70, -15]).scale(350).translate([350, 400]);
        const path = d3.geoPath().projection(projection);

        async function init() {
            // Cargar Mapa Real (TopoJSON de alta calidad)
            const world = await d3.json("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json");
            const countries = topojson.feature(world, world.objects.countries).features;

            const latam = countries.filter(d => targetCountries.includes(d.properties.name));

            svg.selectAll("path")
                .data(latam)
                .enter().append("path")
                .attr("d", path)
                .attr("class", "country")
                .attr("id", d => nameMap[d.properties.name])
                .on("dragover", function(e) { e.preventDefault(); d3.select(this).classed("highlight", true); })
                .on("dragleave", function() { d3.select(this).classed("highlight", false); })
                .on("drop", function(e, d) {
                    e.preventDefault();
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

            // Crear chips de países en la lista
            const list = document.getElementById('list');
            Object.values(nameMap).sort().forEach(name => {
                const chip = document.createElement('div');
                chip.className = 'country-chip';
                chip.textContent = name;
                chip.draggable = true;
                chip.id = "chip-" + name;
                chip.ondragstart = (e) => { draggedName = name; };
                list.appendChild(chip);
            });
        }

        function showAlert(txt, color) {
            const el = document.getElementById('alert');
            el.textContent = txt;
            el.style.background = color;
            el.classList.add('show');
            setTimeout(() => el.classList.remove('show'), 1000);
        }

        function finish() {
            document.getElementById('s-cumbia').play();
            document.getElementById('final-screen').classList.add('active');
            confetti({ particleCount: 200, spread: 80, origin: { y: 0.6 } });
        }

        init();
    </script>
</body>
</html>
"""

components.html(html_mapa_profesional, height=900, scrolling=False)
