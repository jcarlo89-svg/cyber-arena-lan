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
                    return {"teams": {"admin": {"ip": "192.168.128.3", "role": "admin", "score": 0, "defense": 1000, "defenses_active": [], "streak": 0}}, "groups": {}, "last_attack_msg": None}
                data = json.loads(content)
                if not isinstance(data, dict):
                    return {"teams": {"admin": {"ip": "192.168.128.3", "role": "admin", "score": 0, "defense": 1000, "defenses_active": [], "streak": 0}}, "groups": {}, "last_attack_msg": None}
                if "teams" not in data:
                    data["teams"] = {}
                if "groups" not in data:
                    data["groups"] = {}
                if "last_attack_msg" not in data:
                    data["last_attack_msg"] = None
                return data
        except Exception:
            pass
            
    # Estado inicial por defecto si no existe o hay error
    return {
        "teams": {
            "admin": {"ip": "192.168.128.3", "role": "admin", "score": 0, "defense": 1000, "defenses_active": [], "streak": 0}
        },
        "groups": {},
        "last_attack_msg": None
    }

def guardar_estado(state):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(state, f)
    except Exception:
        pass

# Cargar estado actual
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
    
    if state.get("last_attack_msg"):
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
    else:
        st.markdown("""
        <div style="background-color: #111; border: 2px dashed #444; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 25px;">
            <h3 style="color: #888; margin: 0;">📡 ESPERANDO ACTIVIDAD DE RED... ¡PREPÁRENSE PARA LA CAZA!</h3>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("📊 Tabla de Posiciones en Vivo (Live Leaderboard)")
    
    equipos_ordenados = []
    for g, ip in state.get("groups", {}).items():
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
        st.info("No hay equipos participando todavía.")

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
                guardar_estado(state)
                st.success(f"¡Grupo '{nuevo_grupo}' registrado con éxito!")
                st.rerun()

    st.markdown("---")
    st.subheader("🔄 Control de Rondas y Puntajes")
    
    col_admin1, col_admin2 = st.columns(2)
    
    with col_admin1:
        if st.button("🧹 Reiniciar Puntajes y Rachas (Mantener Grupos e IPs)", type="primary"):
            for g in state.get("groups", {}).keys():
                state["teams"][g] = {
                    "ip": state["groups"][g],
                    "role": "team",
                    "score": 0,
                    "defense": 1000,
                    "defenses_active": [],
                    "streak": 0
                }
            state["last_attack_msg"] = None
            guardar_estado(state)
            st.success("¡Puntajes, salud y rachas reseteados para una nueva ronda! Los grupos se mantienen.")
            st.rerun()

    with col_admin2:
        if st.button("🗑️ Borrar TODO (Grupos y Puntajes por completo)"):
            state["teams"] = {"admin": {"ip": "192.168.128.3", "role": "admin", "score": 0, "defense": 1000, "defenses_active": [], "streak": 0}}
            state["groups"] = {}
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
                "Racha": t_data["streak"]
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

st.subheader("🛡️ Panel Defensivo - Bloqueo de Protocolos (Blue Team)")
defenses_actuales = my_data.get("defenses_active", [])
nuevas_defensas = []

for proto in PROTOCOLOS_DISPONIBLES:
    is_checked = st.checkbox(
