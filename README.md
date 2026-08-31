<div align="center">

# Institutional Valuation Engine

### Automated DCF, Trading Comparables, Scenario Analysis, and Deal-Ready Excel Reporting

[![Portfolio](https://img.shields.io/badge/Portfolio-Data%20Analytics-0A66C2?style=flat-square)](https://github.com/gawandeshil03-ops/data-analytics-bi-portfolio1)
[![Repository](https://img.shields.io/badge/GitHub-Valuation%20Engine-181717?style=flat-square&logo=github)](https://github.com/gawandeshil03-ops/institutional-valuation-engine)
![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Finance](https://img.shields.io/badge/Finance-DCF%20%26%20Comps-2E8B57?style=flat-square)
![Excel](https://img.shields.io/badge/Excel-Automated%20Reporting-217346?style=flat-square&logo=microsoftexcel&logoColor=white)

</div>

## Project Overview

The Institutional Valuation Engine is a modular Python toolkit that automates core equity-valuation workflows. It combines Discounted Cash Flow analysis, trading comparables, multi-scenario forecasting, WACC estimation, sensitivity testing, validation checks, visualization, and formatted Excel reporting.

Unlike a rigid spreadsheet model, the project separates data, assumptions, calculations, and reporting into reusable modules. This makes the valuation process easier to audit, extend, and rerun across different companies and scenarios.

## Business Objective

Build a repeatable valuation workflow that can:

- Forecast operating and financial performance
- Run Bear, Base, and Bull scenarios
- Calculate WACC using CAPM-based inputs
- Estimate enterprise and equity value
- Apply Gordon Growth and Exit Multiple terminal-value methods
- Compare results with peer-company trading multiples
- Test valuation sensitivity across WACC and terminal-growth assumptions
- Flag potentially unrealistic assumptions
- Export a structured Excel model and valuation chart

## Valuation Workflow

```text
Company financials and peer data
   ↓
Data loading and validation
   ↓
Historical financial analysis
   ↓
Bear / Base / Bull forecasts
   ↓
WACC and DCF calculation
   ↓
Trading comparables
   ↓
Sensitivity and sanity checks
   ↓
Excel model and valuation visualization
```

## Key Features

### DCF Engine

- Fractional discounting based on the valuation date
- Stub-period and mid-year convention support
- Non-linear annual growth and margin assumptions
- Gordon Growth and Exit Multiple terminal values
- Enterprise-value, equity-value, and implied-share-price calculations

### Multi-Scenario Architecture

- Runs Bear, Base, and Bull cases in one execution
- Allows one scenario to be selected as the primary reporting case
- Compares implied share price, enterprise value, and WACC across cases

### Trading Comparables

- Loads peer-company data from Excel
- Calculates valuation multiples from enterprise value, revenue, and EBITDA
- Produces comparable-company valuation ranges
- Integrates comparable results into the final valuation summary

### Automated Reporting

- Executive valuation summary
- Scenario comparison
- Detailed operating forecast
- DCF build-up
- WACC calculation
- Sensitivity analysis
- Trading-comparables output
- Football-field valuation chart

### Validation

- Checks assumptions before final reporting
- Flags values that may be inconsistent with historical performance
- Separates input, calculation, and output logic for easier review

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic and workflow orchestration |
| Pandas | Financial-data preparation and tabular analysis |
| NumPy | Numerical calculations |
| yfinance | Market-data retrieval |
| Matplotlib | Valuation visualization |
| XlsxWriter | Formatted Excel report generation |
| openpyxl | Excel workbook processing |

## Project Structure

```text
valuation-engine/
├── config.json
├── main.py
├── requirements.txt
├── inputs/
│   ├── AMZN_financials.xlsx
│   └── AMZN_peers.xlsx
└── src/
    ├── comps_model.py
    ├── data_loader.py
    ├── dcf_model.py
    ├── excel_export.py
    ├── financials.py
    ├── plotting.py
    ├── sanity_check.py
    ├── sensitivity_analysis.py
    └── wacc.py
```

> The `inputs` directory and Excel workbooks must be created or supplied before running the engine. Do not commit confidential company data.

## Core Modules

| Module | Responsibility |
|---|---|
| `main.py` | Parses inputs and orchestrates the complete valuation workflow |
| `data_loader.py` | Loads company financials, assumptions, peers, and market data |
| `financials.py` | Prepares historical and forecast financial statements |
| `wacc.py` | Calculates the weighted average cost of capital |
| `dcf_model.py` | Performs forecasting, discounting, and terminal-value calculations |
| `comps_model.py` | Runs trading-comparables analysis |
| `sensitivity_analysis.py` | Generates valuation sensitivity tables |
| `sanity_check.py` | Validates assumptions and outputs |
| `plotting.py` | Creates the football-field valuation chart |
| `excel_export.py` | Produces the formatted Excel deliverable |

## Installation

### Prerequisites

- Python 3.8 or later
- `pip`
- Excel-compatible company and peer input workbooks

### Clone the Repository

```bash
git clone https://github.com/gawandeshil03-ops/institutional-valuation-engine.git
cd institutional-valuation-engine
```

### Create a Virtual Environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Input Preparation

### Company Financials Workbook

Create an Excel workbook such as `inputs/AMZN_financials.xlsx` with the sheets expected by the data loader. The source documentation describes the following analytical areas:

- Historical income statement
- Balance sheet
- Cash-flow information
- Bear, Base, and Bull assumptions
- Revenue growth and margin forecasts
- WACC and terminal-value assumptions

### Peer Workbook

Create `inputs/AMZN_peers.xlsx` containing peer-company values such as:

- Company or ticker
- Enterprise value
- Revenue
- EBITDA
- Relevant valuation multiples

The exact sheet and column names must match the expectations in `src/data_loader.py` and `src/comps_model.py`.

## Configuration

Use project-relative paths in `config.json`:

```json
{
  "ticker": "AMZN",
  "excel_path": "inputs/AMZN_financials.xlsx",
  "peers_path": "inputs/AMZN_peers.xlsx",
  "output_file": "AMZN_Valuation.xlsx",
  "valuation_date": "today"
}
```

Avoid committing machine-specific absolute paths, credentials, or confidential financial data.

## Usage

### Command Line

```bash
python main.py \
  --ticker AMZN \
  --excel inputs/AMZN_financials.xlsx \
  --peers inputs/AMZN_peers.xlsx \
  --output AMZN_Valuation.xlsx \
  --case base
```

On Windows PowerShell, run the command on one line:

```powershell
python main.py --ticker AMZN --excel inputs/AMZN_financials.xlsx --peers inputs/AMZN_peers.xlsx --output AMZN_Valuation.xlsx --case base
```

Valid values for `--case` are:

```text
bear
base
bull
```

### Configuration File

After updating `config.json`, run:

```bash
python main.py
```

## Outputs

A successful run produces:

```text
AMZN_Valuation.xlsx
AMZN_Valuation.png
```

The Excel workbook contains the structured valuation analysis, while the PNG provides a visual valuation-range summary.

## Methodology

### WACC

The Weighted Average Cost of Capital combines the cost of equity and after-tax cost of debt. The cost of equity is estimated using CAPM inputs such as the risk-free rate, beta, and equity-risk premium.

### Discounting

The engine supports exact timing for the first forecast period through stub-period logic and applies the mid-year convention to subsequent forecast cash flows.

### Terminal Value

The model supports:

- Gordon Growth Method
- Exit Multiple Method

### Sensitivity Analysis

Valuation tables vary WACC and terminal-growth assumptions to show how changes in key inputs affect enterprise value and implied share price.

## Suggested Enhancements

- Add automated unit tests for WACC, terminal value, and share-price calculations
- Add Monte Carlo valuation ranges
- Introduce precedent-transactions analysis
- Add input-schema validation and example templates
- Cache and validate external market data
- Add structured logging and error reporting
- Package the application as a command-line tool

## Attribution

- **Portfolio repository:** [gawandeshil03-ops/institutional-valuation-engine](https://github.com/gawandeshil03-ops/institutional-valuation-engine)
- **Original reference repository:** [Zertax7/valuation-engine](https://github.com/Zertax7/valuation-engine)
- **Original README author credit:** Raphael

Retain applicable copyright, attribution, and license notices when reusing or redistributing referenced material.

## Disclaimer

This project is provided for educational and analytical purposes only. It does not constitute investment, accounting, tax, or financial advice. Valuation results depend on the accuracy of the source data and assumptions supplied by the user.

## Portfolio Contact

**Shil Gawande**  
[LinkedIn](https://www.linkedin.com/in/shilgawande2004) · [GitHub](https://github.com/gawandeshil03-ops) · [+91 9172937014](tel:+919172937014)

---

<div align="center">

[← Return to Main Portfolio](https://github.com/gawandeshil03-ops/data-analytics-bi-portfolio1)

</div>
