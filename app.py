import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from typing import Dict, List

# =======================
# Configurazione App & Dati Base
# =======================
st.set_page_config(page_title="Gestione Qualità Automotive - AIAG VDA", layout="wide")

LINGUE = {"IT": "Italiano", "EN": "English", "DE": "Deutsch"}
RUOLI = {
    "admin": "Admin",
    "qe": "Quality Engineer",
    "viewer": "Viewer",
    "supplier": "Supplier",
    "customer": "Customer"
}
# Demo users
UTENTI = [
    {"username": "admin", "password": "admin", "ruolo": "admin", "lang": "IT"},
    {"username": "quality", "password": "quality", "ruolo": "qe", "lang": "EN"},
    {"username": "user", "password": "user", "ruolo": "viewer", "lang": "DE"},
]

if "utente" not in st.session_state:
    st.session_state.utente = None

if "lang" not in st.session_state:
    st.session_state.lang = "IT"

if "audit_log" not in st.session_state:
    st.session_state.audit_log = []

# =======================
# Utility traduzioni
# =======================
def _(msg):
    # Demo semplice: puoi espandere con un dict per ogni lingua
    strings = {
        "Benvenuto": {"IT": "Benvenuto", "EN": "Welcome", "DE": "Willkommen"},
        "Logout": {"IT": "Logout", "EN": "Logout", "DE": "Logout"},
        "Login": {"IT": "Accedi", "EN": "Login", "DE": "Login"},
        "Seleziona lingua": {"IT": "Seleziona lingua", "EN": "Select language", "DE": "Sprache wählen"},
        "Username": {"IT": "Username", "EN": "Username", "DE": "Benutzername"},
        "Password": {"IT": "Password", "EN": "Password", "DE": "Passwort"},
        "Ruolo": {"IT": "Ruolo", "EN": "Role", "DE": "Rolle"},
        "Clienti": {"IT": "Clienti", "EN": "Customers", "DE": "Kunden"},
        "Prodotti": {"IT": "Prodotti", "EN": "Products", "DE": "Produkte"},
        "Versioni": {"IT": "Versioni", "EN": "Versions", "DE": "Versionen"},
        "Flowchart": {"IT": "Flowchart", "EN": "Flowchart", "DE": "Ablaufdiagramm"},
        "FMEA": {"IT": "FMEA", "EN": "FMEA", "DE": "FMEA"},
        "Control Plan": {"IT": "Control Plan", "EN": "Control Plan", "DE": "Control Plan"},
        "Documenti": {"IT": "Documenti", "EN": "Documents", "DE": "Dokumente"},
        "Dashboard": {"IT": "Dashboard", "EN": "Dashboard", "DE": "Dashboard"},
        "Audit Log": {"IT": "Audit Log", "EN": "Audit Log", "DE": "Audit Log"},
        "Utenti": {"IT": "Utenti", "EN": "Users", "DE": "Benutzer"},
        "Anagrafica Clienti": {"IT": "Anagrafica Clienti", "EN": "Customer Registry", "DE": "Kundenverwaltung"},
        "Catalogo Prodotti": {"IT": "Catalogo Prodotti", "EN": "Product Catalog", "DE": "Produktkatalog"},
        "Versioni Prodotto": {"IT": "Versioni Prodotto", "EN": "Product Versions", "DE": "Produktversionen"},
        "Gestione Documenti": {"IT": "Gestione Documenti", "EN": "Document Management", "DE": "Dokumentenmanagement"},
        "Modifica": {"IT": "Modifica", "EN": "Edit", "DE": "Bearbeiten"},
        "Elimina": {"IT": "Elimina", "EN": "Delete", "DE": "Löschen"},
        "Scarica": {"IT": "Scarica", "EN": "Download", "DE": "Herunterladen"},
        # ... espandi a piacere
    }
    return strings.get(msg, {}).get(st.session_state.lang, msg)

# =======================
# Login, Lingua, Permessi
# =======================
def login():
    st.sidebar.title(_("Login"))
    st.session_state.lang = st.sidebar.selectbox(_("Seleziona lingua"), list(LINGUE.keys()), format_func=lambda k: LINGUE[k])
    username = st.sidebar.text_input(_("Username"))
    password = st.sidebar.text_input(_("Password"), type="password")
    if st.sidebar.button(_("Login")):
        utente = next((u for u in UTENTI if u["username"] == username and u["password"] == password), None)
        if utente:
            st.session_state.utente = utente
            st.session_state.lang = utente["lang"]
            st.success(_("Benvenuto") + f", {utente['username']} ({RUOLI[utente['ruolo']]})")
        else:
            st.error("Credenziali errate")

if not st.session_state.utente:
    login()
    st.stop()
else:
    st.sidebar.write(f"{_('Benvenuto')}, **{st.session_state.utente['username']}** ({RUOLI[st.session_state.utente['ruolo']]})")
    if st.sidebar.button(_("Logout")):
        st.session_state.utente = None
        st.experimental_rerun()
    st.sidebar.selectbox(_("Seleziona lingua"), list(LINGUE.keys()), key="lang", format_func=lambda k: LINGUE[k])

PERMESSI = {
    "admin": {"create": True, "edit": True, "approve": True, "read": True},
    "qe": {"create": True, "edit": True, "approve": False, "read": True},
    "viewer": {"create": False, "edit": False, "approve": False, "read": True},
    "supplier": {"create": True, "edit": True, "approve": False, "read": True},
    "customer": {"create": False, "edit": False, "approve": False, "read": True},
}
def can(p):
    ruolo = st.session_state.utente['ruolo']
    return PERMESSI.get(ruolo, {}).get(p, False)

# =======================
# Dati In-Memory (demo)
# =======================
def init_list(k):  # Helper
    if k not in st.session_state:
        st.session_state[k] = []

for k in [
    "clienti", "prodotti", "versioni", "flowcharts", "fmea", "controlplan", "documenti", "revisioni", "commenti"
]:
    init_list(k)

# =======================
# Sidebar menu
# =======================
MENU = [
    _("Dashboard"),
    _("Clienti"),
    _("Prodotti"),
    _("Versioni"),
    _("Flowchart"),
    _("FMEA"),
    _("Control Plan"),
    _("Documenti"),
    _("Audit Log"),
    _("Utenti"),
]
sel = st.sidebar.radio("Menu", MENU)

# =======================
# Dashboard
# =======================
if sel == _("Dashboard"):
    st.title(_("Dashboard"))
    col1, col2 = st.columns(2)
    with col1:
        st.metric(_("Clienti"), len(st.session_state.clienti))
        st.metric(_("Prodotti"), len(st.session_state.prodotti))
    with col2:
        st.metric(_("FMEA"), sum(len(f["righe"]) for f in st.session_state.fmea))
        st.metric(_("Control Plan"), len(st.session_state.controlplan))
    st.write("Ultime modifiche/documenti:")
    st.dataframe(pd.DataFrame(st.session_state.documenti).tail(5))

# =======================
# Clienti
# =======================
if sel == _("Clienti"):
    st.title(_("Anagrafica Clienti"))
    if can("create"):
        with st.form("nuovo_cliente"):
            codice = st.text_input("Codice Cliente")
            ragione = st.text_input("Ragione Sociale")
            email = st.text_input("Email")
            if st.form_submit_button("Aggiungi"):
                st.session_state.clienti.append({
                    "id": str(uuid.uuid4()), "codice": codice, "ragione": ragione, "email": email,
                })
                st.session_state.audit_log.append({"tipo":"cliente","azione":"create","utente":st.session_state.utente["username"],"orario":str(datetime.now()),"dati": codice})
                st.success("Cliente aggiunto")
    df_clienti = pd.DataFrame(st.session_state.clienti)
    st.dataframe(df_clienti)
    if can("edit"):
        idx = st.selectbox("Seleziona cliente per modifica", options=df_clienti.index, format_func=lambda i: df_clienti.loc[i]["ragione"] if not df_clienti.empty else "")
        if st.button(_("Modifica")) and not df_clienti.empty:
            st.session_state.clienti[idx]["ragione"] = st.text_input("Nuova ragione sociale", value=st.session_state.clienti[idx]["ragione"])
            st.success("Modifica demo")

# =======================
# Prodotti
# =======================
if sel == _("Prodotti"):
    st.title(_("Catalogo Prodotti"))
    if can("create"):
        with st.form("nuovo_prodotto"):
            codice_p = st.text_input("Codice Prodotto")
            descrizione = st.text_input("Descrizione")
            cliente = st.selectbox("Cliente", [c["ragione"] for c in st.session_state.clienti]) if st.session_state.clienti else ""
            if st.form_submit_button("Aggiungi"):
                st.session_state.prodotti.append({
                    "id": str(uuid.uuid4()), "codice": codice_p, "descrizione": descrizione, "cliente": cliente
                })
                st.session_state.audit_log.append({"tipo":"prodotto","azione":"create","utente":st.session_state.utente["username"],"orario":str(datetime.now()),"dati": codice_p})
                st.success("Prodotto aggiunto")
    df_prodotti = pd.DataFrame(st.session_state.prodotti)
    st.dataframe(df_prodotti)

# =======================
# Versioni
# =======================
if sel == _("Versioni"):
    st.title(_("Versioni Prodotto"))
    if can("create"):
        with st.form("nuova_versione"):
            prodotto = st.selectbox("Prodotto", [f"{p['codice']} - {p['descrizione']}" for p in st.session_state.prodotti]) if st.session_state.prodotti else ""
            versione = st.text_input("Numero Versione (es: V1, V2...)")
            autore = st.text_input("Autore")
            note = st.text_area("Note")
            if st.form_submit_button("Aggiungi"):
                st.session_state.versioni.append({
                    "id": str(uuid.uuid4()),
                    "prodotto": prodotto,
                    "versione": versione,
                    "autore": autore,
                    "note": note,
                    "data": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.success("Versione aggiunta")
    df_ver = pd.DataFrame(st.session_state.versioni)
    st.dataframe(df_ver)

# =======================
# Flowchart (editor demo)
# =======================
if sel == _("Flowchart"):
    st.title(_("Flowchart"))
    if can("create"):
        with st.form("nuovo_flowchart"):
            versione = st.selectbox("Versione prodotto", [f"{v['prodotto']} [{v['versione']}]" for v in st.session_state.versioni]) if st.session_state.versioni else ""
            editor = st.text_area("Flowchart (editor demo)", placeholder="Inizio -> Attività -> Decisione -> Fine")
            if st.form_submit_button("Salva"):
                st.session_state.flowcharts.append({
                    "id": str(uuid.uuid4()), "versione": versione,
                    "flowchart": editor, "autore": st.session_state.utente["username"], "data": str(datetime.now())
                })
                st.success("Flowchart salvato (testo, per demo)")
    st.write("Flowchart salvati:")
    df_fc = pd.DataFrame(st.session_state.flowcharts)
    st.dataframe(df_fc)

# =======================
# FMEA
# =======================
if sel == _("FMEA"):
    st.title(_("FMEA (AIAG-VDA 2019)"))
    if can("create"):
        with st.form("nuova_fmea"):
            versione = st.selectbox("Versione prodotto", [f"{v['prodotto']} [{v['versione']}]" for v in st.session_state.versioni]) if st.session_state.versioni else ""
            tipo = st.selectbox("Tipo FMEA", ["Design", "Process"])
            # 7 Step AIAG-VDA
            step = st.text_input("Process Step")
            fm = st.text_input("Failure Mode")
            fe = st.text_input("Failure Effect")
            fc = st.text_input("Failure Cause")
            pc = st.text_input("Prevention Controls")
            dc = st.text_input("Detection Controls")
            s = st.number_input("Severity (S)", 1, 10)
            o = st.number_input("Occurrence (O)", 1, 10)
            d = st.number_input("Detection (D)", 1, 10)
            ap = s * o * d  # Sostituisci con AP se hai logica custom
            azione = st.text_input("Azione Raccomandata")
            responsabile = st.text_input("Responsabile")
            deadline = st.date_input("Deadline")
            stato = st.selectbox("Stato Azione", ["Da fare", "In corso", "Completata"])
            if st.form_submit_button("Aggiungi FMEA"):
                st.session_state.fmea.append({
                    "id": str(uuid.uuid4()), "versione": versione, "tipo": tipo,
                    "righe": [{
                        "Process Step": step, "Failure Mode": fm, "Failure Effect": fe, "Failure Cause": fc,
                        "Prevention Controls": pc, "Detection Controls": dc,
                        "S": s, "O": o, "D": d, "AP": ap, "Action": azione,
                        "Responsabile": responsabile, "Deadline": deadline, "Stato Azione": stato,
                    }],
                    "autore": st.session_state.utente["username"],
                    "data": str(datetime.now())
                })
                st.success("FMEA aggiunta")
    # Elenco FMEA
    tab = []
    for f in st.session_state.fmea:
        for r in f["righe"]:
            t = f.copy(); t.pop("righe")
            tab.append({**t, **r})
    if tab:
        st.dataframe(pd.DataFrame(tab))
        st.download_button("Scarica FMEA CSV", pd.DataFrame(tab).to_csv(index=False), file_name="fmea.csv")
    else:
        st.info("Nessuna FMEA presente.")

# =======================
# Control Plan
# =======================
if sel == _("Control Plan"):
    st.title(_("Control Plan"))
    if can("create"):
        with st.form("nuovo_cp"):
            versione = st.selectbox("Versione prodotto", [f"{v['prodotto']} [{v['versione']}]" for v in st.session_state.versioni]) if st.session_state.versioni else ""
            caratteristica = st.text_input("Caratteristica di controllo")
            frequenza = st.text_input("Frequenza")
            metodo = st.text_input("Metodo")
            reazione = st.text_input("Reazione")
            linkage = st.text_input("Linkage APQP/PPAP")
            if st.form_submit_button("Aggiungi CP"):
                st.session_state.controlplan.append({
                    "id": str(uuid.uuid4()), "versione": versione,
                    "caratteristica": caratteristica,
                    "frequenza": frequenza, "metodo": metodo, "reazione": reazione, "linkage": linkage,
                    "autore": st.session_state.utente["username"], "data": str(datetime.now())
                })
                st.success("Control Plan aggiunto")
    st.dataframe(pd.DataFrame(st.session_state.controlplan))

# =======================
# Documenti e Revisioni
# =======================
if sel == _("Documenti"):
    st.title(_("Gestione Documenti"))
    if can("create"):
        with st.form("nuovo_doc"):
            versione = st.selectbox("Versione prodotto", [f"{v['prodotto']} [{v['versione']}]" for v in st.session_state.versioni]) if st.session_state.versioni else ""
            tipo_doc = st.selectbox("Tipo documento", ["FMEA", "Flowchart", "Control Plan", "Altro"])
            file = st.file_uploader("Carica file", type=["pdf", "xlsx", "csv"])
            note = st.text_area("Note revisione")
            if st.form_submit_button("Carica"):
                st.session_state.documenti.append({
                    "id": str(uuid.uuid4()), "versione": versione, "tipo_doc": tipo_doc, "file": file.name if file else "",
                    "autore": st.session_state.utente["username"], "data": str(datetime.now()), "note": note
                })
                st.session_state.revisioni.append({
                    "id": str(uuid.uuid4()), "doc": st.session_state.documenti[-1]["id"], "autore": st.session_state.utente["username"],
                    "note": note, "data": str(datetime.now())
                })
                st.success("Documento caricato")
    st.write("Documenti caricati:")
    st.dataframe(pd.DataFrame(st.session_state.documenti))

# =======================
# Audit Log
# =======================
if sel == _("Audit Log"):
    st.title(_("Audit Log"))
    st.dataframe(pd.DataFrame(st.session_state.audit_log))

# =======================
# Utenti (demo)
# =======================
if sel == _("Utenti"):
    st.title(_("Utenti"))
    df_utenti = pd.DataFrame(UTENTI)
    st.dataframe(df_utenti)

# =======================
# Simulazione AI Assistente (suggerimenti)
# =======================
st.sidebar.title("AI Assistant")
if st.sidebar.button("Suggerisci Failure Modes (Demo)"):
    try:
        import openai
        openai.api_key = st.secrets.get("OPENAI_API_KEY", "")
        prompt = "Suggerisci 3 failure mode tipici per un processo di saldatura in automotive secondo FMEA AIAG-VDA 2019."
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[
            {"role":"system","content":"Sei un esperto automotive quality engineer."},
            {"role":"user","content": prompt}
        ])
        st.sidebar.info(response.choices[0].message.content)
    except Exception as e:
        st.sidebar.warning("Configura OPENAI_API_KEY in Streamlit Secrets per usare questa funzione.")

# =======================
# Fine App
# =======================

