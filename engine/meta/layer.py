import redis
import json

class MetaLayer:
    def __init__(self):
        self.__data = {
            "instances":{},
            "database_services":{},
            "time":{}
        }
        
        self.redis = redis.Redis(host='localhost', port=6379, db=0)



    def create_record(self,identifier: str, data)-> bool:
        self.__data[identifier] = data
        return True
 
    def update_record_by_indentifier(self,identifier, **kwargs):

        if identifier not in self.__data:
            print(f"[MetaLayer][update_records_by_indentifier][error] identifier {identifier} does not exist")
            return False
        
        for key, value in kwargs.items():
            self.__data[identifier][key] = value

        return True
            
    def get_data_identifier(self,identifier):
        return self.__data.get(identifier, {})
    

    def upsert_instance_data(self,indentifier,data):
        self.__data["instances"][indentifier] = data

    def upsert_database_service_data(self,indentifier,data):
        self.__data["database_services"][indentifier] = data

    def get_data(self):
        return self.__data

    def update_meta_data_cache(self):
        json_data = json.dumps(self.__data)
        # Store the JSON string in KeyDB
        self.redis.set('maestro_meta_data', json_data)


    def __str__(self):
        """
        Provide a string representation of the meta layer's data for easy debugging and logging.
        """
        from pprint import pformat
        return pformat(self.__data)