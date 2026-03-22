import pandas as pd

# ============================================================
# STEP 1: LOAD THE DATA
# ============================================================
# Update this path to match where your file is saved
file_path = r"C:\Users\danor\OneDrive\Desktop\PyCharm_CIS3260\Project1\Data Analytics Project\online_retail_II.csv"

print("Loading data... this may take a moment due to file size.")
df = pd.read_csv(file_path, encoding="latin-1")
print(f"Data loaded. Shape: {df.shape}")
print(df.head())
print(f"Data loaded. Shape: {df.shape}")
print(df.head())

# ============================================================
# STEP 2: EXPLORE THE DATA
# ============================================================
print("\n--- Column Names ---")
print(df.columns.tolist())

print("\n--- Data Types ---")
print(df.dtypes)

print("\n--- Missing Values ---")
print(df.isnull().sum())

# ============================================================
# STEP 3: CLEAN THE DATA
# ============================================================
print("\nCleaning data...")

# Drop rows where Customer ID is missing
df = df.dropna(subset=["Customer ID"])

# Remove duplicate rows
df = df.drop_duplicates()

# Remove canceled orders (Invoice numbers that start with 'C')
df = df[~df["Invoice"].astype(str).str.startswith("C")]

# Remove rows with negative or zero quantity and price
df = df[df["Quantity"] > 0]
df = df[df["Price"] > 0]

# Create a TotalPrice column
df["TotalPrice"] = df["Quantity"] * df["Price"]

# Convert InvoiceDate to datetime
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

print(f"Data cleaned. Shape after cleaning: {df.shape}")
print(f"Unique customers: {df['Customer ID'].nunique()}")
print(f"Total transactions: {df['Invoice'].nunique()}")

# ============================================================
# STEP 4: BUILD RFM TABLE
# ============================================================
print("\nBuilding RFM table...")

# Set reference date as one day after the last transaction
reference_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

rfm = df.groupby("Customer ID").agg(
    Recency   = ("InvoiceDate", lambda x: (reference_date - x.max()).days),
    Frequency = ("Invoice", "nunique"),
    Monetary  = ("TotalPrice", "sum")
).reset_index()

print("\n--- RFM Table Sample ---")
print(rfm.head(10))
print(f"\nRFM Table Shape: {rfm.shape}")

# ============================================================
# STEP 5: SEGMENT CUSTOMERS INTO 5 GROUPS
# ============================================================
print("\nSegmenting customers...")

# Score each RFM metric 1-5 (5 = best)
# For Recency: lower days = better, so we reverse the ranking
rfm["Recency"] = pd.to_numeric(rfm["Recency"])
rfm["Frequency"] = pd.to_numeric(rfm["Frequency"])
rfm["Monetary"] = pd.to_numeric(rfm["Monetary"])

rfm["R_Score"] = pd.qcut(rfm["Recency"], q=5, labels=[5, 4, 3, 2, 1], duplicates="drop")
rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5], duplicates="drop")
rfm["M_Score"] = pd.qcut(rfm["Monetary"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5], duplicates="drop")

# Combine scores into overall RFM score
rfm["RFM_Score"] = (
    rfm["R_Score"].astype(int) +
    rfm["F_Score"].astype(int) +
    rfm["M_Score"].astype(int)
)

# Assign segment labels based on RFM score
def assign_segment(score):
    if score >= 13:
        return "Champions"
    elif score >= 10:
        return "Loyal Customers"
    elif score >= 7:
        return "At Risk"
    elif score >= 4:
        return "Needs Attention"
    else:
        return "Lost"

rfm["Segment"] = rfm["RFM_Score"].apply(assign_segment)

print("\n--- Segment Distribution ---")
print(rfm["Segment"].value_counts())

# ============================================================
# STEP 6: KEY INSIGHT - TOP 20% OF CUSTOMERS
# ============================================================
total_revenue = rfm["Monetary"].sum()
top_20_cutoff = rfm["Monetary"].quantile(0.80)
top_20_revenue = rfm[rfm["Monetary"] >= top_20_cutoff]["Monetary"].sum()
top_20_pct = (top_20_revenue / total_revenue) * 100

print(f"\n--- Key Insight ---")
print(f"Top 20% of customers drive {top_20_pct:.1f}% of total revenue")

# ============================================================
# STEP 7: EXPORT RESULTS
# ============================================================
output_path = r"C:\Users\danor\OneDrive\Desktop\PyCharm_CIS3260\Project1\Data Analytics Project\rfm_results.csv"
rfm.to_csv(output_path, index=False)
print(f"\nRFM results saved to: {output_path}")
print("\nDone! Your analysis is complete.")
