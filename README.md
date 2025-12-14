📊 Enterprise-Grade Power BI – Sales Performance & Trend Analysis
📌 Project Overview

This project implements an enterprise-grade Sales Performance & Trend Analysis Dashboard using Power BI Desktop.
The solution follows BI best practices, including star schema modeling, Power Query transformations, DAX time intelligence, interactive dashboards, Excel integration, and advanced visuals.

The dashboard enables stakeholders to monitor sales performance, identify trends, compare regions and products, and take data-driven decisions.

🎯 Business Objectives

Analyze Sales, Profit, and Quantity

Track monthly and yearly trends

Compare performance across regions, categories, and products

Evaluate actual performance vs targets

Enable interactive decision-making

❓ Key Business Questions

How are sales trending monthly and yearly?

Which categories contribute the most to profit?

Which regions are underperforming?

How does actual sales compare with targets?

🗂️ Data Sources & Integration

Sales Dataset (Excel / CSV)
Contains orders, products, customers, regions, sales, quantity, discount, and profit.

Targets Dataset (Excel)
Monthly regional sales targets derived from historical trends.

Date Dimension (DAX)
Custom calendar table for time intelligence.

Excel is treated as the single source of truth, and Power BI refreshes data directly from Excel files.

🧱 Data Model (Star Schema)

The report follows a Star Schema design for performance and scalability:

FactSales – Transactional sales data

DimDate – Date dimension (Year, Month, YearMonth)

DimProduct – Product, Category, Sub-Category

DimCustomer – Customer and segment details

DimRegion – Regional hierarchy

Relationships are one-to-many with single-direction filtering.

🔄 Power Query Transformations

Removed nulls and duplicates

Standardized data types

Created conditional column for Sales Category (High / Medium / Low)

Prepared dimension tables using Power Query references

Optimized data before DAX calculations

🧮 DAX Measures & Time Intelligence

Key measures created using DAX:

Total Sales

Total Profit

Total Quantity

Profit Margin %

Sales YTD

Sales LY (Last Year)

YoY Growth %

Target Achievement %

Time intelligence functions such as TOTALYTD, DATEADD, and SAMEPERIODLASTYEAR are used for trend analysis.

📈 Report Pages & Visuals
1️⃣ Executive Dashboard

KPI Cards (Sales, Profit, YoY Growth)

Line Chart – Sales Trend

Donut Chart – Sales by Category

Ribbon Chart – Category Rank Over Time

2️⃣ Trend Analysis

Line Chart – Sales & Profit

Line + Stacked Column Chart – Sales vs Profit

Shape Map – Sales by Region

3️⃣ Product Performance

Matrix (Category → Sub-Category → Product)

Conditional Formatting:

Data bars for Sales

Color scale for Profit

Top-N filter (Top 10 Products by Sales)

🎨 Formatting & Filters

Report-level filters:

Year

Region

Category

Filters applied once and affect all pages

Bold totals and clean formatting for readability

🧭 Dashboard & Actions

Report published to Power BI Service

Key visuals pinned to a Dashboard

Page navigation actions enabled (KPI → detail page)

Q&A visual added for natural language queries

KPI alerts configured for performance monitoring

🔬 Advanced Visuals (R Script)

Integrated R Script Visual for advanced analytics

Monthly sales trend plotted using R

Demonstrated trend forecasting conceptually using regression

Addressed Power BI R visual limitations through aggregation and margin handling

🧠 Key Learnings

Importance of star schema for BI performance

Correct use of date dimensions for time intelligence

Difference between Power Query transformations and DAX calculations

Practical handling of Power BI Service dashboards and alerts

Integrating advanced analytics using R

✅ Conclusion

This project demonstrates a complete enterprise BI workflow, from raw data ingestion to executive-level dashboards.
It showcases strong understanding of data modeling, analytics, visualization, and business insight generation, aligned with real-world enterprise reporting standards.
