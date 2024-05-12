import csv
import signal
from engine.meta.layer import MetaLayer
import json
import copy


class StatisticsCollector:
    def __init__(self, meta_layer: MetaLayer, output_filename="system_metrics.json"):
        self.meta_layer = meta_layer
        self.output_filename = output_filename
        self.collected_data = {} #NOW A DICT

        signal.signal(signal.SIGINT, self.graceful_shutdown)

    def collect_metrics(self, time: str):
        # system_data = self.meta_layer.get_data()
        # self.collected_data.append(system_data)

        data = copy.deepcopy(self.meta_layer.get_data())
        self.collected_data[time] = data


    def save_to_csv(self):
        print(f"Saving data to {self.output_filename}")
        print(self.collected_data)
        with open(self.output_filename, 'w', newline='') as output_file:
            writer = csv.writer(output_file)
            writer.writerow(['time', 'system_data'])
            for time, data in self.collected_data.items():
                json_data = json.dumps(data)
                writer.writerow([time, json_data])
        print(f"Data saved to {self.output_filename}")
    
    def save_to_json(self):
        print(f"Saving data to {self.output_filename}")
        with open(self.output_filename, 'w') as output_file:
            json.dump(self.collected_data, output_file, indent=4)
        print(f"Data saved to {self.output_filename}")

    def graceful_shutdown(self, signum, frame):
        print("Graceful shutdown initiated...")
        self.save_to_json()
        exit(0)
