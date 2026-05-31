import pandas as pd

combined_pressure = pd.read_csv(
    "data/combined_pressure_by_borough.csv"
)

# Airbnb pressure levels
combined_pressure["airbnb_pressure_level"] = pd.qcut(
    combined_pressure["airbnb_pressure_score"],
    q=3,
    labels=["Low", "Medium", "High"]
)

# Housing pressure levels
combined_pressure["housing_pressure_level"] = pd.qcut(
    combined_pressure["housing_pressure_score"],
    q=3,
    labels=["Low", "Medium", "High"]
)

# Save to a new CSV
combined_pressure.to_csv("data/combined_pressure_by_borough.csv", index=False)