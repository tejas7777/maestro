import pandas as pd
import matplotlib.pyplot as plt
import json
import matplotlib.ticker as ticker

with open('../../system_metrics.json', 'r') as file:
    data = json.load(file)

times = []
avg_cpu_loads = []

minute_counter = 1

for time, details in data.items():
    times.append(minute_counter)
    avg_cpu_loads.append(details['system_data']['avg_cpu'])
    minute_counter += 1

df = pd.DataFrame({
    'Time': times,
    'Average CPU Load': avg_cpu_loads
})

plt.figure(figsize=(10, 5))
plt.plot(df['Time'], df['Average CPU Load'], linestyle='-', linewidth=2)
plt.title('Average CPU Load (Fuzzy Agent)')
plt.xlabel('Time (minutes since start)')
plt.ylabel('Average CPU Load')
plt.grid(False)

plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()