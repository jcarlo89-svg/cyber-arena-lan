import streamlit as st
import json
import os

st.set_page_config(page_title="Cyber Arena - Admin & Teams", page_icon="🛡️", layout="centered")

DB_FILE = "arena_state.json"

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
            "admin": {"ip": "192.168.128.3", "role": "admin", "score": 0, "defense": 1000, "firewall": False, "patch": False}
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

st.title("🛡️ CYBER ARENA - GESTIÓN CENTRALIZADA ⚔️")
st.markdown("---")

# ==========================================
# LOGIN / AUTENTICACIÓN
# ==========================================
st.sidebar.header("🔐 Acceso a la Plataforma")
login_user = st.sidebar.text_input("Nombre de Usuario / Grupo", value="")

if not login_user:
    st.info("👈 Por favor, ingresa tu nombre de usuario o grupo en la barra lateral para iniciar sesión.")
    
    st.subheader("📋 Grupos Registrados en la Red")
    if state.get("groups"):
        preview_data = [{"Grupo": g, "IP Asignada": ip} for g, ip in state["groups"].items()]
        st.table(preview_data)
    else:
        st.warning("Aún no hay grupos creados. El administrador debe crearlos desde su panel.")
    st.stop()

# Validar si es Admin
if login_user.lower() == "admin":
    st.sidebar.success("✅ Sesión iniciada como: ADMINISTRADOR")
    
    st.header("🛠️ Panel de Administración de Red")
    st.markdown("Crea los grupos participantes y asígnales su IP fija en la red local.")
    
    with st.form("form_crear_grupo"):
        nuevo_grupo = st.text_input("Nombre del Nuevo Grupo (Ej. Equipo-Alfa)")
        nueva_ip = st.text_input("IP Fija en la Red (Ej. 192.168.128.15)")
        btn_crear = st.form_submit_button("Crear / Registrar Grupo")
        
        if btn_crear:
            if not nuevo_grupo or not nueva_ip:
                st.error("Completa ambos campos.")
            else:
                state["groups"][nuevo_grupo] = nueva_ip
                if nuevo_grupo not in state["teams"]:
                    state["teams"][nuevo_grupo] = {
                        "ip": nueva_ip,
                        "role": "team",
                        "score": 0,
                        "defense": 1000,
                        "firewall": False,
                        "patch": False
                    }
                else:
                    state["teams"][nuevo_grupo]["ip"] = nueva_ip
                guardar_estado(state)
                st.success(f"¡Grupo '{nuevo_grupo}' registrado con la IP {nueva_ip}!")
                st.rerun()

    st.subheader("📋 Estado Actual de Grupos y IPs")
    if state["groups"]:
        admin_table = [{"Grupo": g, "IP Fija": ip} for g, ip in state["groups"].items()]
        st.table(admin_table)
    else:
        st.info("No hay grupos creados todavía.")
        
    if st.button("🗑️ Reiniciar Toda la Arena (Resetear Puntajes)"):
        state["teams"] = {"admin": {"ip": "192.168.128.3", "role": "admin", "score": 0, "defense": 1000, "firewall": False, "patch": False}}
        state["groups"] = {}
        state["last_attack_msg"] = None
        guardar_estado(state)
        st.success("¡Arena reseteada por completo!")
        st.rerun()

    st.stop()

# ==========================================
# VISTA DE EQUIPOS / GRUPOS PARTICIPANTES
# ==========================================
if login_user not in state["groups"]:
    st.error(f"[!] El usuario '{login_user}' no está registrado en el sistema. Solicita al administrador que cree tu grupo.")
    st.stop()

if login_user not in state["teams"]:
    state["teams"][login_user] = {
        "ip": state["groups"][login_user],
        "role": "team",
        "score": 0,
        "defense": 1000,
        "firewall": False,
        "patch": False
    }
    guardar_estado(state)

my_data = state["teams"][login_user]
my_ip = state["groups"][login_user]

st.sidebar.success(f"Sesión activa: **{login_user}**")
st.sidebar.info(f"Tu IP en la Red: **{my_ip}**")

st.header(f"Panel de Control: {login_user}")

# Mostrar notificación global del último evento de ataque en la red
if state.get("last_attack_msg"):
    msg_info = state["last_attack_msg"]
    if msg_info["type"] == "success":
        st.success(msg_info["text"])
    else:
        st.error(msg_info["text"])

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Tu Score de Ataque", value=my_data["score"])
with col2:
    st.metric(label="Tu Salud Defensiva", value=my_data["defense"])

st.markdown("---")

st.subheader("🛡️ Panel Defensivo (Blue Team)")
col_fw, col_pt = st.columns(2)

with col_fw:
    fw_status = st.checkbox("Activar Firewall Anti-Brute", value=my_data["firewall"])
    if fw_status != my_data["firewall"]:
        state["teams"][login_user]["firewall"] = fw_status
        guardar_estado(state)
        st.rerun()

with col_pt:
    pt_status = st.checkbox("Activar Parche de Base de Datos", value=my_data["patch"])
    if pt_status != state["teams"][login_user]["patch"]:
        state["teams"][login_user]["patch"] = pt_status
        guardar_estado(state)
        st.rerun()

st.markdown("---")

st.subheader("⚔️ Panel de Ataque (Red Team)")

rivales_disponibles = [g for g in state["groups"].keys() if g != login_user]

if not rivales_disponibles:
    st.warning("No hay otros grupos disponibles en la red para atacar todavía.")
else:
    target_group = st.selectbox("Selecciona el Grupo Rival a Atacar", rivales_disponibles)
    target_ip = state["groups"][target_group]
    st.text(f"IP de destino seleccionada: {target_ip}")
    
    vector = st.selectbox("Vector de Ataque", ["Fuerza Bruta (Brute-force)", "Exfiltración / Exploit"])

    if st.button("⚡ Ejecutar Ataque por Red", type="primary"):
        defender = state["teams"][target_group]
        blocked = False
        
        if "Brute" in vector and defender["firewall"]:
            blocked = True
        elif "Exploit" in vector and defender["patch"]:
            blocked = True
            
        if blocked:
            state["teams"][login_user]["score"] += 10
            attack_msg = {
                "type": "error",
                "text": f"[❌ ATAQUE NO EXITOSO / BLOQUEADO] {login_user} intentó atacar a {target_group} ({target_ip}), ¡pero tenía la defensa activa! (+10 pts por intento fallido)."
            }
        else:
            state["teams"][login_user]["score"] += 150
            defender["defense"] = max(0, defender["defense"] - 150)
            attack_msg = {
                "type": "success",
                "text": f"[🚀 ¡ATAQUE EXITOSO!] {login_user} logró penetrar los sistemas de {target_group} ({target_ip}) con {vector}. (+150 pts de ataque / -150 salud defensiva)."
            }
            
        state["last_attack_msg"] = attack_msg
        guardar_estado(state)
        st.rerun()

st.markdown("---")

st.subheader("📋 Estado General de la Red en Vivo")
table_data = []
for g, ip in state["groups"].items():
    t_data = state["teams"].get(g, {"score": 0, "defense": 1000, "firewall": False, "patch": False})
    table_data.append({
        "Grupo": g,
        "IP Fija": ip,
        "Score Ataque": t_data["score"],
        "Defensa": t_data["defense"],
        "Firewall": "🛡️ ON" if t_data["firewall"] else "❌ OFF",
        "Parche": "🛡️ ON" if t_data["patch"] else "❌ OFF"
    })

st.table(table_data)

if st.button("🔄 Actualizar Tablero"):
    st.rerun()
