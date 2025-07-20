import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gestione FMEA - AIAG VDA", layout="wide")

# ---- Dummy DB (in memoria) ----
if 'clienti' not in st.session_state:
    st.session_state.clienti = []
if 'prodotti' not in st.session_state:
    st.session_state.prodotti = []
if 'versioni' not in st.session_state:
    st.session_state.versioni = []
if 'fmea' not in st.session_state:
    st.session_state.fmea = {}

# ---- Sidebar: Menu principale ----
st.sidebar.title("Menu")
menu = st.sidebar.radio("Vai a", ["Clienti", "Prodotti", "Versioni Prodotto", "FMEA Processo"])

# ---- Clienti ----
if menu == "Clienti":
    st.title("Anagrafica Clienti")
    with st.form("nuovo_cliente"):
        codice = st.text_input("Codice Cliente")
        ragione = st.text_input("Ragione Sociale")
        email = st.text_input("Email")
        if st.form_submit_button("Aggiungi"):
            st.session_state.clienti.append({'codice': codice, 'ragione': ragione, 'email': email})
            st.success("Cliente aggiunto")
    st.write("**Elenco Clienti:**")
    df_clienti = pd.DataFrame(st.session_state.clienti)
    st.dataframe(df_clienti)

# ---- Prodotti ----
elif menu == "Prodotti":
    st.title("Catalogo Prodotti")
    if not st.session_state.clienti:
        st.warning("Aggiungi almeno un cliente prima di creare prodotti.")
    else:
        with st.form("nuovo_prodotto"):
            codice_p = st.text_input("Codice Prodotto")
            descrizione = st.text_input("Descrizione")
            cliente = st.selectbox("Cliente", [c['ragione'] for c in st.session_state.clienti])
            if st.form_submit_button("Aggiungi"):
                st.session_state.prodotti.append({'codice': codice_p, 'descrizione': descrizione, 'cliente': cliente})
                st.success("Prodotto aggiunto")
        st.write("**Elenco Prodotti:**")
        df_prod = pd.DataFrame(st.session_state.prodotti)
        st.dataframe(df_prod)

# ---- Versioni Prodotto ----
elif menu == "Versioni Prodotto":
    st.title("Versioni Prodotto")
    if not st.session_state.prodotti:
        st.warning("Aggiungi almeno un prodotto.")
    else:
        with st.form("nuova_versione"):
            prodotto = st.selectbox("Prodotto", [f"{p['codice']} - {p['descrizione']}" for p in st.session_state.prodotti])
            versione = st.text_input("Numero Versione (es: V1, V2...)")
            autore = st.text_input("Autore")
            note = st.text_area("Note")
            if st.form_submit_button("Aggiungi"):
                st.session_state.versioni.append({
                    'prodotto': prodotto, 'versione': versione,
                    'autore': autore, 'note': note, 'data': datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.success("Versione aggiunta")
        st.write("**Elenco Versioni:**")
        df_ver = pd.DataFrame(st.session_state.versioni)
        st.dataframe(df_ver)

# ---- FMEA Processo ----
elif menu == "FMEA Processo":
    st.title("Modulo FMEA Processo")
    if not st.session_state.versioni:
        st.warning("Crea almeno una versione prodotto prima di inserire FMEA.")
    else:
        versione = st.selectbox("Versione Prodotto", [f"{v['prodotto']} [{v['versione']}]" for v in st.session_state.versioni])
        key_fmea = versione
        # Inizializza FMEA se non esiste
        if key_fmea not in st.session_state.fmea:
            st.session_state.fmea[key_fmea] = pd.DataFrame(columns=[
                'Process Step', 'Failure Mode', 'Failure Effect', 'Failure Cause',
                'Prevention Controls', 'Detection Controls', 'Severity (S)',
                'Occurrence (O)', 'Detection (D)', 'AP', 'Action', 'Responsabile', 'Deadline', 'Stato Azione'
            ])

        st.write("**Tabella FMEA (AIAG-VDA)**")
        df = st.session_state.fmea[key_fmea]
        st.dataframe(df, use_container_width=True)
        
        with st.form("aggiungi_fmea"):
            step = st.text_input("Process Step")
            fm = st.text_input("Failure Mode")
            fe = st.text_input("Failure Effect")
            fc = st.text_input("Failure Cause")
            pc = st.text_input("Prevention Controls")
            dc = st.text_input("Detection Controls")
            s = st.number_input("Severity (S)", 1, 10)
            o = st.number_input("Occurrence (O)", 1, 10)
            d = st.number_input("Detection (D)", 1, 10)
            action = st.text_input("Azione Raccomandata")
            resp = st.text_input("Responsabile")
            deadline = st.date_input("Deadline")
            stato = st.selectbox("Stato Azione", ["Da fare", "In corso", "Completata"])
            if st.form_submit_button("Aggiungi riga FMEA"):
                ap = s * o * d # (oppure AP = funzione custom AIAG-VDA)
                new_row = {
                    'Process Step': step, 'Failure Mode': fm, 'Failure Effect': fe, 'Failure Cause': fc,
                    'Prevention Controls': pc, 'Detection Controls': dc, 'Severity (S)': s,
                    'Occurrence (O)': o, 'Detection (D)': d, 'AP': ap, 'Action': action,
                    'Responsabile': resp, 'Deadline': deadline, 'Stato Azione': stato
                }
                st.session_state.fmea[key_fmea] = st.session_state.fmea[key_fmea].append(new_row, ignore_index=True)
                st.success("Riga aggiunta!")

        if not df.empty:
            # Download Excel
            st.download_button(
                label="Scarica FMEA in Excel",
                data=df.to_excel(index=False, engine='openpyxl'),
                file_name=f"FMEA_{versione}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # Download PDF (come placeholder: esporta CSV)
            st.download_button(
                label="Scarica FMEA in CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name=f"FMEA_{versione}.csv",
                mime="text/csv"
            )
