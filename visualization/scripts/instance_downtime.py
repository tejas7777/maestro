import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

with open('../../system_metrics.json', 'r') as file:
    data = json.load(file)

times = []
downtime_counts = []

minute_counter = 1

for time, details in data.items():
    downtime_count = sum(1 for inst_details in details['instances'].values() if inst_details['status'] == 0 and inst_details.get('restart_initiated') != 1)
    times.append(minute_counter)
    downtime_counts.append(downtime_count)
    minute_counter += 1

df = pd.DataFrame({
    'Time': times,
    'Downtime Count': downtime_counts
})

plt.figure(figsize=(10, 5))
plt.bar(df['Time'], df['Downtime Count'], color='steelblue', alpha=1)
plt.title('Downtime Frequency (Reactive Agent)')
plt.xlabel('Time (minutes since start)')
plt.ylabel('Number of Downtimes')
plt.grid(False)
plt.xticks(rotation=45)

plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

plt.tight_layout()
plt.show()
