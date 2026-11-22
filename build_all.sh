#!/bin/bash
# Rebuild every table the app reads (needs data/processed/sales_clean.parquet from step 1).
# Run from the project root with the virtual environment active:  ./build_all.sh
set -e
python -m src.build_weekly
python -m src.build_rfm
python -m src.build_forecast
python -m src.build_pricing
echo "Done. Start the app with:  streamlit run app/streamlit_app.py"
