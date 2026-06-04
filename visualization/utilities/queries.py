# I renamed the fields to match the previous implementation with the mock data
GET_ALL_BOROUGHS = """
    PREFIX ex: <http://example.org/london-airbnb/>
    
    SELECT
        (?borough as ?name)
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

GET_ALL_LISTINGS = """
    PREFIX ex: <http://example.org/london-airbnb/>
    
    SELECT
        (?listing as ?name)
        ?borough
        ?room_type
        ?lat
        ?lon
    WHERE {
        ?listing ex:isLocatedIn ?borough ;
                 ex:hasRoomType ?roomType ;
                 ex:latitude ?lat ;
                 ex:longitude ?lon .        
    
         ?roomType ex:roomTypeName ?room_type .
    }
"""