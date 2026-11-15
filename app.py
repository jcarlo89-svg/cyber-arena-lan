import streamlit as st
import json
import os

st.set_page_config(page_title="Cyber Arena - Admin & Teams", page_icon="🛡️", layout="centered")

DB_FILE = "arena_state.json"

def cargar_estado():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                # Asegurar que existan todas las llaves necesarias
                if not isinstance(data, dict):
                    return {"teams": {}, "groups": {}}
                if "teams" not in data:
                    data["teams"] = {}
                if "groups" not in data:
                    data["groups"] = {}
                return data
        except:
            return {"teams": {}, "groups": {}}
    return {
        "teams": {
            "admin": {"ip": "192.168.128.3", "role": "admin", "score": 0, "defense": 1000, "firewall": False, "patch": False}
        },
        "groups": {}
    }

def guardar_estado(state):
    with open(DB_FILE, "w") as f:
        json.dump(state, f)

state = cargar_estado()
