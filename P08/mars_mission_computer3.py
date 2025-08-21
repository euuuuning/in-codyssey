import platform
import psutil
import json
from mars_mission_computer2 import MissionComputer

class ExtendedMissionComputer(MissionComputer):
    def get_mission_computer_info(self):
        try:
            info = {
            "운영체계": platform.system(),
            "운영체계 버전": platform.version(),
            "CPU 타입": platform.processor(),
            "CPU 코어수": psutil.cpu_count(logical=True),  
            "메모리 크기(GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2)
            }
            print(json.dumps(info, ensure_ascii=False, indent=4))
            return info
        except Exception as e:
            return {"error": str(e)}
        
    def get_mission_computer_load(self):
        try:
            load = {
                'CPU 실시간 사용량(%)': psutil.cpu_percent(interval=1),
                '메모리 실시간 사용량(%)': psutil.virtual_memory().percent
            }
            print(json.dumps(load, ensure_ascii=False, indent=4))
            return load
        except Exception as e:
            return {"error": str(e)}


# 시스템 정보와 부하 출력
if __name__ == "__main__":
    runComputer = ExtendedMissionComputer()
    print("======== Mission Computer 시스템 정보 ========")
    runComputer.get_mission_computer_info()
    print("\n======== Mission Computer 부하 ========")
    runComputer.get_mission_computer_load()    