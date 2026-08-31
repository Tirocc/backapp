import math

import streamlit as st


# --- DATENBANK & REGELN ---
TAFEL_EXTRA = 210
MINDEST_TEIG = 400

PRODUKTE = {
    "Tafel": {"stueck_pro_blech": 40, "bleche_pro_wagen": 18, "max_teig": 800},
    "Tafel Teigling": {"stueck_pro_blech": 35, "bleche_pro_wagen": 13, "max_teig": 800},
    "Tafel Sonntag": {"stueck_pro_blech": 40, "bleche_pro_wagen": 18, "max_teig": 800},
    "Laugen": {"stueck_pro_blech": 45, "bleche_pro_wagen": 16, "max_teig": 750},
    "Laugen Teigling": {"stueck_pro_blech": 35, "bleche_pro_wagen": 13, "max_teig": 750},
    "Mühlenrädle": {"stueck_pro_blech": 35, "bleche_pro_wagen": 18, "max_teig": 750},
    "Milchbrötchen": {"stueck_pro_blech": 40, "bleche_pro_wagen": 18, "max_teig": 750},
    "Schnittbrötchen": {"stueck_pro_blech": 28, "bleche_pro_wagen": 18, "max_teig": 750},
}


def berechne_wagen(produkt_name, stueckzahl):
    if stueckzahl <= 0:
        return None

    produkt = PRODUKTE[produkt_name]
    bleche = math.ceil(stueckzahl / produkt["stueck_pro_blech"])
    volle_wagen, rest_bleche = divmod(bleche, produkt["bleche_pro_wagen"])
    return volle_wagen, rest_bleche, bleche


def berechne_teig(produkt_name, gesamt_stueck):
    """Verteilt die Menge in 5er-Schritten, ohne max_teig zu überschreiten."""
    if gesamt_stueck <= 0:
        return None

    urspruengliche_menge = gesamt_stueck
    gesamt_stueck = math.ceil(gesamt_stueck / 5) * 5
    max_pro_teig = PRODUKTE[produkt_name]["max_teig"]
    anzahl_teige = math.ceil(gesamt_stueck / max_pro_teig)

    gesamt_reihen = gesamt_stueck // 5
    basis_reihen, extra_teige = divmod(gesamt_reihen, anzahl_teige)
    kleine_menge = basis_reihen * 5

    return {
        "anzahl_teige": anzahl_teige,
        "kleine_menge": kleine_menge,
        "kleine_teige": anzahl_teige - extra_teige,
        "grosse_menge": kleine_menge + 5,
        "grosse_teige": extra_teige,
        "gesamt": gesamt_stueck,
        "aufgerundet": gesamt_stueck != urspruengliche_menge,
        "unter_mindestmenge": kleine_menge < MINDEST_TEIG,
    }


def inventar_eingabe(label, key, bleche_pro_inventarwagen):
    col_wagen, col_rest = st.columns(2)
    with col_wagen:
        wagen = st.number_input(
            f"{label} – volle Wägen",
            min_value=0,
            step=1,
            key=f"inv_{key}_wagen",
        )
    with col_rest:
        rest = st.number_input(
            f"{label} – Restbleche",
            min_value=0,
            max_value=bleche_pro_inventarwagen - 1,
            step=1,
            key=f"inv_{key}_rest",
        )
    return wagen * bleche_pro_inventarwagen + rest


def netto_stueck_aus_stueckbedarf(produkt_name, bedarf_stueck, inventar_bleche):
    inventar_stueck = inventar_bleche * PRODUKTE[produkt_name]["stueck_pro_blech"]
    return max(0, bedarf_stueck - inventar_stueck), inventar_stueck


def netto_stueck_aus_blechbedarf(produkt_name, bedarf_bleche, inventar_bleche):
    netto_bleche = max(0, bedarf_bleche - inventar_bleche)
    return netto_bleche * PRODUKTE[produkt_name]["stueck_pro_blech"], netto_bleche


def formatiere_wagen(volle_wagen, rest_bleche):
    teile = []
    if volle_wagen:
        teile.append(f"{volle_wagen} volle Wägen")
    if rest_bleche:
        teile.append(f"1 Wagen mit {rest_bleche} Blechen")
    return " + ".join(teile)


def verteile_bleche(total_bleche, kapazitaet):
    """Verteilt Bleche gleichmäßig, ohne die Wagenkapazität zu überschreiten."""
    if total_bleche <= 0:
        return []
    anzahl_wagen = math.ceil(total_bleche / kapazitaet)
    basis, rest = divmod(total_bleche, anzahl_wagen)
    return [basis + (index < rest) for index in range(anzahl_wagen)]


# --- APP FRONTEND ---
st.set_page_config(page_title="Bäckerei Logistik", layout="wide")
st.title("🥐 Bäckerei Kommandozentrale")

col1, col2, col3 = st.columns(3)

with col1:
    st.header("📅 Täglich (Stück)")
    tafel_stk = st.number_input("Tafel (Standard)", min_value=0, step=5)

    st.caption("Sondersorten Tafel (20er Schritte)")
    tafel_mohn_stk = st.number_input("Tafel Mohn", min_value=0, step=20)
    tafel_sesam_stk = st.number_input("Tafel Sesam", min_value=0, step=20)
    tafel_salz_stk = st.number_input("Tafel Salzkümmel", min_value=0, step=20)

    tafel_teig_stk = st.number_input("Tafel Teiglinge", min_value=0, step=5)
    st.markdown("---")
    laugen_stk = st.number_input("Laugen", min_value=0, step=5)
    laugen_teig_stk = st.number_input("Laugen Teiglinge", min_value=0, step=5)

with col2:
    st.header("❄️ Frosterbedarf (Bleche)")
    muehlen_bl = st.number_input("Mühlenrädle", min_value=0, step=1)
    milch_bl = st.number_input("Milchbrötchen", min_value=0, step=1)
    schnitt_bl = st.number_input("Schnittbrötchen", min_value=0, step=1)

with col3:
    st.header("🔴 Wochenende Sonder")
    tafel_so_stk = st.number_input("Tafel Sonntag", min_value=0, step=5)
    st.caption("Zusatzmengen für Sonntag werden am Samstag produziert.")
    laugen_so_stk = st.number_input("+ Laugen Sonntag", min_value=0, step=5)
    laugen_teig_so_stk = st.number_input("+ Laugen Teiglinge So.", min_value=0, step=5)
    schnitt_so_bl = st.number_input("+ Schnittbrötchen So. (Bleche)", min_value=0, step=1)


with st.expander("📦 Inventar erfassen", expanded=True):
    st.caption(
        "Inventar wird vor der Produktionsplanung abgezogen. "
        "Ein Inventarwagen entspricht 18 Blechen; bei Laugen und Laugen-Teiglingen 24 großen Blechen."
    )
    inv_tag, inv_sonntag = st.tabs(["Täglich / Froster", "Sonntag separat"])

    with inv_tag:
        inv_col1, inv_col2, inv_col3 = st.columns(3)
        with inv_col1:
            inv_tafel_bl = inventar_eingabe("Tafel", "tafel", 18)
            inv_tafel_teig_bl = inventar_eingabe("Tafel Teiglinge", "tafel_teig", 18)
        with inv_col2:
            inv_laugen_bl = inventar_eingabe("Laugen", "laugen", 24)
            inv_laugen_teig_bl = inventar_eingabe("Laugen Teiglinge", "laugen_teig", 24)
        with inv_col3:
            inv_muehlen_bl = inventar_eingabe("Mühlenrädle", "muehlen", 18)
            inv_milch_bl = inventar_eingabe("Milchbrötchen", "milch", 18)
            inv_schnitt_bl = inventar_eingabe("Schnittbrötchen", "schnitt", 18)

    with inv_sonntag:
        so_col1, so_col2 = st.columns(2)
        with so_col1:
            inv_tafel_so_bl = inventar_eingabe("Tafel Sonntag", "tafel_so", 18)
            inv_schnitt_so_bl = inventar_eingabe("Schnittbrötchen Sonntag", "schnitt_so", 18)
        with so_col2:
            inv_laugen_so_bl = inventar_eingabe("Laugen Sonntag", "laugen_so", 24)
            inv_laugen_teig_so_bl = inventar_eingabe(
                "Laugen Teiglinge Sonntag", "laugen_teig_so", 24
            )


# --- BERECHNUNG & AUSGABE ---
if st.button("🚀 Alles berechnen", use_container_width=True, type="primary"):
    summe_tafel_brutto = tafel_stk + tafel_mohn_stk + tafel_sesam_stk + tafel_salz_stk

    tafel_netto, inv_tafel_stk = netto_stueck_aus_stueckbedarf(
        "Tafel", summe_tafel_brutto, inv_tafel_bl
    )
    tafel_teig_netto, inv_tafel_teig_stk = netto_stueck_aus_stueckbedarf(
        "Tafel Teigling", tafel_teig_stk, inv_tafel_teig_bl
    )
    tafel_so_netto, inv_tafel_so_stk = netto_stueck_aus_stueckbedarf(
        "Tafel Sonntag", tafel_so_stk, inv_tafel_so_bl
    )
    laugen_netto, inv_laugen_stk = netto_stueck_aus_stueckbedarf(
        "Laugen", laugen_stk, inv_laugen_bl
    )
    laugen_teig_netto, inv_laugen_teig_stk = netto_stueck_aus_stueckbedarf(
        "Laugen Teigling", laugen_teig_stk, inv_laugen_teig_bl
    )
    laugen_so_netto, inv_laugen_so_stk = netto_stueck_aus_stueckbedarf(
        "Laugen", laugen_so_stk, inv_laugen_so_bl
    )
    laugen_teig_so_netto, inv_laugen_teig_so_stk = netto_stueck_aus_stueckbedarf(
        "Laugen Teigling", laugen_teig_so_stk, inv_laugen_teig_so_bl
    )
    muehlen_netto, muehlen_netto_bl = netto_stueck_aus_blechbedarf(
        "Mühlenrädle", muehlen_bl, inv_muehlen_bl
    )
    milch_netto, milch_netto_bl = netto_stueck_aus_blechbedarf(
        "Milchbrötchen", milch_bl, inv_milch_bl
    )
    schnitt_tag_netto, schnitt_tag_netto_bl = netto_stueck_aus_blechbedarf(
        "Schnittbrötchen", schnitt_bl, inv_schnitt_bl
    )
    schnitt_so_netto, schnitt_so_netto_bl = netto_stueck_aus_blechbedarf(
        "Schnittbrötchen", schnitt_so_bl, inv_schnitt_so_bl
    )
    schnitt_gesamt_netto = schnitt_tag_netto + schnitt_so_netto

    st.markdown("---")
    st.header("📋 Produktionsplan")

    with st.expander("🔎 Bedarf, Inventar und Nettoproduktion"):
        uebersicht = [
            ("Tafel", summe_tafel_brutto, inv_tafel_stk, tafel_netto, "Stk"),
            ("Tafel Teiglinge", tafel_teig_stk, inv_tafel_teig_stk, tafel_teig_netto, "Stk"),
            ("Tafel Sonntag", tafel_so_stk, inv_tafel_so_stk, tafel_so_netto, "Stk"),
            ("Laugen", laugen_stk, inv_laugen_stk, laugen_netto, "Stk"),
            ("Laugen Teiglinge", laugen_teig_stk, inv_laugen_teig_stk, laugen_teig_netto, "Stk"),
            ("Laugen Sonntag", laugen_so_stk, inv_laugen_so_stk, laugen_so_netto, "Stk"),
            ("Laugen Teiglinge Sonntag", laugen_teig_so_stk, inv_laugen_teig_so_stk, laugen_teig_so_netto, "Stk"),
            ("Mühlenrädle", muehlen_bl, inv_muehlen_bl, muehlen_netto_bl, "Bleche"),
            ("Milchbrötchen", milch_bl, inv_milch_bl, milch_netto_bl, "Bleche"),
            ("Schnittbrötchen", schnitt_bl, inv_schnitt_bl, schnitt_tag_netto_bl, "Bleche"),
            ("Schnittbrötchen Sonntag", schnitt_so_bl, inv_schnitt_so_bl, schnitt_so_netto_bl, "Bleche"),
        ]
        st.dataframe(
            [
                {
                    "Produkt": name,
                    "Bedarf": bedarf,
                    "Inventar": inventar,
                    "Zu produzieren": netto,
                    "Einheit": einheit,
                    "Überschuss Inventar": max(0, inventar - bedarf),
                }
                for name, bedarf, inventar, netto, einheit in uebersicht
            ],
            use_container_width=True,
            hide_index=True,
        )

    out_col1, out_col2 = st.columns(2)

    with out_col1:
        st.subheader("🛒 Wägen & Bleche")
        auftraege_wagen = [
            ("Tafel", tafel_netto),
            ("Tafel Teigling", tafel_teig_netto),
            ("Tafel Sonntag", tafel_so_netto),
            ("Laugen", laugen_netto + laugen_so_netto),
            ("Laugen Teigling", laugen_teig_netto + laugen_teig_so_netto),
            ("Mühlenrädle", muehlen_netto),
            ("Milchbrötchen", milch_netto),
            ("Schnittbrötchen", schnitt_gesamt_netto),
        ]

        for name, menge in auftraege_wagen:
            ergebnis = berechne_wagen(name, menge)
            if not ergebnis:
                continue

            volle_wagen, rest_bleche, total_bleche = ergebnis
            if name == "Laugen Teigling":
                verteilung = verteile_bleche(
                    total_bleche, PRODUKTE[name]["bleche_pro_wagen"]
                )
                text = " & ".join(f"1× {bleche} Bleche" for bleche in verteilung)
                st.success(
                    f"**{name}** ({menge} Stk): {len(verteilung)} Wägen 👉 {text}"
                )
            else:
                st.success(
                    f"**{name}** ({menge} Stk): "
                    f"{formatiere_wagen(volle_wagen, rest_bleche)}"
                )

    with out_col2:
        st.subheader("🥣 Teigbestellung")
        teig_auftraege = [
            (
                "Tafel",
                tafel_netto + tafel_teig_netto + TAFEL_EXTRA,
                f"Tafel täglich (netto inkl. Teiglinge & +{TAFEL_EXTRA} Extra)",
            ),
            ("Tafel Sonntag", tafel_so_netto, "Tafel Sonntag (netto)"),
            (
                "Laugen",
                laugen_netto + laugen_teig_netto + laugen_so_netto + laugen_teig_so_netto,
                "Laugen gesamt (netto inkl. Teiglinge und Sonntag)",
            ),
            ("Mühlenrädle", muehlen_netto, "Mühlenrädle (netto)"),
            ("Milchbrötchen", milch_netto, "Milchbrötchen (netto)"),
            ("Schnittbrötchen", schnitt_gesamt_netto, "Schnittbrötchen (netto inkl. Sonntag)"),
        ]

        for produkt_name, menge, label in teig_auftraege:
            ergebnis = berechne_teig(produkt_name, menge)
            if not ergebnis:
                continue

            st.warning(f"**{label}** (Total: {ergebnis['gesamt']} Stk)")
            if ergebnis["aufgerundet"]:
                st.caption("Auf den nächsten 5er-Schritt aufgerundet.")

            teile = []
            if ergebnis["kleine_teige"]:
                teile.append(
                    f"{ergebnis['kleine_teige']}× Teig à {ergebnis['kleine_menge']} Stück"
                )
            if ergebnis["grosse_teige"]:
                teile.append(
                    f"{ergebnis['grosse_teige']}× Teig à {ergebnis['grosse_menge']} Stück"
                )
            st.write("👉 " + "  |  ".join(teile))

            if ergebnis["unter_mindestmenge"] and ergebnis["anzahl_teige"] > 1:
                st.caption(
                    f"Hinweis: Mindestens ein Teig liegt unter {MINDEST_TEIG} Stück, "
                    "weil die maximale Teiggröße nicht überschritten wird."
                )

