import pandas as pd
from typing import Dict, List

def export_to_excel(
    summary_data: Dict[str, float],
    forecast_data: List[Dict[str, float]],
    dcf_data: Dict[str, float],
    comps_data: Dict[str, object],
    sensitivity_df: pd.DataFrame,
    scenario_data: Dict[str, Dict[str, float]],
    filename: str = "valuation_output.xlsx"
):
    """
    Writes all valuation outputs to a multi-tab Excel file with formatting.
    """
    
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    workbook = writer.book

    # =========================
    # DEFINING FORMATS
    # =========================
    header_fmt = workbook.add_format({
        'bold': True, 'text_wrap': True, 'valign': 'top',
        'fg_color': '#D7E4BC', 'border': 1
    })
    currency_fmt = workbook.add_format({'num_format': '$#,##0.00'})
    percent_fmt = workbook.add_format({'num_format': '0.0%'})
    float_fmt = workbook.add_format({'num_format': '#,##0.00'})
    bold_fmt = workbook.add_format({'bold': True})

    # =========================
    # SUMMARY TAB
    # =========================
    summary_df = pd.DataFrame(list(summary_data.items()), columns=["Metric", "Value"])
    summary_df.to_excel(writer, sheet_name='Summary', index=False, startrow=1)
    
    sheet = writer.sheets['Summary']
    sheet.set_column('A:A', 25)
    sheet.set_column('B:B', 15, currency_fmt)
    sheet.write(0, 0, "EXECUTIVE SUMMARY", bold_fmt)

    # =========================
    # SCENARIOS TAB
    # =========================
    
    if scenario_data:
        # Create a list of metrics we want to compare
        metrics = [
            "Implied Share Price", 
            "Equity Value", 
            "Enterprise Value", 
            "WACC", 
            "Terminal Growth Rate", 
            "Exit Multiple"
        ]
        
        data_rows = []
        for m in metrics:
            row = {"Metric": m}
            for case in ["bear", "base", "bull"]:
                # Get value, default to 0 if missing
                val = scenario_data.get(case, {}).get(m, 0)
                row[case.title()] = val
            data_rows.append(row)
            
        scenarios_df = pd.DataFrame(data_rows)
        # Reorder columns just in case
        scenarios_df = scenarios_df[["Metric", "Bear", "Base", "Bull"]]
        
        scenarios_df.to_excel(writer, sheet_name='Scenarios', index=False, startrow=1)
        
        sheet = writer.sheets['Scenarios']
        sheet.write(0, 0, "SCENARIO ANALYSIS", bold_fmt)
        
        # Apply formatting
        for col_num, value in enumerate(scenarios_df.columns.values):
            sheet.write(1, col_num, value, header_fmt)
            
        sheet.set_column('A:A', 25)
        sheet.set_column('B:D', 18)
        
        # Apply currency format to Price, Equity, Enterprise
        # These are rows 0, 1, 2 in the dataframe (so Excel rows 2, 3, 4)
        for r in range(2, 5): 
            sheet.write_row(r, 1, scenarios_df.iloc[r-2, 1:], currency_fmt)
            
        # Apply % format to WACC, Terminal Growth (rows 3, 4 -> Excel 5, 6)
        for r in range(5, 7):
            sheet.write_row(r, 1, scenarios_df.iloc[r-2, 1:], percent_fmt)

    # =========================
    # FORECAST TAB
    # =========================
    forecast_df = pd.DataFrame(forecast_data)
    forecast_df.to_excel(writer, sheet_name='Forecast', index=False, startrow=1)
    
    sheet = writer.sheets['Forecast']
    for col_num, value in enumerate(forecast_df.columns.values):
        sheet.write(1, col_num, value, header_fmt)

    sheet.set_column('A:A', 10)
    sheet.set_column('B:G', 15, currency_fmt)
    sheet.write(0, 0, "OPERATING FORECAST (Selected Case)", bold_fmt)

    # =========================
    # DCF TAB
    # =========================
    dcf_build_df = pd.DataFrame(dcf_data.get("discounted_fcff", []))
    val_output = {k: v for k, v in dcf_data.items() if k != "discounted_fcff"}
    val_df = pd.DataFrame(list(val_output.items()), columns=["Item", "Amount"])

    dcf_build_df.to_excel(writer, sheet_name='DCF', index=False, startrow=2)
    start_row_val = len(dcf_build_df) + 5
    val_df.to_excel(writer, sheet_name='DCF', index=False, startrow=start_row_val)
    
    sheet = writer.sheets['DCF']
    sheet.write(0, 0, "DISCOUNTED CASH FLOW ANALYSIS (Selected Case)", bold_fmt)
    
    for col_num, value in enumerate(dcf_build_df.columns.values):
        sheet.write(2, col_num, value, header_fmt)
        
    sheet.set_column('A:A', 10)
    sheet.set_column('B:Z', 18, currency_fmt)
    sheet.write(start_row_val - 1, 0, "VALUATION SUMMARY", bold_fmt)

    # =========================
    # COMPS TAB
    # =========================
    if comps_data:
        comps_rows = []
        implied_val = comps_data.get("implied_valuation", {})
        for method, values in implied_val.items():
            row = {"Method": method}
            row.update(values)
            comps_rows.append(row)
            
        comps_df = pd.DataFrame(comps_rows)
        comps_df.to_excel(writer, sheet_name='Comps', index=False, startrow=1)
        
        sheet = writer.sheets['Comps']
        sheet.write(0, 0, "TRADING COMPARABLES SUMMARY", bold_fmt)
        for col_num, value in enumerate(comps_df.columns.values):
            sheet.write(1, col_num, value, header_fmt)
        sheet.set_column('A:A', 20)
        sheet.set_column('B:C', 18, currency_fmt)

    # =========================
    # SENSITIVITY TAB
    # =========================
    sensitivity_df.to_excel(writer, sheet_name='Sensitivity', startrow=2, startcol=1)
    
    sheet = writer.sheets['Sensitivity']
    sheet.write(0, 0, "SENSITIVITY ANALYSIS (Share Price)", bold_fmt)
    sheet.write(2, 0, "Growth \\ WACC", bold_fmt)
    
    num_rows, num_cols = sensitivity_df.shape
    sheet.set_column(1, num_cols + 1, 15, currency_fmt)
    sheet.conditional_format(3, 2, 3 + num_rows - 1, 2 + num_cols - 1,
                             {'type': '3_color_scale',
                              'min_color': "#F8696B",
                              'mid_color': "#FFEB84",
                              'max_color': "#63BE7B"})

    writer.close()
    print(f"✅ Successfully exported valuation to {filename}")