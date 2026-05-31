from rdflib import Graph

def shorten_uri(uri):
    return str(uri).split("/")[-1].replace("_", " ")

# Load RDF graph
graph = Graph()
graph.parse("london_airbnb_kg.ttl", format="turtle")

print("Triples loaded:", len(graph))

# Research Question 1
# Query 1: Find the boroughs with "High" airbnb pressure level and retrieve some of the borough-level housing or demographic indicators.
# Which indicators we should use for the "co-occurrence" analysis I don't fully know yet.
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
results = graph.query(rq1_query1)

print("\nRQ1: High airbnb pressure borough with some indicators")
for borough, income, house_price, density in results:
    print(f"{shorten_uri(borough)}")
    print(f"  Median income        : {float(income)}")
    print(f"  Median house price   : {float(house_price)}")
    print(f"  Population density   : {float(density)}")
    print()

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
results = graph.query(rq1_query2)

print("RQ1: Averaged borough-level housing or demographic indicators grouped by pressure level")
for level, borough_count, avg_score, avg_income, avg_house_price, avg_pop_density in results:
    print(f"Airbnb pressure level: {str(level)}")

    print(f"  # Boroughs             : {int(borough_count)}")
    print(f"  Avg pressure score     : {float(avg_score)}")
    print(f"  Avg income             : {float(avg_income)}")
    print(f"  Avg house price        : {float(avg_house_price)}")
    print(f"  Avg population density : {float(avg_pop_density)}")
    print()

# Research Question 2
# Query 1: Examples of entire-home Airbnb listings in high Airbnb and housing pressure boroughs.
# Direct answer to RQ2 (with limit so that we don't print all thousands of them)
# NOTE: For the visualization, we wanted something like dots on the map, so we still need to include
# longitude and latitude in the RDF (I can do this later).
rq2_query1 = """
PREFIX ex: <http://example.org/london-airbnb/>

SELECT
    ?listing
    ?borough
    ?airbnbScore
    ?housingScore
WHERE {
    ?listing ex:isLocatedIn ?borough ;
             ex:hasRoomType ?roomType .
             
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
LIMIT 5
"""
results = graph.query(rq2_query1)

print("RQ2: Entire-home listings in high pressure boroughs")
for listing, borough, airbnb_score, housing_score in results:
    print(f"Listing ID: {shorten_uri(listing)}")
    print(f"  Borough        : {shorten_uri(borough)}")
    print(f"  Airbnb score   : {float(airbnb_score):.3f}")
    print(f"  Housing score  : {float(housing_score):.3f}")
    print()

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
        FILTER(str(?airbnbLevel) = "High")

    ?pressure ex:airbnbPressureLevel ?airbnbLevel .
    ?housing ex:housingPressureLevel ?housingLevel .
    FILTER(str(?housingLevel) = "High")
}
GROUP BY ?borough
ORDER BY DESC(?listingCount)
"""
results = graph.query(rq2_query2)

print("RQ2: Count of entire-home Airbnb listing count with high Airbnb pressure and high housing pressure")
for borough, listing_count in results:
    print(f"{shorten_uri(borough)}")
    print(f"  # Listings: {int(listing_count)}")

# Research Question 3
# Query 1: Hosts with listings in more than one borough (with at least one of them a high pressure one).
# NOTE: City of London does not have pressure profiles (we still have to decide whether to include this).
rq3_query1 =  """
PREFIX ex: <http://example.org/london-airbnb/>

SELECT
    ?host
    (COUNT(DISTINCT ?borough) AS ?boroughCount)
    # List of the individual borough names
    (GROUP_CONCAT(DISTINCT STRAFTER(STR(?borough), "/borough/"); separator=", ") AS ?boroughs)
WHERE {
    ?host ex:hasListing ?listing .
    ?listing ex:isLocatedIn ?borough .

    ?borough ex:hasPressureIndicator ?pressure .
    ?pressure ex:airbnbPressureLevel ?pressureLevel .

    # keep ONLY valid pressure values
    FILTER(BOUND(?pressureLevel))
}
GROUP BY ?host

# At least one of the boroughs has a "High" Airbnb pressure
HAVING (
    COUNT(DISTINCT ?borough) > 1 &&
    SUM(IF(str(?pressureLevel) = "High", 1, 0)) > 0
)
ORDER BY DESC(?boroughCount)
LIMIT 10
"""
results = graph.query(rq3_query1)

print("RQ3: Hosts which are connected to listings across multiple boroughs (high-pressure ones)")
for host_id, borough_count, borough_list in results:
    print(f"Host ID: {shorten_uri(host_id)}")
    print(f"  Borough count : {borough_count}")
    print(f"  Boroughs      : {borough_list}")
    print()

# Research Question 4
# Query 1: Boroughs that fall into each profile based on Airbnb pressure, housing pressure and transport accessibility score.
# NOTE: Might be better to add the transport bands directly into the graphs.
rq4_query1 = """
PREFIX ex: <http://example.org/london-airbnb/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT
    ?pressureLevel
    ?housingLevel
    ?transportBand
    (COUNT(?borough) AS ?boroughCount)
    # List of the individual borough names
    (GROUP_CONCAT(DISTINCT STRAFTER(STR(?borough), "/borough/"); separator=", ") AS ?boroughs)
WHERE {
    ?borough ex:hasPressureIndicator ?pressure ;
             ex:hasHousingIndicator ?housing ;
             ex:transportAccessibility ?transport .

    ?pressure ex:airbnbPressureLevel ?pressureLevel .
    ?housing ex:housingPressureLevel ?housingLevel .

    # Transport accessibility bands (might want to put this into the RDF graph before querying)
    BIND(xsd:float(?transport) AS ?transportNum)
    BIND(
        IF(?transportNum < 4, "Low",
        IF(?transportNum <= 6, "Medium", "High"))
        AS ?transportBand
    )
}

GROUP BY ?pressureLevel ?housingLevel ?transportBand
ORDER BY DESC(?boroughCount)
"""
results = graph.query(rq4_query1)

print("\nRQ4: Borough Pressure Profile Clusters")
for pressureLevel, housingLevel, transportBand, borough_count, boroughs in results:
    print("\nProfile:")
    print(f"  Pressure Level  : {pressureLevel}")
    print(f"  Housing Level   : {housingLevel}")
    print(f"  Transport Band  : {transportBand}")
    print(f"  Borough Count   : {int(borough_count)}")
    print(f"  Boroughs        : {boroughs}")
