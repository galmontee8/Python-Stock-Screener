import pandas as pd

class TableauCleaner:
    def __init__(self, filepath):
        self.filepath = filepath
        
    def consolidate_industries(self, df):
        # We use keywords to bucket the 174 SEC industries into 12 Macro Sectors
        def map_sector(industry_str):
            ind = str(industry_str).upper()
            
            if any(word in ind for word in ['BANK', 'FINANC', 'INSURANCE', 'INVEST', 'CREDIT', 'SAVINGS']):
                return 'Financials'
            elif any(word in ind for word in ['SOFTWARE', 'COMPUTER', 'TECH', 'SEMICONDUCTOR', 'DATA']):
                return 'Technology'
            elif any(word in ind for word in ['MEDICAL', 'PHARMA', 'HEALTH', 'BIOLOGICAL', 'SURGICAL']):
                return 'Healthcare'
            elif any(word in ind for word in ['REAL ESTATE', 'REIT', 'BUILDING']):
                return 'Real Estate'
            elif any(word in ind for word in ['HOTEL', 'MOTEL', 'LODGING', 'RESORT', 'HOSPITALITY']):
                return 'Hotels & Lodging'
            elif any(word in ind for word in ['MOTOR', 'VEHICLE', 'AUTO', 'TRUCK', 'PARTS']):
                return 'Automotive & Vehicles'
            elif any(word in ind for word in ['OIL', 'GAS', 'ENERGY', 'MINING', 'PETROLEUM']):
                return 'Energy & Materials'
            elif any(word in ind for word in ['RETAIL', 'WHOLESALE', 'APPAREL', 'RESTAURANT', 'FOOD', 'BEVERAGE']):
                return 'Consumer & Retail'
            elif any(word in ind for word in ['MANUFACTURING', 'INDUSTRIAL', 'MACHINERY', 'METAL', 'TRANSPORT']):
                return 'Industrials'
            elif any(word in ind for word in ['TELECOM', 'COMMUNICATION', 'RADIO', 'TV']):
                return 'Communications'
            elif any(word in ind for word in ['UTILITY', 'WATER', 'ELECTRIC']):
                return 'Utilities'
            else:
                return 'Other/Diversified'
        
        # Create a brand new column for Tableau
        df['Macro_Sector'] = df['Industry'].apply(map_sector)
        return df

    def filter_na_rows(self, output_filename="tableau_perfect_data.csv"):
        print(f"\n[INIT] Sweeping through {self.filepath} for Tableau prep...")
        
        df = pd.read_csv(self.filepath)
        original_size = len(df)
        
        # 1. Clean the N/A values
        df.replace("N/A", pd.NA, inplace=True)
        clean_df = df.dropna().copy() 
        
        # 2. Consolidate the 174 Industries into 12 Macro Sectors
        clean_df = self.consolidate_industries(clean_df)
        
        final_size = len(clean_df)
        dropped = original_size - final_size
        
        # 3. Save the flawless data
        clean_df.to_csv(output_filename, index=False)
        
        print(f"[REPORT] Dropped {dropped} companies with incomplete data.")
        print(f"[REPORT] Consolidated 174 micro-industries into 12 Macro Sectors.")
        print(f"[SUCCESS] Saved {final_size} flawless rows to {output_filename}.")
        
        return clean_df

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # Point it to the file you just generated
    cleaner = TableauCleaner("gold_standard_results.csv")
    
    # Run the ETL process
    cleaner.filter_na_rows("tableau_perfect_data.csv")