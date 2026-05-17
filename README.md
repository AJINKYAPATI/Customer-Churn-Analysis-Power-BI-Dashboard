# 📊 Customer Churn Analysis — Power BI Dashboard

![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen?style=for-the-badge)
![Domain](https://img.shields.io/badge/Domain-Business%20Intelligence-blue?style=for-the-badge)

---

## 📌 Project Overview

This project presents an end-to-end **Customer Churn Analysis** solution built using **Microsoft Power BI**. The dashboards analyze a telecom company's customer data to identify churn patterns, at-risk customers, and key business metrics — enabling data-driven decisions to improve customer retention and reduce revenue loss.

The project consists of **two interactive dashboards**:
- 🔴 **Customer Churn Dashboard** — Operational view of at-risk customers
- 🟡 **Customer Risk Analysis Dashboard** — Deep-dive into churn drivers and risk factors

---

## 🖥️ Dashboard Previews

### 1. Customer Churn Dashboard
![Customer Churn Dashboard](Customer_Churn_Dashboard.png)

### 2. Customer Risk Analysis Dashboard
![Customer Risk Analysis Dashboard](Customer_Risk_Analysis.png)

---

## 📈 Key Metrics & Insights

### 🔢 High-Level KPIs

| Metric | Value |
|---|---|
| Total Customers | 7,043 |
| Customers at Risk | 1,869 |
| Overall Churn Rate | 26.54% |
| Yearly Charges | $16.06M |
| Monthly Charges | $139.13K |
| Tech Support Tickets | 2,955 |
| Admin Tickets | 3,632 |

---

### 🔍 Key Findings

#### 📡 Churn by Internet Service
- **Fiber Optic** users had the highest churn rate at **41.89%**
- **DSL** users churned at **18.96%**
- Customers with **No internet service** had the lowest churn at **7.40%**

#### 📄 Churn by Contract Type
- **Month-to-Month** contracts had the highest churn rate of **42.71%** (majority of customers)
- **One-year** contracts: **11.27%** churn
- **Two-year** contracts: **2.83%** churn — most loyal customers

#### 📅 Churn by Tenure (Subscription Time)
- Customers with **< 1 Year** tenure had the highest churn at **55.48%**
- Churn drops significantly as tenure increases, highlighting the need for strong early engagement

#### 💳 Churn by Payment Method
- **Electronic Check** users had the highest churn rate at **45.29%**
- **Mailed Check**: 19.11% | **Bank Transfer**: 16.71% | **Credit Card**: 15.24%

#### 👥 Customer Demographics
- **25%** of churned customers are **Senior Citizens**
- **36%** have a **Partner** | **17%** have **Dependents**
- Gender split is nearly equal: **Female 49.76%** | **Male 50.24%**

#### 📦 Subscribed Services Adoption
| Service | Adoption Rate |
|---|---|
| Phone Service | 91% |
| Streaming TV | 44% |
| Streaming Movies | 44% |
| Device Protection | 29% |
| Online Backup | 28% |
| Tech Support | 17% |
| Online Security | 16% |

---

## 🛠️ Tools & Technologies

| Tool | Purpose |
|---|---|
| **Power BI Desktop** | Dashboard design & data visualization |
| **DAX** | Calculated measures, KPIs & custom metrics |
| **Power Query (M Language)** | Data cleaning & transformation |
| **Microsoft Excel / CSV** | Data source |

---

## 📂 Project Structure

```
Customer-Churn-Analysis-PowerBI/
│
├── 📁 Dataset/
│   └── customer_churn_data.csv         # Raw dataset
│
├── 📁 Dashboard/
│   └── Customer_Churn_Analysis.pbix    # Power BI file
│
├── 📁 Screenshots/
│   ├── Customer_Churn_Dashboard.png
│   └── Customer_Risk_Analysis.png
│
└── README.md
```

## 💡 Business Impact

- 📉 Identified **1,869 at-risk customers** representing **$2.86M** in potential yearly revenue loss
- 🎯 Pinpointed **Fiber Optic + Month-to-Month + Electronic Check** as the highest churn risk combination
- 📊 Revealed that customers in their **first year** are most vulnerable — enabling targeted early retention strategies
- 🔒 Recommended promoting **long-term contracts** and **auto-payment methods** to reduce churn

---

## 🚀 Future Improvements

- [ ] Integrate **Machine Learning model** (Logistic Regression / Random Forest) for churn prediction
- [ ] Add **customer lifetime value (CLV)** metric
- [ ] Automate data refresh using **Power BI Service**
- [ ] Build a **real-time churn alert system** using Power BI + Azure
