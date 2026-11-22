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

        # Tab 4: Pricing engine
        "pe_question": "Which prices should change?",
        "pe_max_change": "Max price change per step (%)",
        "pe_min_margin": "Minimum margin when cutting prices (%)",
        "pe_alpha": "Significance level (p-value below)",
        "pe_decision": "Show",
        "pe_search": "Search product",
        "pe_products": "Products analysed",
        "pe_raise": "Price raises",
        "pe_lower": "Price cuts",
        "pe_revenue": "Expected revenue change / week",
        "pe_margin": "Expected margin change / week",
        "pe_table_title": "Recommendations (sorted by expected margin change)",
        "pe_col_product": "Product",
        "pe_col_current": "Current price",
        "pe_col_new": "Recommended price",
        "pe_col_change": "Price change (%)",
        "pe_col_elasticity": "Elasticity",
        "pe_col_ci": "95% confidence interval",
        "pe_col_p": "p-value",
        "pe_col_units": "Units change (%)",
        "pe_col_revenue": "Revenue change / week (GBP)",
        "pe_col_margin": "Margin change / week (GBP)",
        "pe_col_decision": "Decision",
        "pe_col_reason": "Reason",
        "dec_raise": "Raise",
        "dec_lower": "Lower",
        "dec_keep": "Keep",
        "reason_ok": "Margin-optimal price found",
        "reason_max_change": "Limited by the max-change guardrail",
        "reason_not_significant": "No change: elasticity not significant",
        "reason_elasticity_out_of_range": "No change: elasticity not believable",
        "reason_no_better_price": "No change: current price is already best",
        "pe_detail_title": "Expected weekly margin by price",
        "pe_pick_product": "Product to inspect",
        "pe_curve_x": "Price (GBP)",
        "pe_curve_y": "Expected margin per week (GBP)",
        "pe_current": "Current",
        "pe_recommended": "Recommended",
        "pe_how_title": "How does the pricing engine work?",
        "pe_how": (
            "1. **Elasticity**: for each product we fit  log(units) = a + b · log(price) + c · log(store demand)  "
            "on weekly data. **b** is the price elasticity: +1% price changes units by b%. "
            "The store-demand term separates price effects from seasonality.\n"
            "2. **Which products**: at least 30 weeks with sales, the weekly price varies by at least 5% "
            "(and has 4+ different values), and the product sold in the last quarter.\n"
            "3. **Price used**: the median price of normal order lines (up to 100 units). "
            "Bulk lines are excluded because they carry volume discounts.\n"
            "4. **Recommender**: test prices from -max to +max in 1% steps, expected units = units now × (price ratio)^b, "
            "choose the highest expected margin.\n"
            "5. **Guardrails**: max change per step; no price cut below the minimum margin; "
            "no change when the elasticity is not significant or not believable (above 0 or below -5)."
        ),
        "pe_caption": (
            "Estimates come from historical data and are indicative, not causal. Margin uses an ASSUMED unit cost of "
            "60% of each product's median price. Thousands of products are tested, so some 'significant' results "
            "happen by chance. Expected changes assume the elasticity stays constant."
        ),

        # Tab 5: Management summary
        "ms_question": "What should we decide this week?",
        "ms_intro": "One-page summary written by an LLM from the KPI flags, customer segments, forecast and price recommendations.",
        "ms_button": "Generate summary",
        "ms_refresh": "Ask the model again (ignore saved answer)",
        "ms_no_summary": "No saved summary yet. Press the button to generate one.",
        "ms_working": "Writing the summary...",
        "ms_en": "English",
        "ms_de": "Deutsch",
        "ms_src_llm": "Written by {model} just now.",
        "ms_src_cache": "Written by {model} (saved answer, no waiting).",
        "ms_src_rules": "Rule-based text (no LLM key available or the request failed).",
        "ms_error": "The model request failed, showing the rule-based text instead: {error}",
        "ms_prompt_title": "How is the AI used and controlled? (prompt and data)",
        "ms_control": (
            "- The model sees **only** the JSON below, never the raw data.\n"
            "- The structure is fixed: 3 findings, 3 actions, risks.\n"
            "- The prompt forbids invented numbers and requires the assumptions to be stated.\n"
            "- Answers are saved, so the same data always shows the same text and the demo never waits.\n"
            "- Without an API key the app shows a plain rule-based text instead.\n"
            "- A person must still read the summary before acting on it."
        ),
        "ms_system": "System prompt",
        "ms_user": "User prompt (with the data inserted)",
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

        # Tab 4: Pricing engine
        "pe_question": "Welche Preise sollten sich ändern?",
        "pe_max_change": "Max. Preisänderung pro Schritt (%)",
        "pe_min_margin": "Mindestmarge bei Preissenkungen (%)",
        "pe_alpha": "Signifikanzniveau (p-Wert unter)",
        "pe_decision": "Anzeigen",
        "pe_search": "Produkt suchen",
        "pe_products": "Analysierte Produkte",
        "pe_raise": "Preiserhöhungen",
        "pe_lower": "Preissenkungen",
        "pe_revenue": "Erwartete Umsatzänderung / Woche",
        "pe_margin": "Erwartete Margenänderung / Woche",
        "pe_table_title": "Empfehlungen (sortiert nach erwarteter Margenänderung)",
        "pe_col_product": "Produkt",
        "pe_col_current": "Aktueller Preis",
        "pe_col_new": "Empfohlener Preis",
        "pe_col_change": "Preisänderung (%)",
        "pe_col_elasticity": "Elastizität",
        "pe_col_ci": "95%-Konfidenzintervall",
        "pe_col_p": "p-Wert",
        "pe_col_units": "Absatzänderung (%)",
        "pe_col_revenue": "Umsatzänderung / Woche (GBP)",
        "pe_col_margin": "Margenänderung / Woche (GBP)",
        "pe_col_decision": "Entscheidung",
        "pe_col_reason": "Grund",
        "dec_raise": "Erhöhen",
        "dec_lower": "Senken",
        "dec_keep": "Beibehalten",
        "reason_ok": "Margenoptimaler Preis gefunden",
        "reason_max_change": "Durch die maximale Schrittweite begrenzt",
        "reason_not_significant": "Keine Änderung: Elastizität nicht signifikant",
        "reason_elasticity_out_of_range": "Keine Änderung: Elastizität nicht plausibel",
        "reason_no_better_price": "Keine Änderung: aktueller Preis ist bereits optimal",
        "pe_detail_title": "Erwartete Wochenmarge je Preis",
        "pe_pick_product": "Produkt prüfen",
        "pe_curve_x": "Preis (GBP)",
        "pe_curve_y": "Erwartete Marge pro Woche (GBP)",
        "pe_current": "Aktuell",
        "pe_recommended": "Empfohlen",
        "pe_how_title": "Wie funktioniert die Preis-Engine?",
        "pe_how": (
            "1. **Elastizität**: Für jedes Produkt schätzen wir  log(Absatz) = a + b · log(Preis) + c · log(Gesamtnachfrage)  "
            "mit Wochendaten. **b** ist die Preiselastizität: +1% Preis verändert den Absatz um b%. "
            "Der Term für die Gesamtnachfrage trennt Preiseffekte von Saisoneffekten.\n"
            "2. **Welche Produkte**: mindestens 30 Wochen mit Verkäufen, der Wochenpreis schwankt um mindestens 5% "
            "(mit mindestens 4 verschiedenen Werten), und das Produkt wurde im letzten Quartal verkauft.\n"
            "3. **Verwendeter Preis**: der Median-Preis normaler Bestellpositionen (bis 100 Stück). "
            "Großmengen werden ausgeschlossen, weil sie Mengenrabatte enthalten.\n"
            "4. **Empfehlung**: Wir testen Preise von -max bis +max in 1%-Schritten, erwarteter Absatz = heutiger Absatz × (Preisverhältnis)^b, "
            "und wählen die höchste erwartete Marge.\n"
            "5. **Leitplanken**: maximale Änderung pro Schritt; keine Preissenkung unter die Mindestmarge; "
            "keine Änderung, wenn die Elastizität nicht signifikant oder nicht plausibel ist (über 0 oder unter -5)."
        ),
        "pe_caption": (
            "Die Schätzungen stammen aus historischen Daten und sind indikativ, nicht kausal. Die Marge nutzt ANGENOMMENE Stückkosten von "
            "60% des Median-Preises jedes Produkts. Es werden tausende Produkte getestet, daher sind einige 'signifikante' Ergebnisse "
            "Zufall. Die erwarteten Änderungen setzen eine konstante Elastizität voraus."
        ),

        # Tab 5: Management summary
        "ms_question": "Was sollten wir diese Woche entscheiden?",
        "ms_intro": "Einseitige Zusammenfassung, von einem LLM aus KPI-Flags, Kundensegmenten, Prognose und Preisempfehlungen geschrieben.",
        "ms_button": "Zusammenfassung erstellen",
        "ms_refresh": "Modell erneut fragen (gespeicherte Antwort ignorieren)",
        "ms_no_summary": "Noch keine gespeicherte Zusammenfassung. Zum Erstellen den Button drücken.",
        "ms_working": "Die Zusammenfassung wird geschrieben...",
        "ms_en": "English",
        "ms_de": "Deutsch",
        "ms_src_llm": "Soeben von {model} geschrieben.",
        "ms_src_cache": "Von {model} geschrieben (gespeicherte Antwort, keine Wartezeit).",
        "ms_src_rules": "Regelbasierter Text (kein LLM-Schlüssel verfügbar oder die Anfrage ist fehlgeschlagen).",
        "ms_error": "Die Modellanfrage ist fehlgeschlagen, stattdessen wird der regelbasierte Text gezeigt: {error}",
        "ms_prompt_title": "Wie wird die KI eingesetzt und kontrolliert? (Prompt und Daten)",
        "ms_control": (
            "- Das Modell sieht **nur** das JSON unten, nie die Rohdaten.\n"
            "- Die Struktur ist fest vorgegeben: 3 Erkenntnisse, 3 Maßnahmen, Risiken.\n"
            "- Der Prompt verbietet erfundene Zahlen und verlangt, dass die Annahmen genannt werden.\n"
            "- Antworten werden gespeichert: gleiche Daten zeigen immer denselben Text, und die Demo wartet nie.\n"
            "- Ohne API-Schlüssel zeigt die App stattdessen einen einfachen regelbasierten Text.\n"
            "- Ein Mensch muss die Zusammenfassung lesen, bevor gehandelt wird."
        ),
        "ms_system": "System-Prompt",
        "ms_user": "User-Prompt (mit eingefügten Daten)",
    },
}
