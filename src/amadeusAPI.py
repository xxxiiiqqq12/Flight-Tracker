from amadeus import Client, ResponseError


# currently using the "test API" can be changed to production later
amadeus = Client(
    client_id='GAbV3UCbJ0T6CXUg329teBLEwFbRfo94',
    client_secret='6RHnnRHdge8qn0bZ',
    hostname='test'
)


def search_flights(departure, arrival, departure_date, return_date=None):
    """
    Searches for flights between two locations on specified dates.

    Parameters:
    - departure (str): code of the departure airport.
    - arrival (str): code of the arrival airport.
    - departure_date (str): Departure date in 'YYYY-MM-DD' format.
    - return_date (str, optional): Return date in 'YYYY-MM-DD' format for round-trip flights.

    Returns:
    - list: A list of flight offers with price and duration.
    """
    try:
        if return_date:
            # Round-trip search
            response = amadeus.shopping.flight_offers_search.get(
                originLocationCode=departure,
                destinationLocationCode=arrival,
                departureDate=departure_date,
                returnDate=return_date,
                adults=1,
                currencyCode='EUR',
                max=250  # Maximum number of results
            )
        else:
            # One-way search
            response = amadeus.shopping.flight_offers_search.get(
                originLocationCode=departure,
                destinationLocationCode=arrival,
                departureDate=departure_date,
                adults=1,
                currencyCode='EUR',
                max=250
            )

        flight_offers = response.data
        return flight_offers

    except ResponseError as error:
        print(f"An error occurred: {error}")
        return []



def extract_flight_data(flight_offers):
    """
    Extracts relevant flight data from flight offers.

    Parameters:
    - flight_offers (list): List of flight offers returned by the API.

    Returns:
    - list: A list of dictionaries containing flight details.
    """
    flight_data = []

    for offer in flight_offers:
        price = float(offer['price']['grandTotal'])
        itineraries = offer['itineraries']
        total_duration = 0.0  # In hours
        segments_info = []

        for itinerary in itineraries:
            duration = parse_duration(itinerary['duration'])
            total_duration += duration
            segments = itinerary['segments']
            segments_info.extend(segments)

        # Get flight path information
        flight_path = get_flight_path(segments_info)

        flight_data.append({
            'Price': price,
            'Total Duration': total_duration,
            'Flight Path': flight_path,
            'Departure Airport': segments_info[0]['departure']['iataCode'],
            'Arrival Airport': segments_info[-1]['arrival']['iataCode'],
            'Departure DateTime': segments_info[0]['departure']['at'],
            'Arrival DateTime': segments_info[-1]['arrival']['at'],
            'Number of Stops': len(segments_info) - 1
        })

    return flight_data

def parse_duration(duration_str):
    """
    Parses ISO 8601 duration string into hours.

    Parameters:
    - duration_str (str): Duration string in ISO 8601 format (e.g., 'PT2H30M').

    Returns:
    - float: Duration in hours.
    """
    import re
    pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?')
    match = pattern.match(duration_str)
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    total_hours = hours + minutes / 60
    return total_hours

def get_flight_path(segments):
    """
    Constructs a string representing the flight path.

    Parameters:
    - segments (list): List of flight segments.

    Returns:
    - str: Flight path description.
    """
    airports = [segments[0]['departure']['iataCode']]
    for segment in segments:
        airports.append(segment['arrival']['iataCode'])
    flight_path = ' -> '.join(airports)
    return flight_path
