import os
import wave
import pyaudio
import threading
import time
from datetime import datetime

# 녹음 설정
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# 저장 경로 설정
SAVE_DIR = "records"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# 전역 변수
is_recording = False
start_time = None

def record_audio(filename):
    """오디오 녹음"""
    global is_recording, start_time
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    input=True, frames_per_buffer=CHUNK)

    frames = []
    start_time = time.time()
    is_recording = True

    def show_timer():
        """실시간 경과 시간 출력"""
        while is_recording:
            elapsed = int(time.time() - start_time)
            mm, ss = divmod(elapsed, 60)
            print(f"\r녹음 중... {mm:02}:{ss:02}  (중지하려면 Enter)", end="")
            time.sleep(1)

    # 타이머 스레드 시작
    timer_thread = threading.Thread(target=show_timer)
    timer_thread.start()

    print("\n녹음을 시작합니다. Enter를 누르면 중지됩니다.\n")

    while is_recording:
        data = stream.read(CHUNK)
        frames.append(data)

    # 타이머 종료 대기
    timer_thread.join()

    # 녹음 중지
    stream.stop_stream()
    stream.close()
    p.terminate()

    # WAV 파일 저장
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"\n녹음 완료! 저장된 파일: {filename}")

def main():
    global is_recording

    # 사용자에게 녹음 시작 여부 물어보기
    answer = input("녹음을 시작하시겠습니까? (Y/N): ").strip().lower()
    if answer != 'y':
        print("녹음을 취소했습니다.")
        return

    # 파일명 생성
    filename = os.path.join(SAVE_DIR, datetime.now().strftime("%Y%m%d-%H%M%S") + ".wav")

    # 녹음 스레드 시작
    record_thread = threading.Thread(target=record_audio, args=(filename,))
    record_thread.start()

    # 사용자 입력 대기 (Enter 입력 시 녹음 중지)
    input()
    is_recording = False

    # 녹음 스레드 종료 대기
    record_thread.join()

if __name__ == "__main__":
    main()
