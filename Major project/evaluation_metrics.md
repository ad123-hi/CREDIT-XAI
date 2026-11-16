# Model Evaluation Report: Lending Club Loan Default Prediction

This document provides a comprehensive summary of the performance metrics obtained by the final Gradient Boosting Classifier trained via [train.py](file:///c:/Users/chinm/Desktop/Major%20project/train.py).

---

## 1. Executive Summary

The model predicts the probability of a borrower defaulting on a loan (binary classification: `Charged Off = 1`, `Fully Paid = 0`). It was evaluated on a balanced test set containing 4,000 records.

* **Final Model**: Gradient Boosting Classifier
* **Hyperparameters**: `max_depth=3`, `n_estimators=250`
* **Test Accuracy**: **87.90%**
* **Baseline Notebook Accuracy**: **87.75%**

---

## 2. Detailed Classification Report

| Metric | Class 0 (Fully Paid) | Class 1 (Charged Off) | Macro Average | Weighted Average |
| :--- | :--- | :--- | :--- | :--- |
| **Precision** | 0.93 | 0.84 | 0.88 | 0.88 |
| **Recall** | 0.82 | 0.94 | 0.88 | 0.88 |
| **F1-Score** | 0.87 | 0.89 | 0.88 | 0.88 |
| **Support** | 1,997 | 2,003 | 4,000 | 4,000 |

* **Key Takeaway**: The model displays a strong recall of **94%** for predicting defaults (`Charged Off`), which is critical for risk assessment, while maintaining high precision (**93%**) for identifying safe borrowers (`Fully Paid`).

---

## 3. Confusion Matrix

| | Predicted Fully Paid (0) | Predicted Charged Off (1) |
| :--- | :---: | :---: |
| **Actual Fully Paid (0)** | **1,639** (True Negatives) | **358** (False Positives) |
| **Actual Charged Off (1)** | **126** (False Negatives) | **1,877** (True Positives) |

---

## 4. Feature Importances
The features are ranked by their relative Gini importance in the Gradient Boosting decision splits. The corresponding plot is saved as [feature_importances.png](file:///c:/Users/chinm/Desktop/Major%20project/feature_importances.png).

| Rank | Feature Name | Description | Relative Importance |
| :---: | :--- | :--- | :---: |
| 1 | `last_pymnt_amnt` | Last payment amount received | 80.0835% |
| 2 | `sub_grade` | Lending Club assigned sub-grade | 5.3817% |
| 3 | `term` | Length of loan (36 or 60 months) | 4.4255% |
| 4 | `installment` | Monthly payment amount | 3.1661% |
| 5 | `int_rate` | Interest rate of the loan | 1.4149% |
| 6 | `acc_open_past_24mths` | Number of accounts opened in past 24m | 1.2882% |
| 7 | `mo_sin_old_rev_tl_op` | Months since oldest revolving account opened | 0.3775% |
| 8 | `funded_amnt` | Funded amount of the loan | 0.3380% |
| 9 | `loan_amnt` | Requested loan amount | 0.3373% |
| 10 | `log_annual_inc` | Log10 transformed annual income | 0.3269% |
| 11 | `dti` | Debt-to-income ratio | 0.3149% |
| 12 | `avg_cur_bal` | Average current balance of all accounts | 0.3124% |
| 13 | `earliest_cr_line` | Year the earliest credit line was opened | 0.2989% |
| 14 | `bc_open_to_buy` | Total open to buy on revolving credit | 0.2343% |
| 15 | `bc_util` | Ratio of total balance to credit limit on cards | 0.2098% |
| 16 | `fico_score` | Average of high/low FICO range scores | 0.1953% |
| 17 | `revol_util` | Revolving line utilization rate | 0.1857% |
| 18 | `initial_list_status` | Initial listing status of the loan | 0.1781% |
| 19 | `grade` | Lending Club assigned grade | 0.1604% |
| 20 | `mo_sin_rcnt_rev_tl_op` | Months since most recent revolving account opened | 0.1583% |
| 21 | `purpose` | A category provided by the borrower for the loan | 0.1581% |
| 22 | `addr_state` | The state provided by the borrower in the application | 0.1563% |
| 23 | `mort_acc` | Number of mortgage accounts | 0.0770% |
| 24 | `num_actv_rev_tl` | Number of active revolving trades | 0.0767% |
| 25 | `verification_status` | Verification status of borrower's income | 0.0743% |
| 26 | `home_ownership` | Home ownership status of the borrower | 0.0554% |
| 27 | `application_type` | Individual or Joint application | 0.0144% |

---

## 5. Performance Comparison: Notebook vs. Production Script

Due to resolving the **data leakage** vulnerability present in the original notebook's preprocessing code, the production script displays slightly improved metric bounds:

* **Accuracy**: Increased from **87.75%** to **87.90%**.
* **False Negatives**: Reduced from **133** to **126** (the model successfully captured 7 more defaults on the test split).
* **Charged Off Recall**: Increased from **93.00%** to **93.71%**.
