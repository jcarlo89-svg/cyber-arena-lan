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
        state["teams"] = {"admin": {"ip": "192.168.128
