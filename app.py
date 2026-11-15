import streamlit as st
import json
import os
import time

st.set_page_config(page_title="Cyber Arena - Live Esports Spectator", page_icon="🏆", layout="wide")

DB_FILE = "arena_state.json"
PROTOCOLOS_DISPONIBLES = ["SSH (Puerto 22)", "HTTP/Web (Puerto 80/443)", "RDP (Puerto 3389)", "SMB (Puerto 445)", "FTP (Puerto 21)"]

def cargar_estado():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return {"teams": {"admin": {"ip": "192.168.128.3", "role": "admin", "score": 0, "defense": 1000, "defenses_active": [], "streak": 0}}, "groups": {}, "active_spectator_groups": [], "game_mode": "Rondas", "max_rounds": 5, "current_round": 1, "game_over": False, "winner_msg": None, "last_attack_msg": None}
                data = json.loads(content)
                if not isinstance(data, dict):
                    return {"teams": {"admin": {"ip": "192.168.128.3", "role": "admin", "score": 0, "defense": 1000, "defenses_active": [], "streak": 0}}, "groups": {}, "active_spectator_groups": [], "game_mode": "Rondas", "max_rounds": 5, "current_round": 1, "game_over": False, "winner_msg": None, "last_attack_msg": None}
                if "teams" not in data:
                    data["teams"] = {}
                if "groups" not in data:
                    data["groups"] = {}
                if "active_spectator_groups" not in data:
                    data["active_spectator_groups"] = []
                if "game_mode" not in data:
                    data["game_mode"] = "Rondas"
                if "max_rounds" not in data:
                    data["max_rounds"] = 5
                if "current_round" not in data:
                    data["current_round"] = 1
                if "game_over" not in data:
                    data["game_over"] = False
                if "winner_msg" not in data:
                    data["winner_msg"] = None
                if "last_attack_msg" not in data:
                    data["last_attack_msg"] = None
                return data
        except Exception:
            pass
            
    return {
        "teams": {
            "admin": {"ip": "192.168.128.3", "role": "admin", "score": 0, "defense": 1000, "defenses_active": [], "streak": 0}
        },
        "groups": {},
        "active_spectator_groups": [],
        "game_mode": "Rondas",
        "max_rounds": 5,
        "current_round": 1,
        "game_over": False,
        "winner_msg": None,
        "last_attack_msg": None
    }

def guardar_estado(state):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(state, f)
    except Exception:
        pass

def calcular_ganador(state):
    grupos_activos = state.get("active_spectator_groups", list(state.get("groups", {}).keys()))
    if not grupos_activos:
        return "No hay equipos participantes para determinar un ganador."
    
    stats = []
    for g in grupos_activos:
        t = state["teams"].get(g, {"score": 0, "defense": 1000})
        stats.append({"grupo": g, "score": t["score"], "defense": t["defense"]})
    
    stats = sorted(stats, key=lambda x: (x["score"], x["defense"]), reverse=True)
    
    if len(stats) > 1 and stats[0]["score"] == stats[1]["score"] and stats[0]["defense"] == stats[1]["defense"]:
        return f"🤝 ¡EMPATE TÉCNICO! Los equipos {stats[0]['grupo']} y {stats[1]['grupo']} terminaron con idénticas estadísticas ({stats[0]['score']} pts, {stats[0]['defense']} salud)."
    else:
        ganador = stats[0]
        return f"🏆 ¡VICTORY! EL GANADOR DE LA ARENA ES EL GRUPO **{ganador['grupo']}** con {ganador['score']} puntos de ataque y {ganador['defense']} de salud defensiva!"

state = cargar_estado()

# ==========================================
# LOGIN / AUTENTICACIÓN
# ==========================================
st.sidebar.header("🔐 Acceso a la Plataforma")
login_user = st.sidebar.text_input("Usuario / Grupo / spectator", value="")

if not login_user:
    st.title("🏆 CYBER ARENA - LIVE ESPORTS STREAM ⚔️")
    st.info("👈 Escribe **`spectator`** en la barra lateral para ver la pantalla gigante de proyección o ingresa tu grupo.")
    
    st.subheader("📋 Grupos Registrados en la Red")
    if state.get("groups"):
        preview_data = [{"Grupo": g, "IP Asignada": ip} for g, ip in state["groups"].items()]
        st.table(preview_data)
    else:
        st.warning("Aún no hay grupos creados. Entra como 'admin' para crearlos.")
    st.stop()

# ==========================================
# VISTA DE ESPECTADOR (PROYECCIÓN / PANTALLA GIGANTE)
# ==========================================
if login_user.lower() in ["spectator", "espectador", "screen"]:
    st.title("🏆 CYBER ARENA - BROADCAST CENTER (PANTALLA GIGANTE) ⚔️")
    
    col_ctrl1, col_ctrl2 = st.columns([2, 2])
    with col_ctrl1:
        if st.button("⚡ Actualizar Eventos y Tablero Ahora", type="primary"):
            st.rerun()
    with col_ctrl2:
        auto_refresh = st.checkbox("Activar Auto-Refresco (cada 5 segundos)", value=False)

    st.markdown("---")

    game_mode = state.get("game_mode", "Rondas")
    ronda_actual = state.get("current_round", 1)
    max_rondas = state.get("max_rounds", 5)
    
    if game_mode == "Rondas" and state.get("game_over", False):
        st.markdown(f"""
        <div style="background-color: #2b0000; border: 4px solid #ff0000; padding: 25px; border-radius: 12px; text-align: center; margin-bottom: 25px;">
            <h1 style="color: #ff3333; font-size: 42px; margin: 0;">🛑 PARTIDA FINALIZADA 🛑</h1>
            <h2 style="color: #ffcc00; font-size: 28px; margin-top: 15px;">{state.get('winner_msg')}</h2>
        </div>
        """, unsafe_allow_html=True)
    else:
        if game_mode == "Rondas":
            st.info(f"📍 **ESTADO DEL TORNEO:** Modo Rondas | Ronda **{ronda_actual}** de **{max_rondas}**")
        else:
            st.info(f"📍 **ESTADO DEL TORNEO:** Modo Libre (Sin límite de rondas)")

    grupos_a_mostrar = state.get("active_spectator_groups", [])

    if state.get("last_attack_msg") and not (game_mode == "Rondas" and state.get("game_over", False)):
        msg_info = state["last_attack_msg"]
        dota_effect = msg_info.get("dota_effect", "ANNOUNCEMENT")
        
        if msg_info["type"] == "success":
            st.markdown(f"""
            <div style="background-color: #1a0000; border: 3px solid #ffcc00; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 25px;">
                <h1 style="color: #ffcc00; font-size: 38px; margin: 0;">🔥 {dota_effect} 🔥</h1>
                <p style="color: #ffffff; font-size: 22px; margin-top: 10px;">{msg_info['text']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background-color: #001a1a; border: 3px solid #00ffcc; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 25px;">
                <h1 style="color: #00ffcc; font-size: 38px; margin: 0;">🛡️ DEFENSE HOLD / STREAK RESET! 🛡️</h1>
                <p style="color: #ffffff; font-size: 22px; margin-top: 10px;">{msg_info['text']}</p>
            </div>
            """, unsafe_allow_html=True)

    st.subheader("📊 Tabla de Posiciones en Vivo (Live Leaderboard)")
    
    equipos_ordenados = []
    for g in grupos_a_mostrar:
        if g in state.get("groups", {}):
            ip = state["groups"][g]
            t_data = state["teams"].get(g, {"score": 0, "defense": 1000, "defenses_active": [], "streak": 0})
            equipos_ordenados.append({
                "Grupo": g,
                "IP Fija": ip,
                "Score Ataque": t_data["score"],
                "Salud Defensiva": t_data["defense"],
                "Racha Activa 🔥": t_data.get("streak", 0),
                "Protocolos Asegurados": len(t_data.get("defenses_active", []))
            })
    
    equipos_ordenados = sorted(equipos_ordenados, key=lambda x: x["Score Ataque"], reverse=True)
    
    if equipos_ordenados:
        st.dataframe(equipos_ordenados, use_container_width=True, height=400)
    else:
        st.info("El administrador aún no ha seleccionado qué equipos mostrar en el proyector.")

    if auto_refresh:
        time.sleep(5)
        st.rerun()
        
    st.stop()

# ==========================================
# VALIDAR ADMIN
# ==========================================
if login_user.lower() == "admin":
    st.sidebar.success("✅ Sesión: ADMINISTRADOR")
    st.header("🛠️ Panel de Administración de Red")
    
    st.subheader("⚙️ Configuración del Modo de Juego")
    with st.form("form_config_modo"):
        selected_mode = st.radio("Selecciona el Modo de Partida", options=["Rondas", "Libre"], index=0 if state.get("game_mode", "Rondas") == "Rondas" else 1)
        nueva_max_rondas = st.number_input("Cantidad Máxima de Rondas (Solo aplica en Modo Rondas)", min_value=1, max_value=20, value=int(state.get("max_rounds", 5)))
        
        btn_guardar_modo = st.form_submit_button("Guardar Configuración de Partida")
        if btn_guardar_modo:
            state["game_mode"] = selected_mode
            state["max_rounds"] = int(nueva_max_rondas)
            if selected_mode == "Libre":
                state["game_over"] = False
                state["winner_msg"] = None
            guardar_estado(state)
            st.success(f"¡Modo configurado a **{selected_mode}** con éxito!")
            st.rerun()

    st.markdown("---")
    
    with st.form("form_crear_grupo", clear_on_submit=True):
        st.subheader("➕ Registrar Nuevo Grupo")
        nuevo_grupo = st.text_input("Nombre del Grupo (Ej. Equipo-Alfa)")
        nueva_ip = st.text_input("IP Fija (Ej. 192.168.128.15)")
        btn_crear = st.form_submit_button("Registrar Grupo")
        
        if btn_crear:
            if not nuevo_grupo or not nueva_ip:
                st.error("Completa todos los campos.")
            else:
                state["groups"][nuevo_grupo] = nueva_ip
                if nuevo_grupo not in state["teams"]:
                    state["teams"][nuevo_grupo] = {
                        "ip": nueva_ip,
                        "role": "team",
                        "score": 0,
                        "defense": 1000,
                        "defenses_active": [],
                        "streak": 0
                    }
                else:
                    state["teams"][nuevo_grupo]["ip"] = nueva_ip
                
                if nuevo_grupo not in state.get("active_spectator_groups", []):
                    state["active_spectator_groups"].append(nuevo_grupo)

                guardar_estado(state)
                st.success(f"¡Grupo '{nuevo_grupo}' registrado con éxito!")
                st.rerun()

    st.markdown("---")
    st.subheader("📺 Selección de Equipos para el Proyector (Spectator)")
    st.markdown("Marca qué grupos deseas que salgan en la pantalla gigante de la ronda actual:")

    todos_los_grupos = list(state.get("groups", {}).keys())
    active_spectators = state.get("active_spectator_groups", [])

    if todos_los_grupos:
        with st.form("form_selector_proyector"):
            nuevos_activos = []
            for g in todos_los_grupos:
                is_on = st.checkbox(f"Mostrar a **{g}** en el Proyector", value=(g in active_spectators), key=f"proj_{g}")
                if is_on:
                    nuevos_activos.append(g)
            
            btn_guardar_proyector = st.form_submit_button("💾 Guardar Selección para Proyección")
            if btn_guardar_proyector:
                state["active_spectator_groups"] = nuevos_activos
                guardar_estado(state)
                st.success("¡Configuración del proyector actualizada con éxito!")
                st.rerun()
    else:
        st.info("Crea grupos primero para poder seleccionarlos aquí.")

    st.markdown("---")
    st.subheader("🔄 Control de Rondas y Puntajes")
    
    col_admin1, col_admin2 = st.columns(2)
    
    with col_admin1:
        if st.button("🧹 Reiniciar Puntajes, Rachas y Volver a Ronda 1", type="primary"):
            for g in state.get("groups", {}).keys():
                state["teams"][g] = {
                    "ip": state["groups"][g],
                    "role": "team",
                    "score": 0,
                    "defense": 1000,
                    "defenses_active": [],
                    "streak": 0
                }
            state["current_round"] = 1
            state["game_over"] = False
            state["winner_msg"] = None
            state["last_attack_msg"] = None
            guardar_estado(state)
            st.success("¡Partida reiniciada a la Ronda 1! Puntajes y rachas en cero, manteniendo los grupos.")
            st.rerun()

    with col_admin2:
        if st.button("🗑️ Borrar TODO (Grupos y Puntajes por completo)"):
            state["teams"] = {"admin": {"ip": "192.168.128.3", "role": "admin", "score": 0, "defense": 1000, "defenses_active": [], "streak": 0}}
            state["groups"] = {}
            state["active_spectator_groups"] = []
            state["current_round"] = 1
            state["game_over"] = False
            state["winner_msg"] = None
            state["last_attack_msg"] = None
            guardar_estado(state)
            st.success("¡Arena totalmente limpiada!")
            st.rerun()

    st.markdown("---")
    st.subheader("📋 Estado Actual de Grupos y Red")
    if state.get("groups"):
        admin_table = []
        for g, ip in state["groups"].items():
            t_data = state["teams"].get(g, {"score": 0, "defense": 1000, "streak": 0})
            admin_table.append({
                "Grupo": g,
                "IP Fija": ip,
                "Score": t_data["score"],
                "Salud": t_data["defense"],
                "Racha": t_data["streak"],
                "En Proyector": "✅ Sí" if g in state.get("active_spectator_groups", []) else "❌ No"
            })
        st.table(admin_table)
    else:
        st.info("No hay grupos todavía.")

    st.stop()

# ==========================================
# VISTA DE EQUIPOS PARTICIPANTES
# ==========================================
if login_user not in state.get("groups", {}):
    st.error(f"[!] El usuario '{login_user}' no está registrado en la red. Solicita al administrador que cree tu grupo.")
    st.stop()

if login_user not in state["teams"]:
    state["teams"][login_user] = {
        "ip": state["groups"][login_user],
        "role": "team",
        "score": 0,
        "defense": 1000,
        "defenses_active": [],
        "streak": 0
    }
    guardar_estado(state)

my_data = state["teams"][login_user]
my_ip = state["groups"][login_user]

st.sidebar.success(f"Sesión: **{login_user}**")
st.sidebar.info(f"IP: **{my_ip}**")

st.header(f"Panel de Control: {login_user}")

if st.button("🔄 Actualizar Mis Datos / Ver Últimos Eventos"):
    st.rerun()

game_mode = state.get("game_mode", "Rondas")

if game_mode == "Rondas" and state.get("game_over", False):
    st.error(f"🛑 **PARTIDA FINALIZADA** — {state.get('winner_msg')}")
    st.stop()

if game_mode == "Rondas":
    st.info(f"⚔️ **Modo Rondas:** Ronda actual {state.get('current_round', 1)} / {state.get('max_rounds', 5)}")
else:
    st.info(f"♾️ **Modo Libre:** Practica y compite sin límite de rondas.")

if state.get("last_attack_msg"):
    msg_info = state["last_attack_msg"]
    if msg_info["type"] == "success":
        st.success(msg_info["text"])
    else:
        st.error(msg_info["text"])

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Score de Ataque", value=my_data["score"])
with col2:
    st.metric(label="Salud Defensiva", value=my_data["defense"])
with col3:
    st.metric(label="Racha Actual (Streak)", value=my_data.get("streak", 0))

st.markdown("---")

# ==========================================
# FASE 1: PANEL DEFENSIVO
# ==========================================
st.subheader("🛡️ Fase 1: Panel Defensivo - Asegura tu Red (Blue Team)")
st.markdown("Configura qué protocolos mantendrás blindados ante posibles hackeos rivales:")
defenses_actuales = my_data.get("defenses_active", [])
nuevas_defensas = []

for proto in PROTOCOLOS_DISPONIBLES:
    is_checked = st.checkbox(f"Bloquear / Asegurar {proto}", value=(proto in defenses_actuales), key=f"def_{login_user}_{proto}")
    if is_checked:
        nuevas_defensas.append(proto)

if set(nuevas_defensas) != set(defenses_actuales):
    state["teams"][login_user]["defenses_active"] = nuevas_defensas
    guardar_estado(state)
    st.rerun()

st.markdown("---")

# ==========================================
# FASE 2: PANEL DE ATAQUE
# ==========================================
st.subheader("⚔️ Fase 2: Panel de Ataque - Escaneo y Explotación (Red Team)")
st.markdown("Selecciona el equipo rival y los protocolos que deseas vulnerar:")

rivales_disponibles = [g for g in state.get("groups", {}).keys() if g != login_user]

if not rivales_disponibles:
    st.warning("No hay otros grupos conectados para atacar.")
else:
    target_group = st.selectbox("Selecciona el Grupo Rival a Atacar", rivales_disponibles)
    target_ip = state["groups"][target_group]
    st.text(f"IP Objetivo: {target_ip}")
    
    protocolos_a_atacar = []
    for proto in PROTOCOLOS_DISPONIBLES:
        if st.checkbox(f"Atacar {proto}", key=f"atk_{proto}"):
            protocolos_a_atacar.append(proto)

    if st.button("⚡ Ejecutar Ataque", type="primary"):
        if not protocolos_a_atacar:
            st.error("Debes seleccionar al menos un protocolo para lanzar el ataque.")
        else:
            defender = state["teams"][target_group]
            defensas_rival = defender.get("defenses_active", [])
            
            no_bloqueados = [p for p in protocolos_a_atacar if p not in defensas_rival]
            bloqueados = [p for p in protocolos_a_atacar if p in defensas_rival]
            
            num_exitos = len(no_bloqueados)
            puntos_ganados = num_exitos * 100
            dano_defensa = num_exitos * 100
            
            if bloqueados:
                state["teams"][login_user]["streak"] = 0
                racha_rota = True
            else:
                racha_rota = False

            if num_exitos > 0:
                state["teams"][login_user]["score"] += puntos_ganados
                defender["defense"] = max(0, defender["defense"] - dano_defensa)
                
                if not racha_rota:
                    current_streak = state["teams"][login_user].get("streak", 0) + 1
                    state["teams"][login_user]["streak"] = current_streak
                else:
                    current_streak = 0
                
                if current_streak >= 5:
                    dota_effect = f"GODLIKE! ({current_streak}ª Racha Perfecta)"
                elif current_streak == 4:
                    dota_effect = f"RAMPAGE! ({current_streak}ª Racha Perfecta)"
                elif current_streak == 3:
                    dota_effect = f"UNSTOPPABLE! ({current_streak}ª Racha Perfecta)"
                elif current_streak == 2:
                    dota_effect = f"DOMINATING! ({current_streak}ª Racha Perfecta)"
                else:
                    dota_effect = "FIRST BLOOD! / BREACH DETECTED!"

                if racha_rota:
                    msg_text = f"⚠️ {login_user} penetró parcialmente ({', '.join(no_bloqueados)}), ¡pero {target_group} bloqueó {', '.join(bloqueados)}! Racha rota a 0. (+{puntos_ganados} pts)."
                    msg_type = "error"
                else:
                    msg_text = f"🚀 {login_user} hackeo limpio a {target_group} ({target_ip}) explotando: {', '.join(no_bloqueados)}. (+{puntos_ganados} pts)."
                    msg_type = "success"
            else:
                state["teams"][login_user]["streak"] = 0
                dota_effect = "STREAK ENDED / TOTAL DEFENSE HOLD!"
                msg_text = f"🛡️ ¡{target_group} bloqueó ABSOLUTAMENTE todo! Ataque repelido por completo. Racha en 0."
                msg_type = "error"

            state["last_attack_msg"] = {"type": msg_type, "text": msg_text, "dota_effect": dota_effect}
            
            # Si está en modo rondas, avanzamos el contador
            if state.get("game_mode", "Rondas") == "Rondas":
                state["current_round"] += 1
                if state["current_round"] > state["max_rounds"]:
                    state["game_over"] = True
                    state["winner_msg"] = calcular_ganador(state)

            guardar_estado(state)
            st.rerun()

st.markdown("---")

st.subheader("📋 Estado General de la Red en Vivo")
table_data = []
for g, ip in state.get("groups", {}).items():
    t_data = state["teams"].get(g, {"score": 0, "defense": 1000, "defenses_active": [], "streak": 0})
    table_data.append({
        "Grupo": g,
        "IP Fija": ip,
        "Score Ataque": t_data["score"],
        "Salud Defensiva": t_data["defense"],
        "Racha 🔥": t_data.get("streak", 0),
        "Protocolos Asegurados": ", ".join([p.split()[0] for p in t_data.get("defenses_active", [])]) if t_data.get("defenses_active") else "Ninguno ⚠️"
    })

st.table(table_data)

if st.button("🔄 Actualizar Tabla General"):
    st.rerun()
