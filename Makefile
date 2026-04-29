# =============================================================================
# AVGO Equity Research — convenience Makefile
# =============================================================================
# Usage:
#   make data        — refresh market data from yfinance (slow)
#   make valuation   — run the DCF / SOTP / Comps / Monte Carlo engine
#   make figures     — generate all 12 figures + copy them into report/
#   make excel       — build the 10-sheet Excel financial model
#   make report      — compile the LaTeX PDF (runs pdflatex twice)
#   make all         — runs valuation → figures → excel → report (no data fetch)
#   make clean       — remove all generated outputs (keeps data/)
# =============================================================================

PYTHON := python3
PDFLATEX := pdflatex
SCRIPTS := scripts
REPORT := report

.PHONY: all data valuation figures excel report clean help

help:
	@echo "Targets: data, valuation, figures, excel, report, all, clean"

data:
	$(PYTHON) $(SCRIPTS)/01_data_fetch.py

valuation:
	$(PYTHON) $(SCRIPTS)/02_valuation.py

figures: valuation
	$(PYTHON) $(SCRIPTS)/03_figures.py
	cp figures/*.png $(REPORT)/

excel: valuation
	$(PYTHON) $(SCRIPTS)/04_excel_model.py

report: figures
	cd $(REPORT) && $(PDFLATEX) -interaction=nonstopmode AVGO_Equity_Research_Report.tex
	cd $(REPORT) && $(PDFLATEX) -interaction=nonstopmode AVGO_Equity_Research_Report.tex

all: valuation figures excel report

clean:
	rm -f output/*.csv output/*.json output/*.xlsx
	rm -f figures/*.png
	rm -f $(REPORT)/*.aux $(REPORT)/*.log $(REPORT)/*.out $(REPORT)/*.toc
	rm -f $(REPORT)/AVGO_Equity_Research_Report.pdf
	@echo "Cleaned. To regenerate, run: make all"
