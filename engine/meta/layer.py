class MetaLayer:
    def __init__(self):
        self.__data = {}


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


    def __str__(self):
        """
        Provide a string representation of the meta layer's data for easy debugging and logging.
        """
        from pprint import pformat
        return pformat(self.__data)