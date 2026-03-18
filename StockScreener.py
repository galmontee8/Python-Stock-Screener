import pandas as pd
import requests
import time

class StockScreener:
    def __init__(self, csv_filepath, email_contact):
        self.headers = {'User-Agent': f"Research Project {email_contact}"}
        
        # 1. Load CSV
        print(f"[INIT] Loading {csv_filepath}...")
        self.df = pd.read_csv(csv_filepath)
        original_count = len(self.df)
        
        # 2. Clean Data
        # Step A: Convert LAST column (CIK) to numeric
        self.df.iloc[:, -1] = pd.to_numeric(self.df.iloc[:, -1], errors='coerce')
        
        # Step B: Drop rows where CIK is missing
        self.df = self.df.dropna(subset=[self.df.columns[-1]])
        
        # Step C: Normalize CIK (123 -> "0000000123")
        self.df.iloc[:, -1] = self.df.iloc[:, -1].apply(lambda x: str(int(x)).zfill(10))
        
        # Step D: Create Map {Ticker : CIK}
        self.cik_map = dict(zip(self.df.iloc[:, 0], self.df.iloc[:, -1]))
        
        # --- REPORTING ---
        current_count = len(self.df)
        dropped_count = original_count - current_count
        if dropped_count > 0:
            print(f"[INFO] Dropped {dropped_count} rows (missing CIKs).")
        print(f"[INFO] Successfully loaded {current_count} companies.")

    def get_company_identity(self, cik):
        """Fetches Industry/Sector info."""
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return {
                    "Industry": data.get("sicDescription", "Unknown"),
                    "SIC_Code": data.get("sic", "Unknown")
                }
            return {"Industry": "Unknown", "SIC_Code": "Unknown"}
        except:
            return {"Industry": "Unknown", "SIC_Code": "Unknown"}

    def get_all_company_facts(self, cik):
        """Downloads all financial data (XBRL) in one go."""
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None

    def extract_series(self, facts_json, concept_name):
        """Helper to find data in the local JSON."""
        try:
            data = facts_json['facts']['us-gaap'][concept_name]['units']
            if 'USD' in data:
                df = pd.DataFrame(data['USD'])
            elif 'USD/shares' in data:
                df = pd.DataFrame(data['USD/shares'])
            else:
                return pd.DataFrame()
            return df[df['form'] == '10-K'].sort_values('end')
        except KeyError:
            return pd.DataFrame()

    def calculate_metrics(self, ticker):
        cik = self.cik_map.get(ticker)
        if not cik: return {"Ticker": ticker, "Error": "CIK Not Found"}

        # --- REQUESTS ---
        identity = self.get_company_identity(cik)
        facts = self.get_all_company_facts(cik)
        
        if not facts:
            return {"Ticker": ticker, "Error": "No Data / SEC Error"}

        # --- DATA EXTRACTION ---
        
        # 1. REVENUE
        rev_ann = pd.DataFrame()
        revenue_tags = ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", 
                        "SalesRevenueNet", "SalesRevenueGoodsNet"]
        for tag in revenue_tags:
            rev_ann = self.extract_series(facts, tag)
            if not rev_ann.empty: break
            
        # 2. NET INCOME
        net_ann = self.extract_series(facts, "NetIncomeLoss")
        if net_ann.empty: net_ann = self.extract_series(facts, "ProfitLoss")

        # 3. EPS
        eps_ann = self.extract_series(facts, "EarningsPerShareDiluted")
        if eps_ann.empty: eps_ann = self.extract_series(facts, "EarningsPerShareBasic")
        
        # 4. DEBT & EQUITY (For ROIC)
        st_debt = self.extract_series(facts, "ShortTermBorrowings")
        lt_debt = self.extract_series(facts, "LongTermDebtNoncurrent")
        if lt_debt.empty: lt_debt = self.extract_series(facts, "LongTermDebt")
        
        equity = self.extract_series(facts, "StockholdersEquity")
        if equity.empty: equity = self.extract_series(facts, "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest")

        # 5. CURRENT ASSETS/LIABILITIES (For Current Ratio)
        curr_assets = self.extract_series(facts, "AssetsCurrent")
        curr_liab = self.extract_series(facts, "LiabilitiesCurrent")

        # 6. CASH FLOW COMPONENTS (For Free Cash Flow)
        cf_ops = self.extract_series(facts, "NetCashProvidedByUsedInOperatingActivities")
        capex = self.extract_series(facts, "PaymentsToAcquirePropertyPlantAndEquipment")

        # 7. EBITDA Components
        interest = self.extract_series(facts, "InterestExpense")
        taxes = self.extract_series(facts, "IncomeTaxExpenseBenefit")
        depr = self.extract_series(facts, "DepreciationDepletionAndAmortization")

        results = {
            "Ticker": ticker, 
            "CIK": cik,
            "Industry": identity["Industry"]
        }

        try:
            # Helper to safely get the last value or None
            def get_val(series):
                return series.iloc[-1]['val'] if not series.empty else None

            # --- FETCH RAW VALUES ---
            val_net = get_val(net_ann)
            val_st_debt = get_val(st_debt)
            val_lt_debt = get_val(lt_debt)
            val_equity = get_val(equity)
            val_assets_c = get_val(curr_assets)
            val_liab_c = get_val(curr_liab)
            val_cf_ops = get_val(cf_ops)
            val_capex = get_val(capex)
            
            # --- METRIC 1: REVENUE GROWTH ---
            if len(rev_ann) >= 2:
                prev_rev = rev_ann.iloc[-2]['val']
                curr_rev = rev_ann.iloc[-1]['val']
                results["Input_Rev_Prev"] = prev_rev
                results["Input_Rev_Curr"] = curr_rev
                if prev_rev != 0:
                    results["Revenue_Growth"] = (curr_rev - prev_rev) / prev_rev
                else:
                    results["Revenue_Growth"] = "N/A"
            else:
                results["Input_Rev_Prev"] = "N/A"
                results["Input_Rev_Curr"] = "N/A"
                results["Revenue_Growth"] = "N/A"

            # --- METRIC 2: EARNINGS GROWTH ---
            if len(net_ann) >= 2:
                prev_earn = net_ann.iloc[-2]['val']
                curr_earn = net_ann.iloc[-1]['val']
                results["Input_NetInc_Prev"] = prev_earn
                results["Input_NetInc_Curr"] = curr_earn
                if prev_earn != 0:
                    results["Earnings_Growth"] = (curr_earn - prev_earn) / prev_earn
                else:
                    results["Earnings_Growth"] = "N/A"
            else:
                results["Input_NetInc_Prev"] = "N/A"
                results["Input_NetInc_Curr"] = "N/A"
                results["Earnings_Growth"] = "N/A"

            # --- METRIC 3: AUDITED EPS ---
            results["Audited_EPS"] = get_val(eps_ann) if get_val(eps_ann) is not None else "N/A"

            # --- METRIC 4: FREE CASH FLOW (FCF) ---
            # FCF = Operating Cash Flow - CapEx
            results["Input_NetCash_Op"] = val_cf_ops if val_cf_ops is not None else "N/A"
            results["Input_CapEx"] = val_capex if val_capex is not None else "N/A"
            
            if val_cf_ops is not None:
                # If CapEx is missing, assume 0 (some companies have no CapEx)
                capex_safe = val_capex if val_capex is not None else 0
                results["Free_Cash_Flow"] = val_cf_ops - capex_safe
            else:
                results["Free_Cash_Flow"] = "N/A"

            # --- METRIC 5: CURRENT RATIO (Solvency) ---
            results["Input_Assets_Curr"] = val_assets_c if val_assets_c is not None else "N/A"
            results["Input_Liab_Curr"] = val_liab_c if val_liab_c is not None else "N/A"
            
            if val_assets_c is not None and val_liab_c is not None and val_liab_c != 0:
                results["Current_Ratio"] = round(val_assets_c / val_liab_c, 2)
            else:
                results["Current_Ratio"] = "N/A"

            # --- METRIC 6: ROIC (Return on Invested Capital) ---
            results["Input_Equity"] = val_equity if val_equity is not None else "N/A"
            
            invested_capital = ((val_st_debt or 0) + (val_lt_debt or 0) + (val_equity or 0))
            
            if val_net is not None and invested_capital != 0:
                results["ROIC"] = round(val_net / invested_capital, 4) 
            else:
                results["ROIC"] = "N/A"

            # --- METRIC 7: DEBT TO EBITDA ---
            val_int = get_val(interest)
            val_tax = get_val(taxes)
            val_depr = get_val(depr)
            
            ebitda = (val_net or 0) + (val_int or 0) + (val_tax or 0) + (val_depr or 0)
            total_debt = (val_st_debt or 0) + (val_lt_debt or 0)
            
            if ebitda > 0:
                results["Debt_to_EBITDA"] = round(total_debt / ebitda, 2)
            else:
                results["Debt_to_EBITDA"] = 999 

        except Exception as e:
            return {"Ticker": ticker, "Error": str(e)}

        return results

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    FILE_PATH = "sp-600-with-ciks.csv" 
    
    # Initialize
    screener = StockScreener(FILE_PATH, email_contact="almonteeg@gmail.com")
    
    gold_standard = []
    new_companies = []
    skipped = []
    
    tickers = list(screener.cik_map.keys())
    total = len(tickers)
    
    print(f"--- FULL AUDIT STARTING: {total} COMPANIES ---")
    print("Estimated time: ~8 minutes (2 requests per stock)")

    for i, t in enumerate(tickers, 1):
        data = screener.calculate_metrics(t)
        
        if i % 25 == 0:
            print(f"   Progress: {i}/{total}...")

        if "Error" in data:
            skipped.append(data)
        elif data["Revenue_Growth"] == "N/A":
            new_companies.append(data)
        else:
            gold_standard.append(data)
        
        time.sleep(0.15) 

    # Save Results
    if gold_standard:
        pd.DataFrame(gold_standard).to_csv("gold_standard_results.csv", index=False)
        print("Saved gold_standard_results.csv")
        
    if new_companies:
        pd.DataFrame(new_companies).to_csv("new_companies_watch_list.csv", index=False)
        print("Saved new_companies_watch_list.csv")
        
    print(f"\n[DONE] Processed {total} companies.")
    print(f"Valid: {len(gold_standard)} | New: {len(new_companies)} | Skipped: {len(skipped)}")