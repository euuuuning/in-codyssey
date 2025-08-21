import time
import json
from mars_mission_computer import DummySensor

class MissionComputer:
    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': None,      
            'mars_base_external_temperature': None,      
            'mars_base_internal_humidity': None,         
            'mars_base_external_illuminance': None,      
            'mars_base_internal_co2': None,              
            'mars_base_internal_oxygen': None            
        }
        
        self.ds = DummySensor()
        

    def get_sensor_data(self):
       
        while True:
            self.ds.set_env()
            self.env_values = self.ds.get_env()        
            print(json.dumps(self.env_values, ensure_ascii=False, indent=4))
            time.sleep(5)
         
if __name__ == "__main__":
    RunComputer = MissionComputer()
    RunComputer.get_sensor_data()