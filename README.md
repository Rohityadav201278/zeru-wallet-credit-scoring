# zeru-wallet-credit-scoring

This project builds a robust machine learning pipeline to assign **credit scores (0–1000)** to DeFi wallets based on their **historical transaction behavior** on the Aave V2 protocol (Polygon network).

---

##  Problem Statement

Given 100K+ transaction records across various actions (deposit, borrow, repay, redeem, liquidationcall), score each wallet on a 0–1000 scale:

- 🔼 High score → responsible & reliable wallet
- 🔽 Low score → risky, bot-like, or exploitative behavior

---

##  Method Chosen

Since the dataset lacks labeled outcomes (i.e., we don’t know which wallets defaulted), we use an **unsupervised anomaly detection approach**:

###  `IsolationForest`
- Works well with mixed behaviors and numeric features
- Identifies outlier behavior based on feature distributions
- Outputs a score which we **rescale to 0–1000**

This helps detect wallets with unusual patterns (e.g., repeated borrowing with no deposit, very short transaction intervals, or frequent liquidations).

---

##  Architecture Overview


Raw JSON
   │
   ▼
[1] Data Parsing & Normalization
   │
   ▼
[2] Feature Engineering (per wallet)
   │
   ▼
[3] Unsupervised Scoring (IsolationForest)
   │
   ▼
[4] Score Scaling (0–1000)
   │
   ▼
[5] Save as CSV (wallet_scores.csv)
