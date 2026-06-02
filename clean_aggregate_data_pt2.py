import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA

# -------------------------------
# Airbnb pressure score/levels
# -------------------------------
borough_df = pd.read_csv("data/class_Borough.csv")

vars_for_pca = [
    "airbnbPerHousehold",
    "entireHomeShare",
    "avgAvailability",
    "multiHostShare"
]

# Remove boroughs with missing values
pca_data = borough_df.dropna(subset=vars_for_pca).copy()

# Standardize
scaler = StandardScaler()

X_scaled = scaler.fit_transform(
    pca_data[vars_for_pca]
)

# Run PCA: First principal component captures maximum variance
pca = PCA(n_components=1)
pca_scores = pca.fit_transform(X_scaled)

# Add raw PCA score
pca_data["airbnb_pressure_raw"] = pca_scores[:, 0]

# Inspect PCA weights
weights = pd.Series(
    pca.components_[0],
    index=vars_for_pca
)

print("PCA weights:")
print(weights)

print("\nExplained variance:")
print(pca.explained_variance_ratio_[0])

# Flip sign so higher score = higher pressure
if weights["airbnbPerHousehold"] < 0:
    pca_data["airbnb_pressure_raw"] *= -1

# Normalize to 0–1
minmax = MinMaxScaler()

pca_data["airbnb_pressure_score"] = (
    minmax.fit_transform(
        pca_data[["airbnb_pressure_raw"]]
    )
)

# Convert to categories
pca_data["airbnb_pressure_level"] = pd.qcut(
    pca_data["airbnb_pressure_score"],
    q=3,
    labels=["Low","Medium","High"]
)
print(pca_data[["borough", "airbnb_pressure_score", "airbnb_pressure_level"]])

# -------------------------------
# Housing pressure score/levels
# -------------------------------
housing_df = pd.read_csv("data/class_Borough.csv")

# Reverse housing supply
# More new homes -> lower pressure
# Fewer new homes -> higher pressure
housing_df["lowNewHomesPressure"] = -housing_df["newHomes"]

# Variables defining housing pressure
vars_for_pca = [
    "priceIncomeRatio",
    "populationDensity",
    "rentedPrivateRatio",
    "lowNewHomesPressure",
    "netMigration"
]

# Remove missing values
housing_pca = housing_df.dropna(
    subset=vars_for_pca
).copy()

# Standardize variables
scaler = StandardScaler()

X_scaled = scaler.fit_transform(
    housing_pca[vars_for_pca]
)

# PCA
pca = PCA(n_components=1)
housing_scores = pca.fit_transform(X_scaled)

# Add raw PCA score
housing_pca["housing_pressure_raw"] = (housing_scores[:,0])

# Inspect weights
weights = pd.Series(
    pca.components_[0],
    index=vars_for_pca
)

print("PCA weights:")
print(weights)

print("\nExplained variance:")
print(pca.explained_variance_ratio_[0])

# Flip sign if needed (ensure higher score = higher pressure)
if weights["priceIncomeRatio"] < 0:
    housing_pca["housing_pressure_raw"] *= -1

# Normalize to 0–1
minmax = MinMaxScaler()

housing_pca["housing_pressure_score"] = (
    minmax.fit_transform(
        housing_pca[["housing_pressure_raw"]]
    )
)

# Create levels
housing_pca["housing_pressure_level"] = pd.qcut(
    housing_pca["housing_pressure_score"],
    q=3,
    labels=["Low","Medium","High"]
)

print(housing_pca[["borough", "housing_pressure_score", "housing_pressure_level"]])
print()

# Merge the pressure scores and level
pressure = pd.merge(
    pca_data[
        [
            "borough",
            "airbnb_pressure_score"
        ]
    ],
    housing_pca[
        [
            "borough",
            "housing_pressure_score"
        ]
    ],
    on="borough"
)
print(pressure)

# -------------------------------
# Transport accessibility score
# -------------------------------
transport_df = pd.read_csv("data/class_Borough.csv")

# Reverse car ownership -> Higher car ownership = lower accessibility
transport_df["lowCarDependence"] = -transport_df["carsPerHousehold"]

# Variables defining transport accessiblity score
transport_vars = [
    "transportScore",
    "cyclePerMonth",
    "lowCarDependence"
]

# Remove missing values
transport_pca = transport_df.dropna(
    subset=transport_vars
).copy()

# Standardize variables
scaler = StandardScaler()

X_scaled = scaler.fit_transform(
    transport_pca[transport_vars]
)

# PCA
pca = PCA(n_components=1)
transport_scores = pca.fit_transform(X_scaled)

# Add raw PCA score
transport_pca["transport_raw"] = (transport_scores[:,0])

# Inspect weights
weights = pd.Series(
    pca.components_[0],
    index=transport_vars
)

print("PCA weights:")
print(weights)

print("\nExplained variance:")
print(pca.explained_variance_ratio_[0])

# Normalize to 0–1
minmax = MinMaxScaler()

transport_pca["transport_accessibility_score"] = (
    minmax.fit_transform(
        transport_pca[["transport_raw"]]
    )
)

print(transport_pca[["borough", "transport_accessibility_score"]])
print()

# Merge to pressure df
pressure = (
    pressure.merge(
        transport_pca[
            ["borough", "transport_accessibility_score"]
        ],
        on="borough",
        how="left"
    )
)
print(pressure)

# Airbnb pressure levels
pressure["airbnb_pressure_level"] = pd.qcut(
    pressure["airbnb_pressure_score"],
    q=3,
    labels=["Low", "Medium", "High"]
)

# Housing pressure levels
pressure["housing_pressure_level"] = pd.qcut(
    pressure["housing_pressure_score"],
    q=3,
    labels=["Low", "Medium", "High"]
)

# Transport accessibility levels
pressure["transport_accessibility_level"] = pd.qcut(
    pressure["transport_accessibility_score"],
    q=3,
    labels=["Low", "Medium", "High"]
)

pressure.to_csv("data/combined_aggregate_scores.csv", index=False)