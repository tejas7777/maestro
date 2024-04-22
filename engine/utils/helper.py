from engine.meta.layer import MetaLayer

class EngineHelper():
    def __init__(self,MetaLayerObj: MetaLayer):
        self.MetaLayerObj = MetaLayerObj

    def add_intance_meta_data(self, instance):
        return self.MetaLayerObj.create_record(
            identifier=instance.identifier,
            data = { "Instance":{
                        "cpu_usage":instance.current_cpu,
                        "requests_processed":0,
                        "status":1,
                        "scaling_events":0
                }
            }
        )

    def update_intance_meta_data(self, identifier, **kwargs):
        self.MetaLayerObj.update_record_by_indentifier(
            identifier,
            **kwargs
        )
