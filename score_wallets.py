import pandas as pd
import numpy as np
import json
from datetime import datetime
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler
import argparse

def main(input_path, output_path):
    # Load data
    with open(input_path, "r") as f:
        data = json.load(f)

    # Normalize JSON
    df = pd.json_normalize(data)
    df = df.rename(columns={
        "userWallet": "wallet",
        "actionData.amount": "amount",
        "actionData.assetSymbol": "asset"
    })

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # Feature Engineering
    g = df.groupby("wallet")
    features = pd.DataFrame({
        "tx_count": g.size(),
        "total_deposit": g.apply(lambda x: x.loc[x.action == "deposit", "amount"].sum()),
        "total_borrow": g.apply(lambda x: x.loc[x.action == "borrow", "amount"].sum()),
        "active_days": g.timestamp.apply(lambda s: s.dt.date.nunique()),
        "avg_time_between": g.timestamp.apply(lambda s: s.sort_values().diff().dt.total_seconds().mean()),
        "asset_diversity": g.asset.nunique(),
        "liquidations": g.apply(lambda x: (x.action == "liquidationcall").sum())
    })

    features["borrow_to_deposit"] = features["total_borrow"] / (features["total_deposit"] + 1e-6)
    features = features.reset_index().fillna(0)

    # Model
    num_cols = features.select_dtypes(include=np.number).columns
    iso = IsolationForest(n_estimators=300, contamination=0.1, random_state=42)
    iso.fit(features[num_cols])
    raw_score = iso.decision_function(features[num_cols])
    scaled = MinMaxScaler((0, 1000)).fit_transform(raw_score.reshape(-1, 1)).ravel()
    features["credit_score"] = scaled.round().astype(int)

    # Save
    features[["wallet", "credit_score"]].to_csv(output_path, index=False)
    print(f"[✓] Saved: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to user_transactions.json")
    parser.add_argument("--output", default="wallet_scores.csv", help="Path to save scored output")
    args = parser.parse_args()
    
    main(args.input, args.output)


