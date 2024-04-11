import json
import random
from scipy.stats import norm

# Define the structure of the JSON document
json_structure = {"April": {}}

# Parameters for the Gaussian distribution of requests across hours with multiple peak times
peak_hours = [14, 18]  # 2 PM and 6 PM as the peak hours for requests
std_dev = 1  # Standard deviation to control the spread around the peak hours


# Adjusting the generation of data for each day in April with randomness and ensuring no zero requests
for day in range(1, 32):  # Adjust for 31 days
    day_data = {
        "day": ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"][(day + 3) % 7],
        "special": random.choice([0, 1]),
        "marketing_campaign": random.choice([0, 1]),
        "time_passage": []
    }
    
    # Base number of requests, adjusted for special days and marketing campaigns
    base_num_requests = random.randint(1000,2000)
    if day_data["special"] or day_data["marketing_campaign"]:
        base_num_requests *= random.randint(3,4)  # Increase for special days or marketing campaigns

    # Normalize to the highest peak across all hours and multiple peaks
    proportions = [sum(norm.pdf(hour, peak, std_dev) for peak in peak_hours) for hour in range(24)]
    max_proportion = max(proportions)

    for hour in range(24):
        # Recalculating the proportion of requests with added randomness
        random_factor = random.uniform(0.8, 1.2)  # Adding a random factor to introduce variability
        proportion_of_requests = sum(norm.pdf(hour, peak, std_dev) for peak in peak_hours)
        num_requests = max(random.randint(10,50), int(base_num_requests * (proportion_of_requests / max_proportion) * random_factor))
        
        # Adding time passage data for each hour with adjustments
        day_data["time_passage"].append({
            "hour": hour,
            "num_req": num_requests
        })
    
    # Update the JSON structure with the new day data, incorporating randomness
    json_structure["April"][str(day)] = day_data

# Serialize and save the updated JSON with randomness adjustments
json_data = json.dumps(json_structure, indent=4)

with open('engine/artifacts/time.json', 'w') as f:
    f.write(json_data)