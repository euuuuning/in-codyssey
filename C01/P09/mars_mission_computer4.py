import threading
import multiprocessing
import time
import random
import sys

class MissionComputer:
    def __init__(self, name):
        self.name = name
        self.running = True

    # 임무 정보 출력 (20초마다)
    def get_mission_computer_info(self):
        while self.running:
            print(f"[{self.name}] 🚀 미션 컴퓨터 정보 갱신 중...")
            time.sleep(20)

    # 시스템 부하 출력 (20초마다)
    def get_mission_computer_load(self):
        while self.running:
            load = random.randint(10, 90)
            print(f"[{self.name}] 💻 현재 시스템 부하: {load}%")
            time.sleep(20)

    # 센서 데이터 출력 (5초마다)
    def get_sensor_data(self):
        while self.running:
            sensor_value = random.uniform(0, 100)
            print(f"[{self.name}] 🌡 센서 데이터: {sensor_value:.2f}")
            time.sleep(5)

    # 중간에 멈추기 위한 stop 메소드
    def stop(self):
        self.running = False

# ----------------------------
# 멀티스레드 실행 함수
# ----------------------------
def run_threads(computer):
    threads = []
    # 스레드 생성
    threads.append(threading.Thread(target=computer.get_mission_computer_info))
    threads.append(threading.Thread(target=computer.get_mission_computer_load))
    threads.append(threading.Thread(target=computer.get_sensor_data))

    # 스레드 시작
    for t in threads:
        t.start()

    return threads

# ----------------------------
# 멀티프로세스 실행 함수
# ----------------------------
def run_process(computer):
    run_threads(computer)  # 각 프로세스에서 스레드 실행

# ----------------------------
# 키 입력 감지 함수
# ----------------------------
def monitor_stop_signal(computers):
    while True:
        key = input("🛑 종료하려면 q를 입력하세요: ").strip().lower()
        if key == "q":
            for comp in computers:
                comp.stop()
            print("✅ 프로그램을 종료합니다.")
            sys.exit(0)

# ----------------------------
# 메인 실행 부분
# ----------------------------
if __name__ == "__main__":
    # 3개의 MissionComputer 인스턴스 생성
    runComputer1 = MissionComputer("MissionComputer-1")
    runComputer2 = MissionComputer("MissionComputer-2")
    runComputer3 = MissionComputer("MissionComputer-3")

    # 멀티프로세스로 실행
    processes = []
    for comp in [runComputer1, runComputer2, runComputer3]:
        p = multiprocessing.Process(target=run_process, args=(comp,))
        processes.append(p)
        p.start()

    # 키 입력 감시 스레드 시작 (오타 수정 완료!)
    monitor_thread = threading.Thread(target=monitor_stop_signal, args=([runComputer1, runComputer2, runComputer3],))
    monitor_thread.daemon = True
    monitor_thread.start()

    # 프로세스 종료 대기
    for p in processes:
        p.join()
