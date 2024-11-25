import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt

from amadeusAPI import extract_flight_data, search_flights

# Update parameters to match test environment
departure_airport = 'MAD'  # Madrid
destinations = ['CDG']     # Paris Charles de Gaulle
departure_dates = pd.date_range(start='2024-11-25', end='2024-12-01', freq='D')
stay_durations = [11]  # For a return date of 2023-08-12

def collect_flight_data(departure_airport, destinations, departure_dates, stay_durations):
    all_flight_data = []

    for destination in destinations:
        for departure_date in departure_dates.strftime('%Y-%m-%d'):
            for stay_duration in stay_durations:
                # Calculate return date
                return_date = (pd.to_datetime(departure_date) + pd.Timedelta(days=stay_duration)).strftime('%Y-%m-%d')

                print(f"Searching flights from {departure_airport} to {destination} departing on {departure_date} and returning on {return_date}")

                # Search for round-trip flights
                flight_offers = search_flights(departure_airport, destination, departure_date, return_date)
                flight_data = extract_flight_data(flight_offers)

                # Add additional info if flight_data is not empty
                if flight_data:
                    for data in flight_data:
                        data['Destination'] = destination
                        data['Departure Date'] = departure_date
                        data['Return Date'] = return_date
                        data['Stay Duration'] = stay_duration
                        data['Trip Type'] = 'Round-Trip'

                    all_flight_data.extend(flight_data)
                else:
                    print(f"No flights found for {departure_airport} to {destination} on {departure_date}")

                time.sleep(1)  # Respect API rate limits

    return all_flight_data

# Collect data
flight_data = collect_flight_data(departure_airport, destinations, departure_dates, stay_durations)

# Check if data was collected
if flight_data:
    df = pd.DataFrame(flight_data)
    print("Flight data collected successfully:")
    print(df)
else:
    print("No flight data was collected. Please check your parameters and try again.")



"""

# Storing data in excel 

df = pd.DataFrame(flight_data)
df.to_excel('flight_prices_round_trip.xlsx', index=False)


# Finding the cheapest flights 
cheapest_flights = df.loc[df.groupby(['Destination'])['Price'].idxmin()]

print(cheapest_flights[['Destination', 'Departure Date', 'Return Date', 'Price', 'Flight Path']])


# Ensure date columns are datetime objects
df['Departure Date'] = pd.to_datetime(df['Departure Date'])

# Plot price trends for each destination
for destination in destinations:
    dest_df = df[df['Destination'] == destination]
    
    # Create a new figure
    plt.figure(figsize=(12, 6))
    
    # Plotting data for different stay durations
    stay_durations = dest_df['Stay Duration'].unique()
    
    for stay_duration in stay_durations:
        stay_df = dest_df[dest_df['Stay Duration'] == stay_duration]
        plt.plot(stay_df['Departure Date'], stay_df['Price'], marker='o', label=f'Stay {stay_duration} days')
    
    # Set the title and labels
    plt.title(f'Round-Trip Flight Prices Over Time to {destination}')
    plt.xlabel('Departure Date')
    plt.ylabel('Price (EUR)')
    plt.legend(title='Stay Duration')
    plt.grid(True)
    plt.tight_layout()
    
    # Show the plot
    plt.show()

"""
