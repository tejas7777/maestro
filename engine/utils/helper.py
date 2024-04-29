from engine.meta.layer import MetaLayer
from services.instances import StandardInstance
from engine.utils.time_data import TimeData
from services.database_service import DatabaseService

class EngineHelper():
    def __init__(self,meta_layer: MetaLayer, time_data: TimeData):
        self.meta_layer = meta_layer
        self.time_data = time_data

    def add_intance_meta_data(self, instance: StandardInstance, scaling_event = 0):
        instance_data = {
            "cpu_usage":instance.current_cpu,
            "requests_processed":instance.request_processed,
            "status":instance.state,
            "scaling_events":scaling_event,
            "max_cpu":instance.max_cpu,
            "instance_type":instance.instance_compute_type,
            "restart_initiated":instance.restart_initiated,
            "restart_count":instance.restart_count
            }

        return self.meta_layer.upsert_instance_data(
            indentifier= instance.get_instance_identifier(),
            data=instance_data
        )
    
    def add_database_instance_meta_data(self, instance: DatabaseService, scaling_event = 0):
        instance_data = {
            "disk_io_usage":instance.current_disk_io,
            "requests_processed":instance.current_connections,
            "status":instance.state,
            "scaling_events":scaling_event,
            "max_disk_io":instance.max_disk_io,
            "max_connections":instance.max_connections,
            "restart_initiated":instance.restart_initiated,
            "restart_count":instance.restart_count
            }

        return self.meta_layer.upsert_database_service_data(
            indentifier= instance.get_instance_identifier(),
            data=instance_data
        )
    

    
    def update_instance_meta_data(self,instances: list[StandardInstance]):
        for instance in instances:
            self.add_intance_meta_data(instance=instance)

    def update_time_in_meta_layer(self):
        self.meta_layer.update_record_by_indentifier(
            identifier="time",
            data = self.time_data.get_current_time()
        )

    def update_meta_data_after_every_minuite(self,data):
        self.update_time_in_meta_layer()
        self.update_instance_meta_data(instances=data["instances"])
        self.meta_layer.update_meta_data_cache()