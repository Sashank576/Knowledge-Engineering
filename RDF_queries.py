import pandas as pd
from rdflib import Graph
import time

def shorten_uri(uri):
    return str(uri).split("/")[-1].replace("_", " ")

#Runs a SPARQL query and stores the result as a pandas DataFrame. Also shortens URI columns if wanted
def query_to_dataframe(graph, query, shorten_columns=None):
    results = graph.query(query)

    rows = []
    for row in results:
        row_dict = {}

        for var, value in zip(results.vars, row):
            var_name = str(var)

            if value is None:
                row_dict[var_name] = None
            elif shorten_columns and var_name in shorten_columns:
                row_dict[var_name] = shorten_uri(value)
            else:
                row_dict[var_name] = value.toPython()

        rows.append(row_dict)

    return pd.DataFrame(rows)

# Load RDF graph
start = time.time()
graph = Graph()
graph.parse("london_airbnb_kg.ttl", format="turtle")

end = time.time()
print("Triples loaded:", len(graph))
print(f"It took {end-start} seconds to load the RDF graph")

# Airbnb, housing and transport indicator scores and level for every borough
start = time.time()
get_all_boroughs = """
PREFIX ex: <http://example.org/london-airbnb/>

SELECT
    ?borough
    ?airbnb_pressure_indicator
    ?housing_indicator
    ?transportation_indicator

    ?airbnb_score
    ?housing_score
    ?transport_score
WHERE {
    ?borough ex:hasPressureIndicator ?pressureIndicator .
    ?pressureIndicator ex:airbnbPressureLevel ?airbnb_pressure_indicator ;
                       ex:airbnbPressureScore ?airbnb_score .

    ?borough ex:hasHousingIndicator ?housingIndicator .
    ?housingIndicator ex:housingPressureLevel ?housing_indicator ;
                      ex:housingPressureScore ?housing_score .

    ?borough ex:hasTransportIndicator ?transportIndicator .
    ?transportIndicator ex:transportPressureLevel ?transportation_indicator ;
                        ex:transportPressureScore ?transport_score .
}
"""
all_boroughs_indicators_df = query_to_dataframe(
    graph,
    get_all_boroughs,
    shorten_columns=["borough"]
)
all_boroughs_indicators_df.to_csv("visualization/assets/all_borough_indicators.csv", index=False)
end = time.time()
print(f"It took {end-start} seconds to get all indicator levels and scores")

# Get all individual Airbnb listings
start = time.time()
get_all_listings = """
PREFIX ex: <http://example.org/london-airbnb/>

SELECT
    ?name
    ?borough
    ?room_type
    ?lat
    ?lon
    ?price
WHERE {
    ?listing ex:listingName ?name ;
             ex:isLocatedIn ?borough ;
             ex:hasRoomType ?roomType ;
             ex:latitude ?lat ;
             ex:longitude ?lon ;
             ex:priceNight ?price .

     ?roomType ex:roomTypeName ?room_type .
}
"""
all_listings_df = query_to_dataframe(
    graph,
    get_all_listings,
    shorten_columns=["listing", "borough"]
)
all_listings_df.to_csv("visualization/assets/all_listings.csv", index=False)
end = time.time()
print(f"It took {end-start} seconds to get all listings")

# Research Question 1
# Query 1: Find the boroughs with "High" airbnb pressure level and retrieve some of the borough-level housing or demographic indicators.
# Which indicators we should use for the "co-occurrence" analysis I don't fully know yet.
start = time.time()
rq1_query1 = """
PREFIX ex: <http://example.org/london-airbnb/>

SELECT
    ?borough
    ?income
    ?housePrice
    ?popDensity
WHERE {
    ?borough ex:hasPressureIndicator ?pressure .

    ?pressure ex:airbnbPressureLevel ?level ;
              ex:airbnbPressureScore ?score .
    FILTER(str(?level) = "High")

    OPTIONAL { ?borough ex:medianIncome ?income . }
    OPTIONAL { ?borough ex:medianHousePrice ?housePrice . }
    OPTIONAL { ?borough ex:populationDensity ?popDensity . }
}
ORDER BY DESC(?score)
"""
rq1_query1_df = query_to_dataframe(
    graph,
    rq1_query1,
    shorten_columns=["borough"]
)

# Query 2: Compare the averages of some of the indicators between High pressure level boroughs and Low, Medium boroughs.
# The idea is to use these with some visualization (normal bar chart maybe?)
# to compare boroughs with different Airbnb pressure levels on their average borough-level housing or demographic indicators.
rq1_query2 = """
PREFIX ex: <http://example.org/london-airbnb/>

SELECT
    ?level
    (COUNT(?borough) AS ?boroughCount)
    (AVG(?score) AS ?avgPressureScore)
    (AVG(?income) AS ?avgIncome)
    (AVG(?housePrice) AS ?avgHousePrice)
    (AVG(?popDensity) AS ?avgPopDensity)
WHERE {
    ?borough ex:hasPressureIndicator ?pressure .

    ?pressure ex:airbnbPressureLevel ?level ;
              ex:airbnbPressureScore ?score .

    OPTIONAL { ?borough ex:medianIncome ?income . }
    OPTIONAL { ?borough ex:medianHousePrice ?housePrice . }
    OPTIONAL { ?borough ex:populationDensity ?popDensity . }
}
GROUP BY ?level
ORDER BY ?level
"""
rq1_query2_df = query_to_dataframe(graph, rq1_query2)

rq1_query1_df.to_csv("visualization/assets/rq1_high_airbnb_pressure_boroughs.csv", index=False)
rq1_query2_df.to_csv("visualization/assets/rq1_pressure_level_averages.csv", index=False)
end = time.time()
print(f"It took {end-start} seconds to run the queries for RQ1")

# Research Question 2
# Query 1: Examples of entire-home Airbnb listings in high Airbnb and housing pressure boroughs.
# Direct answer to RQ2 (with limit so that we don't print all thousands of them)
start = time.time()
rq2_query1 = """
PREFIX ex: <http://example.org/london-airbnb/>

SELECT
    ?listing
    ?listingName
    ?borough
    ?airbnbScore
    ?housingScore
    ?latitude
    ?longitude
    ?price
    ?reviews
WHERE {
    ?listing ex:isLocatedIn ?borough ;
             ex:listingName ?listingName ;
             ex:hasRoomType ?roomType ;
             ex:latitude ?latitude ;
             ex:longitude ?longitude ;
             ex:priceNight ?price ;
             ex:reviewsMonth ?reviews .

    ?roomType ex:roomTypeName ?roomName .
    FILTER(str(?roomName) = "Entire home/apt")

    ?borough ex:hasPressureIndicator ?pressure ;
             ex:hasHousingIndicator ?housing .

    ?pressure ex:airbnbPressureLevel ?airbnbLevel ;
              ex:airbnbPressureScore ?airbnbScore .
    FILTER(str(?airbnbLevel) = "High")

    ?housing ex:housingPressureLevel ?housingLevel ;
             ex:housingPressureScore ?housingScore .
    FILTER(str(?housingLevel) = "High")
}
"""
rq2_query1_df = query_to_dataframe(
    graph,
    rq2_query1,
    shorten_columns=["listing", "borough"]
)

# Query 2: Count the number of such listings per high pressure borough
# For further (bar chart) visualization alongside the London map dot plot idea.
rq2_query2 = """
PREFIX ex: <http://example.org/london-airbnb/>

SELECT
    ?borough
    (COUNT(?listing) AS ?listingCount)
WHERE {
    ?listing ex:isLocatedIn ?borough ;
             ex:hasRoomType ?roomType .

    ?roomType ex:roomTypeName ?roomName .
    FILTER(str(?roomName) = "Entire home/apt")

    ?borough ex:hasPressureIndicator ?pressure ;
             ex:hasHousingIndicator ?housing .

    ?pressure ex:airbnbPressureLevel ?airbnbLevel .
    FILTER(str(?airbnbLevel) = "High")

    ?housing ex:housingPressureLevel ?housingLevel .
    FILTER(str(?housingLevel) = "High")
}
GROUP BY ?borough
ORDER BY DESC(?listingCount)
"""
rq2_query2_df = query_to_dataframe(
    graph,
    rq2_query2,
    shorten_columns=["borough"]
)

rq2_query1_df.to_csv("visualization/assets/rq2_entire_home_examples.csv", index=False)
rq2_query2_df.to_csv("visualization/assets/rq2_entire_home_counts.csv", index=False)
end = time.time()
print(f"It took {end-start} seconds to run the queries for RQ2")

# Research Question 3
# Query 1: Hosts with listings in more than one borough (with at least one of them a high pressure one).
# NOTE: City of London does not have pressure profiles (we still have to decide whether to include this).
start = time.time()
rq3_query1 = """
PREFIX ex: <http://example.org/london-airbnb/>

SELECT
    ?host
    ?hostName
    ?hostListingCount
    (COUNT(DISTINCT ?borough) AS ?boroughCount)
        # List of the individual borough names
    (GROUP_CONCAT(DISTINCT STRAFTER(STR(?borough), "/borough/"); separator=", ") AS ?boroughs)
WHERE {
    ?host   ex:hasListing ?listing ;
            ex:hostName ?hostName ;
            ex:hostListingCount ?hostListingCount .

    ?listing ex:isLocatedIn ?borough .

    ?borough ex:hasPressureIndicator ?pressure .
    ?pressure ex:airbnbPressureLevel ?pressureLevel .

    FILTER(BOUND(?pressureLevel))
}
GROUP BY ?host

# At least one of the boroughs has a "High" Airbnb pressure
HAVING (
    COUNT(DISTINCT ?borough) > 1 &&
    SUM(IF(str(?pressureLevel) = "High", 1, 0)) > 0
)
ORDER BY DESC(?boroughCount)
"""
rq3_query1_df = query_to_dataframe(
    graph,
    rq3_query1,
    shorten_columns=["host"]
)

rq3_query1_df.to_csv("visualization/assets/rq3_multiborough_hosts.csv", index=False)
end = time.time()
print(f"It took {end-start} seconds to run the queries for RQ3")

# Research Question 4
# Query 1: Boroughs that fall into each profile based on Airbnb pressure, housing pressure and transport accessibility score.
# NOTE: Might be better to add the transport bands directly into the graphs.
start = time.time()
rq4_query1 = """
PREFIX ex: <http://example.org/london-airbnb/>

SELECT
    ?pressureLevel
    ?housingLevel
    ?transportLevel
    (COUNT(?borough) AS ?boroughCount)
        # List of the individual borough names
    (GROUP_CONCAT(DISTINCT STRAFTER(STR(?borough), "/borough/"); separator=", ") AS ?boroughs)
WHERE {
    ?borough ex:hasPressureIndicator ?pressure ;
             ex:hasHousingIndicator ?housing ;
             ex:hasTransportIndicator ?transport .

    ?pressure ex:airbnbPressureLevel ?pressureLevel .
    ?housing ex:housingPressureLevel ?housingLevel .
    ?transport ex:transportPressureLevel ?transportLevel .
}
GROUP BY ?pressureLevel ?housingLevel ?transportLevel
ORDER BY DESC(?boroughCount)
"""
rq4_query1_df = query_to_dataframe(graph, rq4_query1)

# Query 2: Borough profile similarity
rq4_query2 = """
PREFIX ex: <http://example.org/london-airbnb/>

SELECT ?from_borough ?to_borough ?similarity
WHERE {
    ?profile ex:hasSource ?from_borough ;
             ex:hasTarget ?to_borough ;
             ex:similarityValue ?similarity .

    # FILTER(?similarity > 0.8)
}
ORDER BY DESC(?similarity)
"""
rq4_query2_df = query_to_dataframe(
    graph,
    rq4_query2,
    shorten_columns=["from_borough", "to_borough"]
)

rq4_query1_df.to_csv("visualization/assets/rq4_pressure_profile_clusters.csv", index=False)
rq4_query2_df.to_csv("visualization/assets/rq4_similarity_pairs.csv", index=False)
end = time.time()
print(f"It took {end-start} seconds to run the queries for RQ4")
