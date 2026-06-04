import pandas as pd

# -------------------------------------------------------------
# Prepare the original london borough (demographics) dataset
# -------------------------------------------------------------
# Load the CSV
df = pd.read_csv("data/demographics.csv")

# Check shape (rows, columns)
print(df.shape)

# Select only certain columns
demographics_df = df[
    [
        "Area name",
        "GLA Population Estimate 2016",
        "GLA Household Estimate 2016",
        "Population density (per hectare) 2016",
        "Modelled Household median income estimates 2012/13",
        "Median House Price, 2014",
        "New Homes (net) 2014/15 (provisional)",
        "Homes Owned outright, (2014) %",
        "Being bought with mortgage or loan, (2014) %",
        "Rented from Local Authority or Housing Association, (2014) %",
        "Rented from Private landlord, (2014) %",
        "Average Public Transport Accessibility score, 2014",
        "Net internal migration (2014)",
        "Net international migration (2014)",
        "% of adults who cycle at least once per month, 2013/14",
        "Number of cars per household, (2011 Census)"
    ]
]

# Rename columns
demographics_df = demographics_df.rename(columns={
    "Area name": "borough",
    "GLA Population Estimate 2016": "populationEstimate",
    "GLA Household Estimate 2016": "householdEstimate",
    "Population density (per hectare) 2016": "populationDensity",
    "Modelled Household median income estimates 2012/13": "medianIncome",
    "Median House Price, 2014": "medianHousePrice",
    "New Homes (net) 2014/15 (provisional)": "newHomes",
    "Homes Owned outright, (2014) %": "ownedRatio1",
    "Being bought with mortgage or loan, (2014) %": "ownedRatio2",
    "Rented from Local Authority or Housing Association, (2014) %": "rentedAssociationRatio",
    "Rented from Private landlord, (2014) %": "rentedPrivateRatio",
    "Average Public Transport Accessibility score, 2014": "transportScore",
    "Net internal migration (2014)": "netInternalMigration",
    "Net international migration (2014)": "netInternationalMigration",
    "% of adults who cycle at least once per month, 2013/14": "cyclePerMonth",
    "Number of cars per household, (2011 Census)": "carsPerHousehold"
})

# Remove rows with missing borough names or household estimates
demographics_df = demographics_df.dropna(subset=["borough", "householdEstimate"])

# Ratio of non-rented homes
demographics_df["ownedRatio"] = (
    demographics_df["ownedRatio1"] + demographics_df["ownedRatio2"]
)
demographics_df = demographics_df.drop(
    columns=["ownedRatio1", "ownedRatio2"]
)

def clean_numeric(series):
    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("£", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip(),
        errors="coerce"
    )

numeric_cols = [
    "populationEstimate",
    "householdEstimate",
    "populationDensity",
    "medianIncome",
    "medianHousePrice",
    "newHomes",
    "ownedRatio",
    "rentedAssociationRatio",
    "rentedPrivateRatio",
    "transportScore",
    "netInternalMigration",
    "netInternationalMigration",
    "cyclePerMonth",
    "carsPerHousehold"
]

for col in numeric_cols:
    demographics_df[col] = clean_numeric(demographics_df[col])

# Impute missing value for the percentage of privately rented homes for the City of London using the median
rent_share_median = demographics_df["rentedPrivateRatio"].median()
demographics_df.loc[
    demographics_df["borough"] == "City of London",
    "rentedPrivateRatio"
] = rent_share_median

# Impute missing value for the percentage of cycling adults for the City of London using the median
demographics_df.loc[
    demographics_df["borough"] == "City of London",
    "cyclePerMonth"
] = demographics_df["cyclePerMonth"].median()

# Net migration
# positive migration → more housing demand
# negative migration → less housing demand
demographics_df["netMigration"] = (
    demographics_df["netInternalMigration"]
    +
    demographics_df["netInternationalMigration"]
)
demographics_df = demographics_df.drop(
    columns=["netInternalMigration", "netInternationalMigration"]
)

# ---------------------------------------------------
# Prepare the original Airbnb dataset
# ---------------------------------------------------
# Load the CSV
df = pd.read_csv("data/listings.csv")

# Check shape (rows, columns)
print(df.shape)

# Select only certain columns
airbnb_df = df[
    [
        "id",
        "name",
        "host_id",
        "host_name",
        "neighbourhood",
        "latitude",
        "longitude",
        "room_type",
        "price",
        "minimum_nights",
        "number_of_reviews",
        "last_review",
        "reviews_per_month",
        "calculated_host_listings_count",
        "availability_365"
    ]
]

# Rename columns
airbnb_df = airbnb_df.rename(columns={
    "id": "listingID",
    "name": "listingName",
    "host_id": "hostID",
    "host_name": "hostName",
    "neighbourhood": "borough",
    "room_type": "roomType",
    "price": "priceNight",
    "minimum_nights": "minNights",
    "number_of_reviews": "reviewCount",
    "last_review": "lastReviewDate",
    "reviews_per_month": "reviewsMonth",
    "calculated_host_listings_count": "hostListingCount",
    "availability_365": "availability"
})

# Convert date column
airbnb_df["lastReviewDate"] = pd.to_datetime(
    airbnb_df["lastReviewDate"],
    errors="coerce"
)

# If NaN reviews, take it as 0
airbnb_df["reviewsMonth"] = airbnb_df["reviewsMonth"].fillna(0)
airbnb_df["reviewCount"] = airbnb_df["reviewCount"].fillna(0)

# Split into Host class and Listing class
host_df = airbnb_df[["hostID", "hostName", "listingID", "hostListingCount"]]
host_df.to_csv("data/class_Host.csv", index=False)

listing_df = airbnb_df.drop(columns=["hostName", "hostListingCount", "hostID"])
listing_df.to_csv("data/class_Listing.csv", index=False)

# --------------------------------------------------------------
# Aggregate the listing-level Airbnb data to the borough level
# --------------------------------------------------------------
# Borough-level dataframe
borough_airbnb = pd.DataFrame({
    "borough": sorted(airbnb_df["borough"].unique())
})

# 1. Total number of Airbnb listings per borough
borough_airbnb["listingCount"] = (
    airbnb_df.groupby("borough")
    .size()
    .values
)

# 2. Room type share per borough
borough_airbnb["entireHomeShare"] = (
    airbnb_df.groupby("borough")["roomType"]
    .apply(lambda x: (x == "Entire home/apt").mean())
    .values
)

# 3. Multi-hosts (professional hosts) per borough
borough_airbnb["multiHostShare"] = (
    airbnb_df.groupby("borough")["hostListingCount"]
    .apply(lambda x: (x > 3).mean())
    .values
)

# 4. Cross-borough hosts (alternative professional hosts)
borough_airbnb["multiHostShare2"] = (
    airbnb_df.assign(
        multiBoroughHost=airbnb_df.groupby("hostID")["borough"].transform("nunique").gt(1)
    )
    .groupby("borough")["multiBoroughHost"]
    .mean()
    .values
)

# 5. Active listings: The dataset was created in the middle of 2019,
# so consider a listing active if there was a review in 2019.
borough_airbnb["activeListingsShare"] = (
    airbnb_df.assign(
        active=airbnb_df["lastReviewDate"].notna()
        & (airbnb_df["lastReviewDate"].dt.year == 2019)
    )
    .groupby("borough")["active"]
    .mean()
    .values
)

# 6. Average reviews per month per borough as an indicator for demand
borough_airbnb["avgReviewsPerMonth"] = (
    airbnb_df.groupby("borough")["reviewsMonth"]
    .mean()
    .values
)

# 7. Average availability
borough_airbnb["avgAvailability"] = (
    airbnb_df.groupby("borough")["availability"]
    .mean()
    .values
)

# Result of data aggregation from listing-level to borough-level
print(borough_airbnb)

# -----------------------------------------------------------------
# Merge original demographics dataset with aggregated Airbnb data
# -----------------------------------------------------------------
# Merge the aggregated data and the original demographics data
borough_merged = borough_airbnb.merge(
    demographics_df,
    on="borough",
    how="left"
)

# Number of Airbnb listings per 1000 households
borough_merged["airbnbPerHousehold"] = (
    borough_merged["listingCount"] /
    borough_merged["householdEstimate"]
) * 1000

# Number of Airbnb listings per 1000 people
borough_merged["airbnbPerCapita"] = (
    borough_merged["listingCount"] /
    borough_merged["populationEstimate"]
)

# Affordability indicator
borough_merged["priceIncomeRatio"] = (
    borough_merged["medianHousePrice"]
    /
    borough_merged["medianIncome"]
)

borough_merged.to_csv("data/class_Borough.csv", index=False)
