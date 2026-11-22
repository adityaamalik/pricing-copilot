"""All text shown in the app, in English and German.

To add a language or change a label, edit only this file.
Missing keys fall back to the key itself (see t() in common.py).
"""

TEXT = {
    "en": {
        # General
        "language": "Language / Sprache",
        "all": "All",
        "tab_kpi": "KPI monitor",
        "tab_segments": "Customer segments",
        "tab_forecast": "Demand forecast",
        "tab_pricing": "Pricing engine",
        "tab_summary": "Management summary",
        "coming_soon": "Coming soon.",

        # Product groups and segments (display names)
        "grp_Christmas": "Christmas",
        "grp_Bags": "Bags",
        "grp_Kitchen & Dining": "Kitchen & Dining",
        "grp_Home Decor": "Home Decor",
        "grp_Stationery & Gifts": "Stationery & Gifts",
        "grp_Toys & Games": "Toys & Games",
        "grp_Other": "Other",
        "seg_Champions": "Champions",
        "seg_Loyal": "Loyal",
        "seg_New": "New",
        "seg_At risk": "At risk",
        "seg_Hibernating": "Hibernating",

        # Tab 1: KPI monitor
        "kpi_question": "Is pricing on track?",
        "country": "Country",
        "product_group": "Product group",
        "band_width": "Band width (± standard deviations)",
        "wow_limit": "Week-over-week limit (%)",
        "m_revenue": "Weekly revenue (GBP)",
        "m_units": "Weekly units",
        "m_avg_price": "Average selling price (GBP)",
        "m_margin_pct": "Estimated margin %",
        "m_return_rate": "Return rate %",
        "flags_title": "Deviation flags",
        "no_flags": "No deviations found for this selection.",
        "col_week": "Week",
        "col_metric": "KPI",
        "col_value": "Value",
        "col_expected": "Expected",
        "col_change": "Change vs. last week (%)",
        "col_action": "Suggested action",
        "kpi_caption": (
            "Assumption: there is no cost column, so unit cost is assumed to be "
            "{share} of each product's median price. Margin is an estimate. "
            "Average price also moves with product mix, not only with price changes."
        ),

        # Tab 2: Customer segments
        "seg_question": "Who buys, and how price-sensitive are they?",
        "seg_table_title": "Segments at a glance",
        "col_segment": "Segment",
        "col_customers": "Customers",
        "col_revenue": "Revenue (GBP)",
        "col_recency": "Avg. days since last order",
        "col_orders": "Avg. orders",
        "col_rev_share": "Revenue share (%)",
        "col_price_paid": "Avg. price paid per unit (GBP)",
        "col_discount": "Avg. discount vs. usual price (%)",
        "chart_rev_share": "Revenue share by segment (%)",
        "chart_customers": "Customers by segment",
        "seg_rules_title": "How are the segments defined?",
        "seg_rules": (
            "Each customer gets a score from 1 (worst) to 5 (best) for **R**ecency "
            "(days since last order), **F**requency (number of orders) and **M**onetary "
            "(total spent).\n\n"
            "- **Champions**: R ≥ 4 and F ≥ 4\n"
            "- **Loyal**: R ≥ 3 and F ≥ 3 (but not Champions)\n"
            "- **New**: R ≥ 4 and F ≤ 2\n"
            "- **At risk**: R ≤ 2 and F ≥ 3\n"
            "- **Hibernating**: everyone else"
        ),
        "top_customers": "Top 100 customers by revenue",
        "col_customer": "Customer ID",
        "col_country": "Country",
        "seg_caption": (
            "Discount = how far below the product's usual (median) price a customer paid. "
            "Customers without a customer ID are not included. "
            "This describes past prices paid, it is not a measured price elasticity."
        ),

        # Tab 3: Demand forecast
        "fc_question": "What will we sell next?",
        "fc_product": "Product",
        "fc_chart_title": "Weekly units: history, backtest and 8-week forecast",
        "fc_history": "Actual units",
        "fc_naive_bt": "Baseline (backtest)",
        "fc_lgbm_bt": "LightGBM (backtest)",
        "fc_naive_fc": "Baseline (forecast)",
        "fc_lgbm_fc": "LightGBM (forecast)",
        "fc_errors_title": "Backtest on the last 12 weeks: error (MAPE, lower is better)",
        "fc_col_product": "Product",
        "fc_col_naive": "Baseline MAPE (%)",
        "fc_col_lgbm": "LightGBM MAPE (%)",
        "fc_average": "Average",
        "fc_better": "LightGBM beats the baseline for {n} of {total} products.",
        "fc_avg_text": "Average error: baseline {naive:.1f}%, LightGBM {lgbm:.1f}%.",
        "fc_how_title": "How does the forecast work?",
        "fc_how": (
            "- **Backtest**: we hide the last 12 weeks, forecast them, and compare with what really sold.\n"
            "- **Baseline (seasonal naive)**: forecast = the same week one year earlier.\n"
            "- **LightGBM**: one model for all 10 products. It sees the recent level, the same week "
            "last year, the week of the year and how many weeks ahead it predicts.\n"
            "- **Products**: the 10 best-selling products (by revenue) that sold in at least 60 weeks "
            "and are not dominated by a single huge order."
        ),
        "fc_caption": (
            "MAPE = average of |actual - forecast| / actual, only for weeks with sales. "
            "Weekly sales per product are lumpy (wholesale orders), so errors of 30-80% are normal. "
            "With only two years of data, the yearly pattern is learned from a single previous year."
        ),
    },
    "de": {
        # General
        "language": "Language / Sprache",
        "all": "Alle",
        "tab_kpi": "KPI-Monitor",
        "tab_segments": "Kundensegmente",
        "tab_forecast": "Absatzprognose",
        "tab_pricing": "Preis-Engine",
        "tab_summary": "Management-Zusammenfassung",
        "coming_soon": "Folgt in Kürze.",

        # Product groups and segments (display names)
        "grp_Christmas": "Weihnachten",
        "grp_Bags": "Taschen",
        "grp_Kitchen & Dining": "Küche & Tisch",
        "grp_Home Decor": "Wohndeko",
        "grp_Stationery & Gifts": "Papeterie & Geschenke",
        "grp_Toys & Games": "Spielzeug & Spiele",
        "grp_Other": "Sonstiges",
        "seg_Champions": "Champions",
        "seg_Loyal": "Treue Kunden",
        "seg_New": "Neukunden",
        "seg_At risk": "Abwanderungsgefährdet",
        "seg_Hibernating": "Inaktiv",

        # Tab 1: KPI monitor
        "kpi_question": "Ist die Preisgestaltung auf Kurs?",
        "country": "Land",
        "product_group": "Produktgruppe",
        "band_width": "Bandbreite (± Standardabweichungen)",
        "wow_limit": "Grenze Vorwochenänderung (%)",
        "m_revenue": "Wochenumsatz (GBP)",
        "m_units": "Wochenabsatz (Stück)",
        "m_avg_price": "Durchschnittlicher Verkaufspreis (GBP)",
        "m_margin_pct": "Geschätzte Marge %",
        "m_return_rate": "Retourenquote %",
        "flags_title": "Abweichungs-Flags",
        "no_flags": "Keine Abweichungen für diese Auswahl gefunden.",
        "col_week": "Woche",
        "col_metric": "KPI",
        "col_value": "Wert",
        "col_expected": "Erwartet",
        "col_change": "Änderung zur Vorwoche (%)",
        "col_action": "Empfohlene Maßnahme",
        "kpi_caption": (
            "Annahme: Es gibt keine Kostenspalte. Die Stückkosten werden daher mit "
            "{share} des Median-Preises jedes Produkts angenommen. Die Marge ist eine Schätzung. "
            "Der Durchschnittspreis ändert sich auch durch den Produktmix, nicht nur durch Preisänderungen."
        ),

        # Tab 2: Customer segments
        "seg_question": "Wer kauft, und wie preissensibel sind die Kunden?",
        "seg_table_title": "Segmente im Überblick",
        "col_segment": "Segment",
        "col_customers": "Kunden",
        "col_revenue": "Umsatz (GBP)",
        "col_recency": "Ø Tage seit letzter Bestellung",
        "col_orders": "Ø Bestellungen",
        "col_rev_share": "Umsatzanteil (%)",
        "col_price_paid": "Ø gezahlter Preis pro Stück (GBP)",
        "col_discount": "Ø Rabatt zum üblichen Preis (%)",
        "chart_rev_share": "Umsatzanteil je Segment (%)",
        "chart_customers": "Kunden je Segment",
        "seg_rules_title": "Wie sind die Segmente definiert?",
        "seg_rules": (
            "Jeder Kunde erhält eine Bewertung von 1 (schlecht) bis 5 (sehr gut) für "
            "**R**ecency (Tage seit der letzten Bestellung), **F**requency (Anzahl Bestellungen) "
            "und **M**onetary (Gesamtumsatz).\n\n"
            "- **Champions**: R ≥ 4 und F ≥ 4\n"
            "- **Treue Kunden**: R ≥ 3 und F ≥ 3 (aber keine Champions)\n"
            "- **Neukunden**: R ≥ 4 und F ≤ 2\n"
            "- **Abwanderungsgefährdet**: R ≤ 2 und F ≥ 3\n"
            "- **Inaktiv**: alle anderen"
        ),
        "top_customers": "Top 100 Kunden nach Umsatz",
        "col_customer": "Kunden-ID",
        "col_country": "Land",
        "seg_caption": (
            "Rabatt = wie weit unter dem üblichen (Median-)Preis eines Produkts ein Kunde bezahlt hat. "
            "Kunden ohne Kunden-ID sind nicht enthalten. "
            "Das beschreibt bisher gezahlte Preise, es ist keine gemessene Preiselastizität."
        ),

        # Tab 3: Demand forecast
        "fc_question": "Was werden wir als Nächstes verkaufen?",
        "fc_product": "Produkt",
        "fc_chart_title": "Wöchentlicher Absatz: Verlauf, Backtest und 8-Wochen-Prognose",
        "fc_history": "Tatsächlicher Absatz",
        "fc_naive_bt": "Baseline (Backtest)",
        "fc_lgbm_bt": "LightGBM (Backtest)",
        "fc_naive_fc": "Baseline (Prognose)",
        "fc_lgbm_fc": "LightGBM (Prognose)",
        "fc_errors_title": "Backtest der letzten 12 Wochen: Fehler (MAPE, niedriger ist besser)",
        "fc_col_product": "Produkt",
        "fc_col_naive": "Baseline MAPE (%)",
        "fc_col_lgbm": "LightGBM MAPE (%)",
        "fc_average": "Durchschnitt",
        "fc_better": "LightGBM schlägt die Baseline bei {n} von {total} Produkten.",
        "fc_avg_text": "Durchschnittlicher Fehler: Baseline {naive:.1f}%, LightGBM {lgbm:.1f}%.",
        "fc_how_title": "Wie funktioniert die Prognose?",
        "fc_how": (
            "- **Backtest**: Wir blenden die letzten 12 Wochen aus, prognostizieren sie und vergleichen mit dem echten Absatz.\n"
            "- **Baseline (saisonal naiv)**: Prognose = dieselbe Woche ein Jahr zuvor.\n"
            "- **LightGBM**: ein Modell für alle 10 Produkte. Es kennt das aktuelle Niveau, dieselbe Woche "
            "im Vorjahr, die Kalenderwoche und wie viele Wochen es vorausschaut.\n"
            "- **Produkte**: die 10 umsatzstärksten Produkte, die in mindestens 60 Wochen verkauft wurden "
            "und nicht von einer einzigen Riesenbestellung dominiert werden."
        ),
        "fc_caption": (
            "MAPE = Durchschnitt von |Ist - Prognose| / Ist, nur für Wochen mit Verkäufen. "
            "Der Wochenabsatz je Produkt schwankt stark (Großhandelsbestellungen), daher sind Fehler von 30-80% normal. "
            "Mit nur zwei Jahren Daten wird das Jahresmuster aus nur einem Vorjahr gelernt."
        ),
    },
}
