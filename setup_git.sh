#!/bin/bash
# Run this once to initialize your git repository and push to GitHub
# Usage: bash setup_git.sh

echo "================================================"
echo "  DemandIQ — Git Setup Script"
echo "================================================"

# Initialize git
git init
git add .
git commit -m "feat: initial DemandIQ project setup

- SARIMA/SARIMAX/ARIMA/ARIMAX forecasting pipeline
- Run logging and version control (runs/run_log.json)
- Executive dashboard with 6 tabs
- Dark industrial UI with IBM Plex Mono + Syne fonts
- Streamlit Cloud deployment config"

echo ""
echo "Next steps:"
echo "  1. Create a new repo on GitHub: https://github.com/new"
echo "  2. Run: git remote add origin https://github.com/YOUR_USERNAME/demandiq.git"
echo "  3. Run: git push -u origin main"
echo "  4. Deploy on Streamlit Cloud: https://share.streamlit.io"
echo ""
echo "For future runs, commit your updated outputs:"
echo "  python src/pipeline.py --notes 'Your note here'"
echo "  git add outputs/ runs/"
echo "  git commit -m 'data: pipeline run YYYY-MM-DD, MAPE X.X%'"
echo "  git push"
