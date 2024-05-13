import matplotlib.pyplot as plt
import json

with open('../../agent_metrics.json', 'r') as file:
    data = json.load(file)

minutes = []
predicted = []
actual = []

minute_counter = 1

for key, value in data.items():
    minutes.append(minute_counter)
    predicted.append(value['prediction'])
    actual.append(value['actual'])
    minute_counter += 1

# Create the plot
plt.figure(figsize=(12, 6))
plt.plot(minutes, predicted, label='Predicted', linestyle='-', marker='None')
plt.plot(minutes, actual, label='Actual', linestyle='-', marker='None')
plt.title('Comparison of Predicted vs. Actual CPU Load')
plt.xlabel('Time (minutes since start)')
plt.ylabel('CPU Load')
plt.legend()
plt.grid(False)
plt.tight_layout()
plt.xticks(rotation=45)
plt.show()