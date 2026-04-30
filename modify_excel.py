import openpyxl
from openpyxl.comments import Comment

wb = openpyxl.load_workbook("output/AVGO_Financial_Model.xlsx", data_only=False)

# Issue 1: Comps EPS
sheet_comps = wb['7. Comps']
sheet_comps['C22'] = "='3. Income Statement'!G16*(1-'3. Income Statement'!G24)/'1. Cover'!C12"

# Issue 2: Comps median (D14 to M14)
for col_idx in range(4, 14): # D is 4, M is 13
    col_letter = openpyxl.utils.get_column_letter(col_idx)
    sheet_comps[f"{col_letter}14"] = f"=MEDIAN({col_letter}6:{col_letter}12)"

# Issue 3: SOTP margin derivation
sheet_sotp = wb['8. SOTP']
sheet_sotp['A1'] = "Blended EBITDA margin FY25A = 67.7%; Software revenue weight = 37.4%; Semi revenue weight = 62.6%"
sheet_sotp['A2'] = "If software EBITDA margin = 77% (Broadcom upper-bound), implied semi EBITDA margin = 62.0%"
comment_text = "Derived from FY25A blended 67.7% EBITDA margin and revenue mix. Software at 77% (peer benchmarks), implying semi at 62.0%."
comment_d5 = Comment(comment_text, "Author")
comment_d5.width = 300
comment_d5.height = 100
comment_d6 = Comment(comment_text, "Author")
comment_d6.width = 300
comment_d6.height = 100
sheet_sotp['D5'].comment = comment_d5
sheet_sotp['D6'].comment = comment_d6

# Issue 4: DCF WACC hardcode to 9.5% and Football field link
sheet_wacc = wb['5. WACC']
sheet_wacc['C12'] = 0.095

sheet_football = wb['10. Football Field']
sheet_football['D5'] = "='4. DCF'!C25"

wb.save("output/AVGO_Financial_Model.xlsx")
print("Excel modifications saved.")
