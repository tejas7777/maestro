'''
NOTE THIS CLASS IS DEPRECATED AND NOT USED IN THE FINAL IMPLEMENTATION
'''

class ExecutorPipeline():
    def __init__(self, execution_pipeline):
        self.process_execution_pipeline:list[dict] = []
        self.data = []
    

    def execute(self,minuite,hour, initial_stage_data = {}):

        stage_data = initial_stage_data
        for i in range(len(self.process_execution_pipeline)):
            stage = self.process_execution_pipeline[i]
            stage_name = stage.keys()[0]
            stage_runner = stage.values()[0]

            output = stage_runner.execute(stage_data)

            


        
        

