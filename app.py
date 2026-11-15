import streamlit as st
import json
import os

st.set_page_config(page_title="Cyber Arena - Protocol Security", page_icon="🛡️", layout="centered")

DB_FILE = "arena_state.json"

# Lista oficial de protocolos disponibles en la arena
PROTOCOLOS_DISPONIBLES = ["SSH (Puerto 22)", "HTTP/Web (Puerto 80/443)", "RDP (Puerto 3389)", "SMB (Puerto 445)", "FTP (Puerto 21)"]

def cargar_estado():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return {"teams": {}, "groups": {}, "last_attack_msg": None}
                data = json.loads(content)
                if not isinstance(data, dict):
                    return {"teams": {}, "groups": {}, "last_attack_msg": None}
                if "teams" not in data:
                    data["teams"] = {}
                if "groups" not in data:
                    data["groups"] = {}
                if "last_attack_msg" not in data:
                    data["last_attack_msg"] = None
                return data
        except Exception:
            return {"teams": {}, "groups": {}, "last_attack_msg": None}
    return {
        "teams": {
            "admin": {"ip": "192.168.128.3", "role": "admin", "score": 0, "defense": 1000, "defenses_active": []}
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

state = cargar_estado()

st.title("🛡️ CYBER ARENA - PROTOCOLOS DE RED ⚔️")
st.markdown("---")

# ==========================================
# LOGIN / AUTENTICACIÓN
# ==========================================
st.sidebar.header("🔐 Acceso a la Plataforma")
login_user = st.sidebar.text_input("Nombre de Usuario / Grupo", value="")

if not login_user:
    st.info("👈 Ingresa tu nombre de grupo o 'admin' en la barra lateral para comenzar.")
    st.subheader("📋 Grupos Registrados en la Red")
    if state.get("groups"):
        preview_data = [{"Grupo": g, "IP Asignada": ip} for g, ip in state["groups"].items()]
        st.table(preview_data)
    else:
        st.warning("Aún no hay grupos creados. Entra como 'admin' para crearlos.")
    st.stop()

# Validar Administrador
if login_user.lower() == "admin":
    st.sidebar.success("✅ Sesión: ADMINISTRADOR")
    st.header("🛠️ Panel de Administración de Red")
    
    with st.form("form_crear_grupo"):
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
                        "defenses_active": [] # Lista de protocolos bloqueados
                    }
                else:
                    state["teams"][nuevo_grupo]["ip"] = nueva_ip
                guardar_estado(state)
                st.success(f"¡Grupo '{nuevo_grupo}' registrado con éxito!")
                st.rerun()

    st.subheader("📋 Estado Actual de la Red")
    if state["groups"]:
        admin_table = [{"Grupo": g, "IP Fija": ip} for g, ip in state["groups"].items()]
        st.table(admin_table)
    else:
        st.info("No hay grupos todavía.")
        
    if st.button("🗑️ Reiniciar Toda la Arena"):
        state["teams"] = {"admin": {"ip": "192.168.128.3", "role": "admin", "score": 0, "defense": 1000, "defenses_active": []}}
        state["groups"] = {}
        state["last_attack_msg"] = None
        guardar_estado(state)
        st.success("¡Arena reseteada!")
        st.rerun()
    st.stop()

# ==========================================
# VISTA DE EQUIPOS
# ==========================================
if login_user not in state["groups"]:
    st.error(f"[!] El usuario '{login_user}' no está registrado. Pídele al admin que cree tu grupo.")
    st.stop()

if login_user not in state["teams"]:
    state["teams"][login_user] = {
        "ip": state["groups"][login_user],
        "role": "team",
        "score": 0,
        "defense": 1000,
        "defenses_active": []
    }
    guardar_estado(state)

my_data = state["teams"][login_user]
my_ip = state["groups"][login_user]

st.sidebar.success(f"Sesión: **{login_user}**")
st.sidebar.info(f"IP: **{my_ip}**")

st.header(f"Panel de Control: {login_user}")

# Mostrar alertas de ataques en tiempo real
if state.get("last_attack_msg"):
    msg_info = state["last_attack_msg"]
    if msg_info["type"] == "success":
        st.success(msg_info["text"])
    else:
        st.error(msg_info["text"])

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Score de Ataque", value=my_data["score"])
with col2:
    st.metric(label="Salud Defensiva", value=my_data["defense"])

st.markdown("---")

# ==========================================
# PANEL DEFENSIVO (Seleccionar protocolos a blindar)
# ==========================================
st.subheader("🛡️ Panel Defensivo - Bloqueo de Protocolos (Blue Team)")
st.markdown("Selecciona qué protocolos deseas endurecer / bloquear con reglas de firewall y parches:")

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
# PANEL DE ATAQUE (Seleccionar protocolos a vulnerar)
# ==========================================
st.subheader("⚔️ Panel de Ataque - Escaneo de Protocolos (Red Team)")

rivales_disponibles = [g for g in state["groups"].keys() if g != login_user]

if not rivales_disponibles:
    st.warning("No hay otros grupos conectados para atacar.")
else:
    target_group = st.selectbox("Selecciona el Grupo Rival a Escanear/Atacar", rivales_disponibles)
    target_ip = state["groups"][target_group]
    st.text(f"IP Objetivo: {target_ip}")
    
    st.markdown("Selecciona los **protocolos que deseas atacar** en esta oleada:")
    protocolos_a_atacar = []
    for proto in PROTOCOLOS_DISPONIBLES:
        if st.checkbox(f"Atacar {proto}", key=f"atk_{proto}"):
            protocolos_a_atacar.append(proto)

    if st.button("⚡ Ejecutar Ataque por Protocolos Seleccionados", type="primary"):
        if not protocolos_a_atacar:
            st.error("Debes seleccionar al menos un protocolo para lanzar el ataque.")
        else:
            defender = state["teams"][target_group]
            defensas_rival = defender.get("defenses_active", [])
            
            # Evaluar qué protocolos pasaron y cuáles fueron bloqueados
            no_bloqueados = [p for p in protocolos_a_atacar if p not in defensas_rival]
            bloqueados = [p for p in protocolos_a_atacar if p in defensas_rival]
            
            puntos_ganados = len(no_bloqueados) * 100
            dano_defensa = len(no_bloqueados) * 100
            
            state["teams"][login_user]["score"] += puntos_ganados
            defender["defense"] = max(0, defender["defense"] - dano_defensa)
            
            if no_bloqueados:
                msg_text = f"[🚀 ¡BRECHA EXITOSA!] {login_user} atacó a {target_group} ({target_ip}). Protocolos vulnerables explotados: {', '.join(no_bloqueados)}. (+{puntos_ganados} pts)."
                msg_type = "success"
            else:
                msg_text = f"[❌ BLOQUEADO TOTAL] {target_group} tenía seguros todos los protocolos que intentaste atacar. Ninguna brecha abierta."
                msg_type = "error"
                
            if bloqueados:
                msg_text += f" (Bloqueados por el rival: {', '.join(bloqueados)})"

            state["last_attack_msg"] = {"type": msg_type, "text": msg_text}
            guardar_estado(state)
            st.rerun()

st.markdown("---")

# ==========================================
# ESTADO GENERAL DE LA RED
# ==========================================
st.subheader("📋 Estado General de la Red en Vivo")
table_data = []
for g, ip in state["groups"].items():
    t_data = state["teams"].get(g, {"score": 0, "defense": 1000, "defenses_active": []})
    table_data.append({
        "Grupo": g,
        "IP Fija": ip,
        "Score Ataque": t_data["score"],
        "Salud Defensiva": t_data["defense"],
        "Protocolos Asegurados": ", ".join([p.split()[0] for p in t_data.get("defenses_active", [])]) if t_data.get("defenses_active") else "Ninguno ⚠️"
    })

st.table(table_data)

if st.button("🔄 Actualizar Tablero"):
    st.rerun()
