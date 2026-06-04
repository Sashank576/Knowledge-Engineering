# I renamed the fields to match the previous implementation with the mock data
GET_ALL_BOROUGHS = """
    PREFIX ex: <http://example.org/london-airbnb/>
    
    SELECT
        (?borough as ?name)
        ?airbnb_pressure_indicator
        ?housing_indicator
        ?transportation_indicator
    WHERE {
        ?borough ex:hasPressureIndicator ?pressureIndicator .
        ?pressureIndicator ex:airbnbPressureLevel ?airbnb_pressure_indicator .
    
        ?borough ex:hasHousingIndicator ?housingIndicator .
        ?housingIndicator ex:housingPressureLevel ?housing_indicator .
    
        ?borough ex:hasTransportIndicator ?transportIndicator .
        ?transportIndicator ex:transportPressureLevel ?transportation_indicator .
    }
"""