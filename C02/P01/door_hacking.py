import zipfile
import itertools
import string
import time
import multiprocessing
from datetime import datetime
import io

class ZipCracker:
    def __init__(self, zip_path, password_length=6, output_file='password.txt'):
        self.zip_path = zip_path
        self.password_length = password_length
        self.output_file = output_file
        self.chars = list(string.ascii_lowercase + string.digits)
        self.cpu_count = multiprocessing.cpu_count()

        # 공유 변수
        self.found = multiprocessing.Value('b', False)
        self.found_password = multiprocessing.Array('c', b' ' * password_length)
        self.stop_event = multiprocessing.Event()
        self.counter = multiprocessing.Value('i', 0)

        # ZIP 파일을 메모리에 로딩
        self.zip_bytes = self.load_zip_bytes()

    def load_zip_bytes(self):
        with open(self.zip_path, 'rb') as f:
            return f.read()

    def try_passwords(self, prefixes):
        for prefix in prefixes:
            if self.found.value or self.stop_event.is_set():
                return

            suffix_len = self.password_length - len(prefix)
            for combo in itertools.product(self.chars, repeat=suffix_len):
                if self.found.value or self.stop_event.is_set():
                    return

                attempt = prefix + ''.join(combo)

                with self.counter.get_lock():
                    self.counter.value += 1

                try:
                    with zipfile.ZipFile(io.BytesIO(self.zip_bytes)) as zf:
                        zf.extractall(pwd=attempt.encode('utf-8'))
                    with self.found.get_lock():
                        self.found.value = True
                        self.stop_event.set()
                        self.found_password[:] = attempt.encode('utf-8')
                    return
                except:
                    continue

    def monitor_progress(self):
        start = time.time()
        while not self.found.value and not self.stop_event.is_set():
            time.sleep(5)
            elapsed = int(time.time() - start)
            print(f"[⏱ {elapsed}s] 시도 횟수: {self.counter.value:,}")

    def run(self):
        print(f"🔓 비밀번호 해킹 시작 (멀티프로세싱 {self.cpu_count}코어 사용)")
        print(f"패스워드 후보 문자: {''.join(self.chars)}")
        print(f"전체 후보 개수: {len(self.chars) ** self.password_length:,}개\n")

        # 접두사 생성 및 분할
        prefix_len = 2
        all_prefixes = [''.join(p) for p in itertools.product(self.chars, repeat=prefix_len)]
        chunk_size = (len(all_prefixes) + self.cpu_count - 1) // self.cpu_count
        chunks = [all_prefixes[i * chunk_size:(i + 1) * chunk_size] for i in range(self.cpu_count)]

        # 프로세스 생성
        processes = []
        for chunk in chunks:
            p = multiprocessing.Process(target=self.try_passwords, args=(chunk,))
            processes.append(p)
            p.start()

        # 진행 상황 모니터링
        monitor = multiprocessing.Process(target=self.monitor_progress)
        monitor.start()

        try:
            while not self.found.value and not self.stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⛔ 사용자 중단. 모든 프로세스를 종료합니다...")
            self.stop_event.set()

        for p in processes:
            p.join()
        monitor.terminate()

        found_pw = self.found_password[:].decode('utf-8').rstrip()
        print(f"\n🏁⏱️ 종료 시간: {datetime.now().strftime('%H:%M:%S')} — 총 시도 횟수: {self.counter.value:,}")

        if found_pw:
            print(f"🔐 저장된 비밀번호: {found_pw}")
            with open(self.output_file, 'w') as f:
                f.write(found_pw)
            print(f"📁 비밀번호가 '{self.output_file}' 파일에 저장되었습니다.")
        else:
            print("❌ 비밀번호를 찾지 못했습니다.")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    cracker = ZipCracker(zip_path='emergency_storage_key.zip')
    cracker.run()