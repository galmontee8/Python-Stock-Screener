# Python-Stock-Screener
## Overview
This project is a high-performance data extraction and financial analysis tool built to audit the S&P 600 index. By interfacing directly with the SEC EDGAR API, the script pulls raw XBRL (eXtensible Business Reporting Language) facts to calculate institutional-grade valuation metrics that aren't always available on retail platforms.
## Data Validation & Output Segmentation
The core logic of this screener is built on comparative analytics. To calculate growth and efficiency ratios, the script segments the S&P 600 (sp-600-with-ciks.csv) into two distinct groups based on available documentation:

### 1. Gold Standard Results (gold_standard_results.csv)
These are the companies with enough data for a full quantitative audit.

Criteria: Companies with at least two SEC filings (e.g., two 10-K annual reports).

Why it matters: Two filings provide the necessary data points to calculate Year-over-Year (YoY) Growth, ROIC, and Debt-to-EBITDA. This ensures the metrics represent a trend rather than a single snapshot in time.

### 2. New Companies Watch List (new_companies_watch_list.csv)
These are companies that are officially part of the index but lack sufficient history for comparison.

Criteria: Companies with only one SEC filing or missing historical XBRL tags.

Why it matters: While we can see their current financial health, we can't calculate growth metrics. These are separated to keep the "Gold Standard" list focused on companies with verifiable performance trends.
## Core Features
Automated SEC Data Retrieval: Programmatically fetches companyfacts JSON data using normalized CIK (Central Index Key) identifiers.

XBRL Tag Mapping: Maps inconsistent GAAP tags (e.g., Revenues vs SalesRevenueNet) into a standardized data frame.

Quantitative Audit Engine: Calculates year-over-year (YoY) growth and solvency ratios.

Data Validation Pipeline: Automatically categorizes companies into "Gold Standard" (full history), "Watch List" (new/incomplete), or "Skipped" (filing errors).
## Key Metrics Calculated 
The screener uses raw financial statements to derive: ROIC (Return on Invested Capital): $\frac{\text{Net Income}}{\text{Debt} + \text{Equity}}$ — measures capital efficiency.

Free Cash Flow (FCF): $\text{Operating Cash Flow} - (\text{CapEx} - \text{Asset Disposals})$ determines actual liquidity.

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
