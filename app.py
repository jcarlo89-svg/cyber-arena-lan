import streamlit as st
import json
import os

# Configuración de la página
st.set_page_config(page_title="Cyber Arena - Cloud", page_icon="🛡️", layout="centered")

# Archivo JSON local para persistir el estado de la sesión en la nube
DB_FILE = "arena_state.json"

def cargar_estado():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def guardar_estado(state):
    with open(DB_FILE, "w") as f:
        json.dump(state, f)

# Inicializar estado global
state = cargar_estado()

st.title("🛡️ CYBER ARENA - RED TEAM vs BLUE TEAM ⚔️")
st.markdown("---")

# Registro de equipo local en la sesión actual
st.sidebar.header("⚙️ Tus Credenciales")
my_name = st.sidebar.text_input("Nombre de tu Equipo", value="Equipo-Alfa")
my_ip = st.sidebar.text_input("Tu IP / Identificador", value="192.168.1.50")

if not my_name or not my_ip:
    st.warning("Por favor ingresa tu nombre e IP para participar.")
    st.stop()

# Registrar o actualizar equipo en el estado global
if my_name not in state:
    state[my_name] = {
        "ip": my_ip,
        "score": 0,
        "defense": 1000,
        "firewall": False,
        "patch": False
    }
    guardar_estado(state)

# Actualizar IP si cambió
state[my_name]["ip"] = my_ip
guardar_estado(state)

# Mostrar métricas del equipo actual
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Tu Score de Ataque", value=state[my_name]["score"])
with col2:
    st.metric(label="Tu Salud Defensiva", value=state[my_name]["defense"])

st.markdown("---")

# Panel Defensivo (Blue Team)
st.subheader("🛡️ Panel Defensivo (Blue Team)")
col_fw, col_pt = st.columns(2)

with col_fw:
    fw_status = st.checkbox("Activar Firewall Anti-Brute", value=state[my_name]["firewall"])
    if fw_status != state[my_name]["firewall"]:
        state[my_name]["firewall"] = fw_status
        guardar_estado(state)
        st.rerun()

with col_pt:
    pt_status = st.checkbox("Activar Parche de Base de Datos", value=state[my_name]["patch"])
    if pt_status != state[my_name]["patch"]:
        state[my_name]["patch"] = pt_status
        guardar_estado(state)
        st.rerun()

st.markdown("---")

# Panel de Ataque (Red Team)
st.subheader("⚔️ Panel de Ataque (Red Team)")
target_name = st.text_input("Nombre del Equipo Rival a Atacar", placeholder="Ej. Equipo-Bravo")
vector = st.selectbox("Vector de Ataque", ["Fuerza Bruta (Brute-force)", "Exfiltración / Exploit"])

if st.button("⚡ Ejecutar Ataque por Red", type="primary"):
    if not target_name:
        st.error("Escribe el nombre del equipo rival.")
    elif target_name == my_name:
        st.error("No puedes atacarte a ti mismo.")
    elif target_name not in state:
        st.error(f"[!] ERROR DE RED: El equipo '{target_name}' no está conectado o no existe.")
    else:
        defender = state[target_name]
        blocked = False
        
        # Evaluar lógica de escudos
        if "Brute" in vector and defender["firewall"]:
            blocked = True
        elif "Exploit" in vector and defender["patch"]:
            blocked = True
            
        if blocked:
            state[my_name]["score"] += 10
            guardar_estado(state)
            st.warning(f"[X] BLOQUEADO: {target_name} tiene la defensa activa contra este vector. (+10 pts por intento)")
        else:
            state[my_name]["score"] += 150
            state[target_name]["defense"] = max(0, state[target_name]["defense"] - 150)
            guardar_estado(state)
            st.success(f"[!!!] ¡Ataque exitoso contra {target_name}! Brecha abierta. (+150 pts)")
        st.rerun()

st.markdown("---")

# Tabla de Posiciones en Vivo (Estado de la Red)
st.subheader("📋 Estado General de la Red en Vivo")
table_data = []
for name, data in state.items():
    table_data.append({
        "Equipo": name,
        "IP": data["ip"],
        "Score Ataque": data["score"],
        "Defensa": data["defense"],
        "Firewall": "🛡️ ON" if data["firewall"] else "❌ OFF",
        "Parche": "🛡️ ON" if data["patch"] else "❌ OFF"
    })

st.table(table_data)

# Botón para refrescar la vista de la red
if st.button("🔄 Actualizar Tablero"):
    st.rerun()