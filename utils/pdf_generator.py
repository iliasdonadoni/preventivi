from fpdf import FPDF
from datetime import datetime
import os


class PDF(FPDF):

    def header(self):
        self.image("static/logo.jpg", 10, 8, 25)
        self.set_font("Arial", 'B', 12)
        self.set_xy(140, 10)
        self.multi_cell(
            60, 5,
            "Ilias Donadoni – Quote App\nConsulente IT\nTel: +41 76 572 04 09\ninfo@iliasdonadoni.ch",
            0, 'R')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", 'I', 8)
        self.cell(0, 10, f"Pagina {self.page_no()}", 0, 0, 'C')


def genera_pdf(data):
    ore = 2  # consulenza base
    costo_ora = 140

    MODULI_ORE = {
        "form contatto": 1.0,
        "slider immagini": 2.0,
        "galleria immagini": 2.0,
        "descrizione azienda": 0.5,
        "team": 1.0,
        "partner": 1.0,
        "sponsor": 1.0,
        "mission": 1.0,
        "storia": 1.0,
        "mappa": 1.0,
        "home base": 2.0,
        "servizi": 1.0,
        "listino prezzi": 0.5,
        "faq": 2.0,
        "area download": 2.5,
        "blog": 2.5,
        "valori": 1.5,
        "testimonianze": 1.5,
        "video": 2.0,
        "call to action": 0.5,
        "social media": 2.5,
        "recensioni google": 1.5,
        "live chat": 1.0,
        "newsletter": 2.5,
        "orari apertura": 1.0
    }

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Struttura Pagine e Moduli", 0, 1)

    # Tabella dettagliata
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(50, 8, "Pagina", 1, 0, 'C', 1)
    pdf.cell(70, 8, "Modulo", 1, 0, 'C', 1)
    pdf.cell(20, 8, "Ore", 1, 0, 'C', 1)
    pdf.cell(30, 8, "CHF", 1, 1, 'C', 1)

    pagine = data.get("pagine_dettaglio", {})
    for pagina, moduli in pagine.items():
        for m in moduli:
            mod_ore = MODULI_ORE.get(m, 0.5)
            mod_costo = mod_ore * costo_ora
            ore += mod_ore
            pdf.set_font("Arial", '', 10)
            pdf.cell(50, 8, clean_for_pdf(normalize_text(pagina)), 1)
            pdf.cell(70, 8, clean_for_pdf(normalize_text(m)), 1)
            pdf.cell(20, 8, f"{mod_ore:.1f}", 1, 0, 'C')
            pdf.cell(30, 8, f"{mod_costo:.2f}", 1, 1, 'C')

    # Funzionalità extra
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Funzionalità Extra", 0, 1)

    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(60, 8, "Funzione", 1, 0, 'C', 1)
    pdf.cell(70, 8, "Tipo / Modalità", 1, 0, 'C', 1)
    pdf.cell(20, 8, "Ore", 1, 0, 'C', 1)
    pdf.cell(30, 8, "CHF", 1, 1, 'C', 1)

    f = data.get('features', {})
    for k, v in f.items():
        if v:
            f_ore = 2 if k in ['eventi', 'prenotazioni', 'appuntamenti'] else 1
            f_cost = f_ore * costo_ora
            ore += f_ore
            pdf.set_font("Arial", '', 10)
            pdf.cell(60, 8, clean_for_pdf(k.capitalize()), 1)
            pdf.cell(70, 8, clean_for_pdf(str(v)), 1)
            pdf.cell(20, 8, f"{f_ore}", 1, 0, 'C')
            pdf.cell(30, 8, f"{f_cost:.2f}", 1, 1, 'C')

    # Totale
    ore += 5  # gestione e documentazione
    totale = ore * costo_ora

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(150, 10,
             "Totale preventivo (incl. documentazione e configurazione)", 1)
    pdf.cell(30, 10, f"CHF {totale:.2f}", 1, 1, 'C')

    # Info cliente
    pdf.ln(10)
    pdf.set_font("Arial", '', 10)
    cliente_info = f"Cliente: {data.get('cliente_nome', '')} - {data.get('cliente_email', '')} [{data.get('cliente_azienda', '')}]"
    pdf.multi_cell(0, 6, clean_for_pdf(normalize_text(cliente_info)))

    # Seconda pagina: documentazione
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "📑 Documentazione del Preventivo", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.ln(4)
    pdf.multi_cell(
        0, 6,
        clean_for_pdf("""
Questo preventivo è stato generato automaticamente tramite l'app 'Quote App' sviluppata da Ilias Donadoni.

 **Algoritmo di calcolo**:
- Ogni modulo ha un tempo stimato di sviluppo in ore
- Ogni funzionalità ha un peso in base alla modalità scelta (visualizzazione, email, app)
- Le ore vengono sommate a una base fissa per la consulenza e la documentazione
- Costo orario: CHF 140/h

 **Autenticazione**:
- Firma digitale automatica con data/ora
- Tutto il contenuto è stato generato sulla base delle scelte del cliente

"""))
    pdf.ln(5)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0,
             6,
             f"Data generazione: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
             ln=True)
    pdf.cell(0, 6, "Consulente: Ilias Donadoni", ln=True)

    # Output
    fname = f"quote_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    path = os.path.join("static", fname)
    pdf.output(path)
    return path, ore, totale


import unicodedata


def normalize_text(text):
    if not text:
        return ''
    # Rimuove accenti e simboli non supportati da latin-1
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('latin-1', errors='ignore').decode('latin-1')
    return text.replace("–", "-").replace("—", "-").replace("‘", "'") \
               .replace("’", "'").replace("“", '"').replace("”", '"')


def clean_for_pdf(s):
    return s.encode('latin-1', errors='replace').decode('latin-1')
