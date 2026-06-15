import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# ============================================
# SETUP - Good looking graphs!
# ============================================
plt.style.use("seaborn-v0_8")
sns.set_palette("husl")

# ============================================
# FUNCTION 1: Load Data
# ============================================
def load_data():
    csv_path = "data/inc42_articles.csv"

    if not os.path.exists(csv_path):
        print("❌ No data found! Run data_collector.py first!")
        return None

    df = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df)} articles from CSV!")
    print(f"   Columns: {list(df.columns)}")
    return df

# ============================================
# FUNCTION 2: Clean Data
# ============================================
def clean_data(df):
    print("\n🧹 Cleaning data...")

    # Remove rows where company is empty
    df = df.dropna(subset=["company", "sector"])

    # Fill empty amounts
    df["amount"] = df["amount"].fillna("Not mentioned")

    # Convert date to proper format
    df["scraped_date"] = pd.to_datetime(df["scraped_date"])

    # Add a column - has_amount (True/False)
    df["has_amount"] = df["amount"] != "Not mentioned"

    print(f"✅ Clean data ready! {len(df)} articles remaining!")
    return df

# ============================================
# FUNCTION 3: Sector Analysis
# ============================================
def analyze_sectors(df):
    print("\n📊 Analyzing sectors...")

    # Count articles per sector
    sector_counts = df["sector"].value_counts()

    print("\n🏆 Top Sectors by Article Count:")
    print("-" * 35)
    for sector, count in sector_counts.items():
        bar = "█" * count
        print(f"{sector:<15} {bar} ({count})")

    # Plot bar chart
    plt.figure(figsize=(12, 6))
    colors = sns.color_palette("husl", len(sector_counts))
    bars = plt.bar(sector_counts.index, 
                   sector_counts.values, 
                   color=colors,
                   edgecolor="white",
                   linewidth=1.5)

    # Add value labels on bars
    for bar, value in zip(bars, sector_counts.values):
        plt.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.1,
                str(value),
                ha="center",
                va="bottom",
                fontweight="bold",
                fontsize=11)

    plt.title("India Startup Funding — Sector Wise Distribution",
              fontsize=16, fontweight="bold", pad=20)
    plt.xlabel("Sector", fontsize=13)
    plt.ylabel("Number of Funding Articles", fontsize=13)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    # Save chart
    os.makedirs("assets", exist_ok=True)
    plt.savefig("assets/sector_analysis.png", dpi=150, bbox_inches="tight")
    print("✅ Chart saved: assets/sector_analysis.png")
    #plt.show()

    return sector_counts

# ============================================
# FUNCTION 4: Funding Amount Analysis
# ============================================
def analyze_funding_amounts(df):
    print("\n💰 Analyzing funding amounts...")

    # Separate articles with and without amounts
    with_amount    = df[df["has_amount"] == True]
    without_amount = df[df["has_amount"] == False]

    print(f"\n   Articles with amount    : {len(with_amount)}")
    print(f"   Articles without amount : {len(without_amount)}")

    # Pie chart
    plt.figure(figsize=(8, 8))
    sizes  = [len(with_amount), len(without_amount)]
    labels = ["Amount Mentioned", "Amount Not Mentioned"]
    colors = ["#2ecc71", "#e74c3c"]
    explode = (0.05, 0)

    plt.pie(sizes,
            labels=labels,
            colors=colors,
            explode=explode,
            autopct="%1.1f%%",
            startangle=90,
            textprops={"fontsize": 13})

    plt.title("Funding Articles — Amount Availability",
              fontsize=16, fontweight="bold", pad=20)
    plt.tight_layout()
    plt.savefig("assets/amount_analysis.png", dpi=150, bbox_inches="tight")
    print("✅ Chart saved: assets/amount_analysis.png")
    #plt.show()

# ============================================
# FUNCTION 5: Source Analysis
# ============================================
def analyze_sources(df):
    print("\n📰 Analyzing news sources...")

    source_counts = df["source"].value_counts().head(10)

    print("\n🏆 Top News Sources:")
    print("-" * 35)
    for source, count in source_counts.items():
        print(f"{source:<30} ({count} articles)")

    # Horizontal bar chart
    plt.figure(figsize=(12, 6))
    colors = sns.color_palette("coolwarm", len(source_counts))
    bars = plt.barh(source_counts.index,
                    source_counts.values,
                    color=colors,
                    edgecolor="white")

    for bar, value in zip(bars, source_counts.values):
        plt.text(bar.get_width() + 0.1,
                bar.get_y() + bar.get_height()/2,
                str(value),
                va="center",
                fontweight="bold")

    plt.title("Top News Sources for India Startup Funding",
              fontsize=16, fontweight="bold", pad=20)
    plt.xlabel("Number of Articles", fontsize=13)
    plt.ylabel("News Source", fontsize=13)
    plt.tight_layout()
    plt.savefig("assets/source_analysis.png", dpi=150, bbox_inches="tight")
    print("✅ Chart saved: assets/source_analysis.png")
    #plt.show()

# ============================================
# MAIN FUNCTION
# ============================================
def run_analysis():
    print("=" * 50)
    print("   INDIA STARTUP FUNDING ANALYZER")
    print("=" * 50)

    # Load data
    df = load_data()
    if df is None:
        return

    # Clean data
    df = clean_data(df)

    # Run all analysis
    analyze_sectors(df)
    analyze_funding_amounts(df)
    analyze_sources(df)

    print("\n" + "=" * 50)
    print("✅ Analysis Complete!")
    print("   Check assets/ folder for charts!")
    print("=" * 50)

if __name__ == "__main__":
    run_analysis()