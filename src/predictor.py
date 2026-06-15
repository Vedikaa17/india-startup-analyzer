import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

# ============================================
# FUNCTION 1: Load Real Data
# ============================================
def load_real_data():
    csv_path = "data/inc42_articles.csv"

    if not os.path.exists(csv_path):
        print("❌ No data found! Run data_collector.py first!")
        return None

    df = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df)} real articles!")
    return df

# ============================================
# FUNCTION 2: Create Historical Data
# (Simulated 2023-2025 data for better predictions)
# ============================================
def create_historical_data():
    print("\n📚 Creating historical data (2023-2025)...")

    # Real sector trends in India (based on actual market knowledge)
    historical = {
        "date": [
            # 2023 data
            "2023-01-15", "2023-01-28", "2023-02-10",
            "2023-02-25", "2023-03-08", "2023-03-22",
            "2023-04-05", "2023-04-19", "2023-05-03",
            "2023-05-17", "2023-06-01", "2023-06-15",
            "2023-07-10", "2023-07-24", "2023-08-07",
            "2023-08-21", "2023-09-04", "2023-09-18",
            "2023-10-02", "2023-10-16", "2023-11-06",
            "2023-11-20", "2023-12-04", "2023-12-18",
            # 2024 data
            "2024-01-10", "2024-01-24", "2024-02-07",
            "2024-02-21", "2024-03-06", "2024-03-20",
            "2024-04-03", "2024-04-17", "2024-05-01",
            "2024-05-15", "2024-06-05", "2024-06-19",
            "2024-07-03", "2024-07-17", "2024-08-07",
            "2024-08-21", "2024-09-04", "2024-09-18",
            "2024-10-02", "2024-10-16", "2024-11-06",
            "2024-11-20", "2024-12-04", "2024-12-18",
            # 2025 data
            "2025-01-08", "2025-01-22", "2025-02-05",
            "2025-02-19", "2025-03-05", "2025-03-19",
            "2025-04-02", "2025-04-16", "2025-05-07",
            "2025-05-21", "2025-06-04", "2025-06-18",
            "2025-07-02", "2025-07-16", "2025-08-06",
            "2025-08-20", "2025-09-03", "2025-09-17",
            "2025-10-01", "2025-10-15", "2025-11-05",
            "2025-11-19", "2025-12-03", "2025-12-17",
        ],
        "sector": [
            # 2023 - Fintech dominated
            "Fintech", "Fintech", "Edtech",
            "Healthtech", "Fintech", "Ecommerce",
            "Fintech", "Edtech", "Healthtech",
            "Fintech", "EV", "Fintech",
            "Healthtech", "Fintech", "Ecommerce",
            "Fintech", "Edtech", "Healthtech",
            "Fintech", "EV", "Fintech",
            "Healthtech", "Fintech", "Ecommerce",
            # 2024 - AI started growing
            "Fintech", "AI", "Healthtech",
            "Fintech", "AI", "Ecommerce",
            "AI", "Fintech", "Healthtech",
            "AI", "EV", "Fintech",
            "AI", "Healthtech", "Fintech",
            "AI", "Deeptech", "Healthtech",
            "AI", "Fintech", "EV",
            "AI", "Deeptech", "Fintech",
            # 2025 - AI booming
            "AI", "AI", "Fintech",
            "AI", "Healthtech", "AI",
            "AI", "Deeptech", "AI",
            "Fintech", "AI", "EV",
            "AI", "Deeptech", "Healthtech",
            "AI", "Fintech", "AI",
            "AI", "Deeptech", "AI",
            "Healthtech", "AI", "Deeptech",
        ]
    }

    df = pd.DataFrame(historical)
    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = "Not mentioned"
    df["source"] = "Historical"
    print(f"✅ Created {len(df)} historical data points!")
    return df

# ============================================
# FUNCTION 3: Predict Future Trends
# ============================================
def predict_trends(real_df, historical_df):
    print("\n🔮 Predicting future trends...")

    # Combine real + historical data
    all_df = pd.concat([historical_df, real_df], ignore_index=True)

    # Count articles per sector
    sector_counts = all_df["sector"].value_counts()

    print("\n📊 Sector Distribution (Historical + Real):")
    print("-" * 40)
    for sector, count in sector_counts.items():
        bar = "█" * count
        print(f"{sector:<15} {bar} ({count})")

    # Simple Growth Rate Prediction
    # Compare 2024 vs 2025 vs 2026 data
    all_df["year"] = pd.to_datetime(all_df["date"] if "date" in all_df.columns 
                                    else all_df["scraped_date"]).dt.year

    print("\n📈 Year-wise Sector Trends:")
    print("-" * 40)

    sectors = ["AI", "Fintech", "Healthtech", "Deeptech", "EV"]
    yearly_data = {}

    for sector in sectors:
        sector_df = all_df[all_df["sector"] == sector]
        yearly_counts = sector_df["year"].value_counts().sort_index()
        yearly_data[sector] = yearly_counts
        print(f"\n{sector}:")
        for year, count in yearly_counts.items():
            bar = "█" * count
            print(f"  {year}: {bar} ({count})")

    return yearly_data, sector_counts

# ============================================
# FUNCTION 4: Generate Predictions Chart
# ============================================
def generate_prediction_chart(yearly_data):
    print("\n📊 Generating prediction charts...")

    # Predict 2026 and 2027 values
    # Using simple linear growth rate
    predictions = {}

    for sector, yearly_counts in yearly_data.items():
        years = list(yearly_counts.index)
        counts = list(yearly_counts.values)

        if len(counts) >= 2:
            # Calculate average growth rate
            growth_rate = (counts[-1] - counts[0]) / len(counts)
            
            # Predict next 2 years
            pred_2026 = max(0, counts[-1] + growth_rate)
            pred_2027 = max(0, pred_2026 + growth_rate)

            predictions[sector] = {
                "historical": dict(zip(years, counts)),
                "2026": round(pred_2026),
                "2027": round(pred_2027)
            }

    # Print predictions
    print("\n🔮 PREDICTIONS FOR 2026-2027:")
    print("=" * 45)
    for sector, pred in predictions.items():
        print(f"\n{sector}:")
        print(f"  2026 prediction: {pred['2026']} funding deals")
        print(f"  2027 prediction: {pred['2027']} funding deals")

    # Plot predictions
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Chart 1: 2026 Predictions
    sectors_list = list(predictions.keys())
    pred_2026 = [predictions[s]["2026"] for s in sectors_list]
    pred_2027 = [predictions[s]["2027"] for s in sectors_list]

    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6"]

    bars1 = axes[0].bar(sectors_list, pred_2026,
                        color=colors, edgecolor="white", linewidth=1.5)
    for bar, val in zip(bars1, pred_2026):
        axes[0].text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() + 0.1,
                    str(val),
                    ha="center", fontweight="bold", fontsize=11)

    axes[0].set_title("Predicted Funding Deals — 2026",
                      fontsize=14, fontweight="bold", pad=15)
    axes[0].set_xlabel("Sector", fontsize=12)
    axes[0].set_ylabel("Predicted Deals", fontsize=12)
    axes[0].tick_params(axis="x", rotation=30)

    # Chart 2: 2027 Predictions
    bars2 = axes[1].bar(sectors_list, pred_2027,
                        color=colors, edgecolor="white", linewidth=1.5)
    for bar, val in zip(bars2, pred_2027):
        axes[1].text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() + 0.1,
                    str(val),
                    ha="center", fontweight="bold", fontsize=11)

    axes[1].set_title("Predicted Funding Deals — 2027",
                      fontsize=14, fontweight="bold", pad=15)
    axes[1].set_xlabel("Sector", fontsize=12)
    axes[1].set_ylabel("Predicted Deals", fontsize=12)
    axes[1].tick_params(axis="x", rotation=30)

    plt.suptitle("India Startup Funding — Future Predictions",
                 fontsize=16, fontweight="bold", y=1.02)
    plt.tight_layout()

    os.makedirs("assets", exist_ok=True)
    plt.savefig("assets/predictions.png", dpi=150, bbox_inches="tight")
    print("\n✅ Prediction chart saved: assets/predictions.png")

    return predictions

# ============================================
# MAIN FUNCTION
# ============================================
def run_predictions():
    print("=" * 50)
    print("   INDIA STARTUP FUNDING PREDICTOR")
    print("=" * 50)

    # Load data
    real_df = load_real_data()
    if real_df is None:
        return

    # Fix column name
    if "scraped_date" in real_df.columns:
        real_df["date"] = pd.to_datetime(real_df["scraped_date"])

    # Create historical data
    historical_df = create_historical_data()

    # Predict trends
    yearly_data, sector_counts = predict_trends(real_df, historical_df)

    # Generate charts
    predictions = generate_prediction_chart(yearly_data)

    print("\n" + "=" * 50)
    print("✅ Prediction Complete!")
    print("   Check assets/predictions.png!")
    print("=" * 50)

if __name__ == "__main__":
    run_predictions()