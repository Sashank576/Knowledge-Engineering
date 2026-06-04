import pandas as pd
import re
from rdflib import Graph, Namespace, RDF, RDFS, XSD, Literal, URIRef

# Load data
listing_df = pd.read_csv("data/class_Listing.csv")
host_df = pd.read_csv("data/class_Host.csv")
borough_df = pd.read_csv("data/class_Borough.csv")

# Load Airbnb and Housing Pressure file
all_scores_levels = pd.read_csv("data/new_combined_aggregate_scores.csv")

# Load the borough profile similarity file
borough_similarity = pd.read_csv("data/borough_profile_similarity.csv")

# Create graph
graph = Graph()
EX = Namespace("http://example.org/london-airbnb/")

graph.bind("ex", EX)
graph.bind("rdf", RDF)
graph.bind("rdfs", RDFS)
graph.bind("xsd", XSD)

def removeSpace(value):
    return str(value).replace(" ", "_").replace("/", "_")

# Classes
classes = [
    "Borough",
    "Listing",
    "Host",
    "RoomType",
    "HousingIndicator",
    "PressureIndicator",
    "TransportIndicator",
    "ProfileSimilarity"
]

for cls in classes:
    graph.add((EX[cls], RDF.type, RDFS.Class))

# Object properties
object_properties = {
    "isLocatedIn": ("Listing", "Borough"),
    "hasRoomType": ("Listing", "RoomType"),
    "hasListing": ("Host", "Listing"),
    "hasHousingIndicator": ("Borough", "HousingIndicator"),
    "hasPressureIndicator": ("Borough", "PressureIndicator"),
    "hasTransportIndicator": ("Borough", "TransportIndicator"),

    "hasSource": ("ProfileSimilarity", "Borough"),
    "hasTarget": ("ProfileSimilarity", "Borough"),
}

for prop, (domain, range_) in object_properties.items():
    graph.add((EX[prop], RDF.type, RDF.Property))
    graph.add((EX[prop], RDFS.domain, EX[domain]))
    graph.add((EX[prop], RDFS.range, EX[range_]))

# Datatype properties
datatype_properties = {
    # Listing
    "listingID": ("Listing", XSD.integer),
    "listingName": ("Listing", XSD.string),
    "latitude": ("Listing", XSD.float),
    "longitude": ("Listing", XSD.float),
    "priceNight": ("Listing", XSD.float),
    "availability": ("Listing", XSD.integer),
    "reviewsMonth": ("Listing", XSD.float),

    # Host
    "hostID": ("Host", XSD.integer),
    "hostListingCount": ("Host", XSD.integer),

    # Borough
    "boroughName": ("Borough", XSD.string),
    "populationEstimate": ("Borough", XSD.integer),
    "householdEstimate": ("Borough", XSD.integer),
    "populationDensity": ("Borough", XSD.float),
    "medianHousePrice": ("Borough", XSD.float),
    "newHomes": ("Borough", XSD.float),
    "medianIncome": ("Borough", XSD.float),
    "ownedRatio": ("Borough", XSD.float),
    "rentedAssociationRatio": ("Borough", XSD.float),
    "rentedPrivateRatio": ("Borough", XSD.float),

    # RoomType
    "roomTypeName": ("RoomType", XSD.string),

    # Indicators
    "airbnbPressureScore": ("PressureIndicator", XSD.float),
    "airbnbPressureLevel": ("PressureIndicator", XSD.string),
    "housingPressureScore": ("HousingIndicator", XSD.float),
    "housingPressureLevel": ("HousingIndicator", XSD.string),
    "transportPressureScore": ("TransportIndicator", XSD.float),
    "transportPressureLevel": ("TransportIndicator", XSD.string),

    # Profile similarity
    "similarityValue": ("ProfileSimilarity", XSD.float)
}

for prop, (domain, range_) in datatype_properties.items():
    graph.add((EX[prop], RDF.type, RDF.Property))
    graph.add((EX[prop], RDFS.domain, EX[domain]))
    graph.add((EX[prop], RDFS.range, range_))

# Column mappings for new class files
listing_literal_mapping = {
    "listingID": (EX.listingID, XSD.integer),
    "listingName": (EX.listingName, XSD.string),
    "latitude": (EX.latitude, XSD.float),
    "longitude": (EX.longitude, XSD.float),
    "priceNight": (EX.priceNight, XSD.float),
    "availability": (EX.availability, XSD.integer),
    "reviewsMonth": (EX.reviewsMonth, XSD.float),
}

host_literal_mapping = {
    "hostID": (EX.hostID, XSD.integer),
    "hostListingCount": (EX.hostListingCount, XSD.integer),
}

borough_literal_mapping = {
    "populationEstimate": (EX.populationEstimate, XSD.integer),
    "householdEstimate": (EX.householdEstimate, XSD.integer),
    "populationDensity": (EX.populationDensity, XSD.float),
    "medianHousePrice": (EX.medianHousePrice, XSD.float),
    "newHomes": (EX.newHomes, XSD.float),
    "medianIncome": (EX.medianIncome, XSD.float),
    "ownedRatio": (EX.ownedRatio, XSD.float),
    "rentedAssociationRatio": (EX.rentedAssociationRatio, XSD.float),
    "rentedPrivateRatio": (EX.rentedPrivateRatio, XSD.float),
}

# Convert class_Listing
for _, row in listing_df.iterrows():
    listing = EX[f"listing/{row['listingID']}"]
    borough = EX[f"borough/{removeSpace(row['borough'])}"]
    room_type = EX[f"roomType/{removeSpace(row['roomType'])}"]

    graph.add((listing, RDF.type, EX.Listing))
    graph.add((borough, RDF.type, EX.Borough))
    graph.add((room_type, RDF.type, EX.RoomType))

    graph.add((listing, EX.isLocatedIn, borough))
    graph.add((listing, EX.hasRoomType, room_type))

    graph.add((borough, EX.boroughName, Literal(row["borough"], datatype=XSD.string)))
    graph.add((room_type, EX.roomTypeName, Literal(row["roomType"], datatype=XSD.string)))

    for csv_col, (rdf_prop, datatype) in listing_literal_mapping.items():
        if csv_col in listing_df.columns and pd.notna(row[csv_col]):
            graph.add((listing, rdf_prop, Literal(row[csv_col], datatype=datatype)))

# Convert class_Host
for _, row in host_df.iterrows():

    host = EX[f"host/{row['hostID']}"]
    listing = EX[f"listing/{row['listingID']}"]

    graph.add((host, RDF.type, EX.Host))
    graph.add((listing, RDF.type, EX.Listing))
    graph.add((host, EX.hasListing, listing))

    for csv_col, (rdf_prop, datatype) in host_literal_mapping.items():
        if csv_col in host_df.columns and pd.notna(row[csv_col]):
            graph.add((host, rdf_prop, Literal(row[csv_col], datatype=datatype)))

# Convert class_Borough
for _, row in borough_df.iterrows():

    borough = EX[f"borough/{removeSpace(row['borough'])}"]

    graph.add((borough, RDF.type, EX.Borough))
    graph.add((borough, EX.boroughName, Literal(row["borough"], datatype=XSD.string)))

    for csv_col, (rdf_prop, datatype) in borough_literal_mapping.items():
        if csv_col in borough_df.columns and pd.notna(row[csv_col]):
            graph.add((borough, rdf_prop, Literal(row[csv_col], datatype=datatype)))

# Add pressure indicators from score/level indicator file
for _, row in all_scores_levels.iterrows():
    borough = EX[f"borough/{removeSpace(row['borough'])}"]
    pressure_indicator = EX[f"pressureIndicator/{removeSpace(row['borough'])}"]
    housing_indicator = EX[f"housingIndicator/{removeSpace(row['borough'])}"]
    transport_indicator = EX[f"transportIndicator/{removeSpace(row['borough'])}"]

    graph.add((borough, RDF.type, EX.Borough))

    graph.add((pressure_indicator, RDF.type, EX.PressureIndicator))
    graph.add((housing_indicator, RDF.type, EX.HousingIndicator))
    graph.add((transport_indicator, RDF.type, EX.TransportIndicator))

    graph.add((borough, EX.hasPressureIndicator, pressure_indicator))
    graph.add((borough, EX.hasHousingIndicator, housing_indicator))
    graph.add((borough, EX.hasTransportIndicator, transport_indicator))

    if "airbnb_pressure_score" in all_scores_levels.columns:
        graph.add((pressure_indicator, EX.airbnbPressureScore,
                   Literal(row["airbnb_pressure_score"], datatype=XSD.float)))

    if "airbnb_pressure_level" in all_scores_levels.columns:
        graph.add((pressure_indicator, EX.airbnbPressureLevel,
                   Literal(row["airbnb_pressure_level"], datatype=XSD.string)))

    if "housing_pressure_score" in all_scores_levels.columns:
        graph.add((housing_indicator, EX.housingPressureScore,
                   Literal(row["housing_pressure_score"], datatype=XSD.float)))

    if "housing_pressure_level" in all_scores_levels.columns:
        graph.add((housing_indicator, EX.housingPressureLevel,
                   Literal(row["housing_pressure_level"], datatype=XSD.string)))

    if "transport_pressure_score" in all_scores_levels.columns:
        graph.add((transport_indicator, EX.transportPressureScore,
                Literal(row["transport_pressure_score"], datatype=XSD.float)))

    if "transport_pressure_level" in all_scores_levels.columns:
        graph.add((transport_indicator, EX.transportPressureLevel,
                Literal(row["transport_pressure_level"], datatype=XSD.string)))

# Add borough profile similarity scores
for _, row in borough_similarity.iterrows():
    b1 = EX[f"borough/{removeSpace(row['source'])}"]
    b2 = EX[f"borough/{removeSpace(row['target'])}"]

    similarity_relation = EX[
        f"similarity/{removeSpace(row['source'])}_to_{removeSpace(row['target'])}"
    ]

    graph.add((similarity_relation, RDF.type, EX.ProfileSimilarity))
    graph.add((similarity_relation, EX.hasSource, b1))
    graph.add((similarity_relation, EX.hasTarget, b2))
    graph.add((similarity_relation, EX.similarityValue,
               Literal(float(row["similarity"]), datatype=XSD.float)))

# Save RDF file (We can save other formats too if needed I think)
graph.serialize(destination="london_airbnb_kg.ttl", format="turtle")

print("RDF graph created successfully.")
print("Total triples:", len(graph))
print("Saved file:")
print("london_airbnb_kg.ttl")

# SPARQL test with simple query
query = """
PREFIX ex: <http://example.org/london-airbnb/>

SELECT ?borough ?indicator
WHERE {
    ?borough ex:hasPressureIndicator ?indicator .
}
LIMIT 10
"""

for result in graph.query(query):
    print(result)