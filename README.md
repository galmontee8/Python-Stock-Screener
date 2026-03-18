# Python-Stock-Screener
## Overview
This project is a high-performance data extraction and financial analysis tool built to audit the sp-600-with-ciks index. By interfacing directly with the SEC EDGAR API, the script pulls raw XBRL (eXtensible Business Reporting Language) facts to calculate institutional-grade valuation metrics that aren't always available on retail platforms.
## Core Features
Automated SEC Data Retrieval: Programmatically fetches companyfacts JSON data using normalized CIK (Central Index Key) identifiers.

XBRL Tag Mapping: Maps inconsistent GAAP tags (e.g., Revenues vs SalesRevenueNet) into a standardized data frame.

Quantitative Audit Engine: Calculates year-over-year (YoY) growth and solvency ratios.

Data Validation Pipeline: Automatically categorizes companies into "Gold Standard" (full history), "Watch List" (new/incomplete), or "Skipped" (filing errors).
## Key Metrics Calculated 
The screener uses raw financial statements to derive: ROIC (Return on Invested Capital): $\frac{\text{Net Income}}{\text{Debt} + \text{Equity}}$ — measures capital efficiency.

Free Cash Flow (FCF): $\text{Operating Cash Flow} - \text{CapEx}$ determines actual liquidity.

Debt-to-EBITDA: Measures leverage by reconstructing EBITDA from Net Income, Interest, Taxes, and Depreciation.YoY Revenue & Earnings Growth: Identifies fundamental momentum.
