import pandas as pd
import matplotlib.pyplot as plt
import json
import matplotlib.ticker as ticker

# Load your JSON data
with open('../../system_metrics.json', 'r') as file:
    data = json.load(file)

# Prepare the data for plotting
times = []
avg_cpu_loads = []

# Use a counter to assign minutes sequentially
minute_counter = 1

for time, details in data.items():
    times.append(minute_counter)  # Append the counter as the current minute
    avg_cpu_loads.append(details['system_data']['avg_cpu'])
    minute_counter += 1  # Increment the counter for the next row

# Create a DataFrame
df = pd.DataFrame({
    'Time': times,
    'Average CPU Load': avg_cpu_loads
})

# Plotting
plt.figure(figsize=(10, 5))
plt.plot(df['Time'], df['Average CPU Load'], linestyle='-', linewidth=2)
plt.title('Average CPU Load (Reactive Agent)')
plt.xlabel('Time (minutes since start)')
plt.ylabel('Average CPU Load')
plt.grid(False)

# Ensure x-axis shows integer labels correctly
plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()