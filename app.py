import streamlit as st
import math

# --- DATENBANK & REGELN ---
produkte = {
    "Tafel": {"stueck_pro_blech": 40, "bleche_pro_wagen": 18, "max_teig": 800},
    "Tafel Teigling": {"stueck_pro_blech": 35, "bleche_pro_wagen": 13, "max_teig": 800},
    "Tafel Sonntag": {"stueck_pro_blech": 40, "bleche_pro_wagen": 18, "max_teig": 800},
    "Laugen": {"stueck_pro_blech": 45, "bleche_pro_wagen": 16, "max_teig": 750},
    "Laugen Teigling": {"stueck_pro_blech": 35, "bleche_pro_wagen": 13, "max_teig": 750},
    "Mühlenrädle": {"stueck_pro_blech": 35, "bleche_pro_wagen": 18, "max_teig": 750},
    "Milchbrötchen": {"stueck_pro_blech": 40, "bleche_pro_wagen": 18, "max_teig": 750},
    "Schnittbrötchen": {"stueck_pro_blech": 28, "bleche_pro_wagen": 18, "max_teig": 750}
}

def berechne_waegen(name, stueckzahl):
    if stueckzahl == 0: return None
    bleche = math.ceil(stueckzahl / produkte[name]["stueck_pro_blech"])
    volle_wagen = bleche // produkte[name]["bleche_pro_wagen"]
    rest_bleche = bleche % produkte[name]["bleche_pro_wagen"]
    return volle_wagen, rest_bleche, bleche

def berechne_teig(produkt_name, gesamt_stueck):
    if gesamt_stueck == 0: return None
    
    if gesamt_stueck % 5 != 0:
        gesamt_stueck = gesamt_stueck + (5 - (gesamt_stueck % 5))
        
    max_pro_teig = produkte[produkt_name]["max_teig"]
    
    if gesamt_stueck > max_pro_teig and (gesamt_stueck / 2) < 400:
        return 1, gesamt_stueck, 0, 0, gesamt_stueck
        
    anzahl_teige = math.ceil(gesamt_stueck / max_pro_teig)
    gesamt_reihen = gesamt_stueck // 5
    reihen_pro_teig = gesamt_reihen // anzahl_teige
    rest_reihen = gesamt_reihen % anzahl_teige
    standard_menge = reihen_pro_teig * 5
    
    return anzahl_teige, standard_menge, rest_reihen, anzahl_teige - rest_reihen, gesamt_stueck

# --- APP FRONTEND ---
st.set_page_config(page_title="Bäckerei Logistik", layout="wide")
st.title("🥐 Bäckerei Kommandozentrale")

col1, col2, col3 = st.columns(3)

with col1:
    st.header("📅 Täglich (Stück)")
    tafel_stk = st.number_input("Tafel (Standard)", min_value=0, step=5)
    
    # NEU: Die 3 Sondertafel-Produkte in 20er Schritten
    st.caption("Sondersorten Tafel (20er Schritte)")
    tafel_mohn_stk = st.number_input("Tafel Mohn", min_value=0, step=20)
    tafel_sesam_stk = st.number_input("Tafel Sesam", min_value=0, step=20)
    tafel_salz_stk = st.number_input("Tafel Salzkümmel", min_value=0, step=20)
    
    tafel_teig_stk = st.number_input("Tafel Teiglinge", min_value=0, step=5)
    st.markdown("---")
    laugen_stk = st.number_input("Laugen", min_value=0, step=5)
    laugen_teig_stk = st.number_input("Laugen Teiglinge", min_value=0, step=5)

with col2:
    st.header("❄️ Froster (Bleche)")
    muehlen_bl = st.number_input("Mühlenrädle (Bleche)", min_value=0, step=1)
    milch_bl = st.number_input("Milchbrötchen (Bleche)", min_value=0, step=1)
    schnitt_bl = st.number_input("Schnittbrötchen (Bleche)", min_value=0, step=1)

with col3:
    st.header("🔴 Wochenende Sonder")
    tafel_so_stk = st.number_input("Tafel Sonntag", min_value=0, step=5)
    st.markdown("*(Zusatzmengen für So. werden zu Sa. addiert)*")
    laugen_so_stk = st.number_input("+ Laugen Sonntag", min_value=0, step=5)
    laugen_teig_so_stk = st.number_input("+ Laugen Teiglinge So.", min_value=0, step=5)
    schnitt_so_bl = st.number_input("+ Schnittbrötchen So. (Bleche)", min_value=0, step=1)

# --- BERECHNUNG & AUSGABE ---
if st.button("🚀 Alles Berechnen", use_container_width=True, type="primary"):
    
    # 1. Daten aggregieren
    summe_tafel = tafel_stk + tafel_mohn_stk + tafel_sesam_stk + tafel_salz_stk
    summe_laugen = laugen_stk + laugen_so_stk
    summe_laugen_teig = laugen_teig_stk + laugen_teig_so_stk
    
    summe_muehlen = muehlen_bl * produkte["Mühlenrädle"]["stueck_pro_blech"]
    summe_milch = milch_bl * produkte["Milchbrötchen"]["stueck_pro_blech"]
    summe_schnitt = (schnitt_bl + schnitt_so_bl) * produkte["Schnittbrötchen"]["stueck_pro_blech"]
    
    st.markdown("---")
    st.header("📋 Produktionsplan")
    
    out_col1, out_col2 = st.columns(2)
    
    with out_col1:
        st.subheader("🛒 Wägen & Bleche")
        auftraege_waegen = [
            ("Tafel", summe_tafel), ("Tafel Teigling", tafel_teig_stk), ("Tafel Sonntag", tafel_so_stk),
            ("Laugen", summe_laugen), ("Laugen Teigling", summe_laugen_teig),
            ("Mühlenrädle", summe_muehlen), ("Milchbrötchen", summe_milch), ("Schnittbrötchen", summe_schnitt)
        ]
        
        for name, menge in auftraege_waegen:
            res = berechne_waegen(name, menge)
            if res:
                v_wagen, r_bleche, total_bleche = res
                
                # SONDERFALL 1: Laugen Teiglinge (Gleichmäßig auf 2 Wägen verteilen)
                if name == "Laugen Teigling":
                    w1 = math.ceil(total_bleche / 2)
                    w2 = total_bleche // 2
                    st.success(f"**{name}** ({menge} Stk): Aufgeteilt auf 2 Wägen 👉 1x {w1} Bleche & 1x {w2} Bleche")
                
                # SONDERFALL 2: Tafel Teiglinge (6 Bleche in Sonderwagen)
                elif name == "Tafel Teigling":
                    if total_bleche >= 6:
                        rest_nach_sonder = total_bleche - 6
                        vw = rest_nach_sonder // produkte[name]["bleche_pro_wagen"]
                        rb = rest_nach_sonder % produkte[name]["bleche_pro_wagen"]
                        rest_str = f" + 1 Wagen mit {rb} Blechen" if rb > 0 else ""
                        st.success(f"**{name}** ({menge} Stk): 1 Sonder-Wagen (6 Bleche) + {vw} volle Wägen{rest_str}")
                    else:
                        st.success(f"**{name}** ({menge} Stk): 1 Sonder-Wagen mit {total_bleche} Blechen")
                
                # STANDARD-PRODUKTE
                else:
                    rest_str = f" + 1 Wagen mit {r_bleche} Blechen" if r_bleche > 0 else ""
                    st.success(f"**{name}** ({menge} Stk): {v_wagen} volle Wägen{rest_str}")

    with out_col2:
        st.subheader("🥣 Teigbestellung")
        
        teig_auftraege = [
            ("Tafel", summe_tafel + tafel_teig_stk, "Tafel (Gesamt inkl. Sondersorten & Teiglinge)"),
            ("Tafel Sonntag", tafel_so_stk, "Tafel Sonntag"),
            ("Laugen", summe_laugen + summe_laugen_teig, "Laugen (inkl. Teiglinge)"),
            ("Mühlenrädle", summe_muehlen, "Mühlenrädle"),
            ("Milchbrötchen", summe_milch, "Milchbrötchen"),
            ("Schnittbrötchen", summe_schnitt, "Schnittbrötchen")
        ]
        
        for p_name, menge, label in teig_auftraege:
            res = berechne_teig(p_name, menge)
            if res:
                a_teige, s_menge, r_reihen, t_normal, finale_stk = res
                st.warning(f"**{label}** (Total: {finale_stk} Stk)")
                if r_reihen == 0:
                    st.write(f"👉 {a_teige}x Teig à {s_menge} Stück")
                else:
                    st.write(f"👉 {t_normal}x Teig à {s_menge} Stück  |  {r_reihen}x Teig à {s_menge + 5} Stück")
