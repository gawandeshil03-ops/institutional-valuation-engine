# 📊 Institutional Valuation Engine

**A professional-grade equity valuation toolkit built in Python. Automates Discounted Cash Flow (DCF) and Trading Comparables analysis with multi-scenario support, sensitivity testing, and deal-ready Excel exports.**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Finance](https://img.shields.io/badge/Finance-DCF%20%26%20Comps-green)
![Status](https://img.shields.io/badge/Status-Production--Ready-success)

## 📖 Overview

The **Valuation Engine** is a modular financial modeling tool designed to automate the equity valuation process with precision and speed. Unlike rigid Excel templates, this engine decouples logic from data, enabling:

* **Advanced Modeling:** Automatically handles complex timing (Stub Periods, Mid-Year Convention).
* **Rapid Scenario Analysis:** Instantly calculates and compares Bear, Base, and Bull cases side-by-side.
* **Visual Insight:** Programmatically generates "Football Field" valuation charts and sensitivity heatmaps.
* **Validation:** Built-in "Sanity Checks" flag unrealistic assumptions (e.g., margins exceeding historical averages).

This project demonstrates the application of software engineering principles to complex financial modeling workflows.

---

## 🚀 Key Features

### 1. Robust DCF Engine
* **Precision Timing:** Calculates fractional discount factors based on the exact valuation date using Stub Period logic.
* **Vectorized Forecasting:** Supports non-linear growth assumptions (e.g., "Step-down" growth: 10% $\to$ 8% $\to$ 5%) rather than flat linear projections.
* **Dual Terminal Value Methods:** Supports both **Gordon Growth** and **Exit Multiple** methods.

### 2. Multi-Scenario Architecture
* Runs **Bear**, **Base**, and **Bull** cases simultaneously in a single execution.
* Outputs a dynamic side-by-side comparison of Implied Share Price, Enterprise Value, and WACC across all scenarios.

### 3. Automated Reporting
* **Excel Dashboard:** Exports a fully formatted `.xlsx` model containing:
    * Executive Summary & Scenario Comparison
    * Detailed Operating Model (Forecast)
    * DCF Build-up & WACC Calculation
    * Sensitivity Analysis (Data Tables)
    * Trading Comps
* **Visualization:** Generates a professional **"Football Field" chart** (`.png`) comparing the 52-week trading range, Analyst Targets, and DCF sensitivity ranges.

---

## 🛠️ Installation

### Prerequisites
* Python 3.8+
* `pip`

### Setup
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/valuation-engine.git](https://github.com/YOUR_USERNAME/valuation-engine.git)
    cd valuation-engine
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 📂 Project Structure

```text
Valuation Engine/
├── config.json              # Default configuration settings
├── main.py                  # Entry point (Run this file)
├── requirements.txt         # Python dependencies
├── inputs/                  # Input Data Folder
│   ├── company_financials.xlsx  # Master Financials Template
│   └── peers.xlsx               # Master Peers Template
└── src/                     # Core Logic Modules
    ├── dcf_model.py         # Discounting & Forecasting Engine
    ├── wacc.py              # Cost of Capital (CAPM) Calculation
    ├── sensitivity.py       # Data Table Generation
    ├── plotting.py          # Football Field Charting
    ├── sanity_check.py      # Logic Validation
    └── excel_export.py      # XlsxWriter Formatting Engine


## 💻 Usage

### 1. Prepare Your Data
You need two Excel files in the `inputs/` folder (templates provided in repo):

* **Financials File:** (`{Ticker}_financials.xlsx`)
    * **Income_Statement:** Historical Revenue, EBITDA, EBIT, Net Income.
    * **Balance_Sheet:** Debt, Cash, Shares Outstanding.
    * **Cash_Flow:** CapEx, Change in NWC.
    * **Assumptions:** Define your 3 scenarios (Bear/Base/Bull) for Growth, Margins, WACC, etc.

* **Peers File:** (`{Ticker}_peers.xlsx`)
    * List of competitors with EV, Revenue, and EBITDA for trading multiples analysis.

### 2. Run the Engine
You can run the engine via the command line or by editing `config.json`.

**Option A: Command Line (Recommended)**
```bash
python main.py --ticker AMZN --excel inputs/AMZN_financials.xlsx --peers inputs/AMZN_peers.xlsx --output AMZN_Valuation.xlsx --case base

**Option B: Config File Edit config.json with your specific file paths**, then simply run:
```bash
python main.py

### 3. View Results
The tool will generate:

AMZN_Valuation.xlsx: A fully formatted Excel model ready for analysis.

AMZN_Valuation.png: A valuation summary chart.

## 📊 Methodology

WACC: Calculated using CAPM (Capital Asset Pricing Model). Beta is dynamically fetched via yfinance or can be manually overridden in the assumptions.
Discounting: Uses exact day-count logic for the Stub Period (Year 1) and standard mid-year convention for subsequent years ($t-0.5$).
Sensitivity Analysis: Automatically generates data tables varying WACC and Terminal Growth Rates to stress-test the valuation.

## ⚠️ Disclaimer
This tool is for educational purposes only. It does not constitute financial advice. Valuation outputs depend entirely on the quality of the assumptions provided by the user.

## 👤 Author
Raphael Master in Management Student @ Skema Business School Aspiring Corporate Finance / Investment Banking Professional