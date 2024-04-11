import matplotlib.pyplot as plt
import numpy as np
import json

# Load the JSON data from the file
with open('engine/artifacts/time.json', 'r') as f:
    json_data = json.load(f)

# Extracting data for visualization
hourly_traffic_weekdays = {hour: [] for hour in range(24)}  # Dictionary to hold traffic counts for each hour

# Iterate over each day in April, accumulating traffic counts for each hour
for day, day_data in json_data["April"].items():
    if day_data["day"] not in ["SAT", "SUN"]:  # Skip weekends
        continue
    if day_data["special"] == 1:  # Skip special days
        continue
    if day_data["marketing_campaign"] == 1:
        continue
    for hour_data in day_data["time_passage"]:
        hourly_traffic_weekdays[hour_data["hour"]].append(hour_data["num_req"])

# Calculating average traffic for each hour across non-special weekdays
avg_traffic_weekdays = [np.mean(hourly_traffic_weekdays[hour]) for hour in range(24)]

# Visualization for non-special weekdays
plt.figure(figsize=(10, 6))
plt.plot(range(24), avg_traffic_weekdays, marker='o', linestyle='-', color='g')
plt.title('Average Traffic Distribution Across Non-Special Weekdays')
plt.xlabel('Hour of the Day')
plt.ylabel('Average Number of Requests')
plt.xticks(range(0, 24, 1))
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.tight_layout()
plt.show()