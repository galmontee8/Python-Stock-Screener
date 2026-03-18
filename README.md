# Python-Stock-Screener
## Overview
This project is a high-performance data extraction and financial analysis tool built to audit the sp-600-with-ciks index. By interfacing directly with the SEC EDGAR API, the script pulls raw XBRL (eXtensible Business Reporting Language) facts to calculate institutional-grade valuation metrics that aren't always available on retail platforms.
## Data Source & Indexing
The core of this audit is built around the sp-600-with-ciks.csv dataset.

Target Index: S&P 600 Small-Cap Index.

Identifier Mapping: The script utilizes a pre-mapped CSV of tickers and their corresponding Central Index Keys (CIK) to ensure 100% accuracy when querying the SEC EDGAR database.

Normalization: Includes a custom pipeline to pad CIKs with leading zeros, meeting the SEC’s strict 10-digit string requirement for RESTful API calls.
## Core Features
Automated SEC Data Retrieval: Programmatically fetches companyfacts JSON data using normalized CIK (Central Index Key) identifiers.

XBRL Tag Mapping: Maps inconsistent GAAP tags (e.g., Revenues vs SalesRevenueNet) into a standardized data frame.

Quantitative Audit Engine: Calculates year-over-year (YoY) growth and solvency ratios.

Data Validation Pipeline: Automatically categorizes companies into "Gold Standard" (full history), "Watch List" (new/incomplete), or "Skipped" (filing errors).
## Key Metrics Calculated 
The screener uses raw financial statements to derive: ROIC (Return on Invested Capital): $\frac{\text{Net Income}}{\text{Debt} + \text{Equity}}$ — measures capital efficiency.

Free Cash Flow (FCF): $\text{Operating Cash Flow} - \text{CapEx}$ determines actual liquidity.

Debt-to-EBITDA: Measures leverage by reconstructing EBITDA from Net Income, Interest, Taxes, and Depreciation.YoY Revenue & Earnings Growth: Identifies fundamental momentum.
## Technical Stack
Language: Python 3.x

Libraries: Pandas (Data manipulation), Requests (API handling), Time (Rate-limiting compliance).

Data Source: SEC EDGAR RESTful API.
## How to Run
Clone the repo: git clone https://github.com/galmontee8/Python-Stock-Screener.git

Install dependencies: pip install pandas requests

Execute the audit: python StockScreener.py
## Last-Minute Check
Before you hit "Commit":

Upload the Code: Make sure StockScreener.py is actually in the repo.

Upload the Data: Drop gold_standard_results.csv in there.

The Header: Make sure your GitHub profile has your real name so it matches your resume.
