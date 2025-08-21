import os
import time
import zipfile
from itertools import product
from multiprocessing import Pool, Event, Value, cpu_count, get_context

CHARS = 'abcdefghijklmnopqrstuvwxyz0123456789'
PASS_LEN = 6
PREFIX_LEN = 2
PROGRESS_EVERY = 100_000  # 워커 수가 많아질수록 늘리기

# 전역 변수: 워커 프로세스에서 ZIP 객체를 캐싱
_zip_path = None
_first_name = None

def _init_worker(zip_path, first_name):
    global _zip_path, _first_name
    _zip_path = zip_path
    _first_name = first_name

def _try_prefix(args):
    prefix, stop_event, counter, total = args
    suffix_len = PASS_LEN - len(prefix)
    chars = CHARS
    zpath = _zip_path
    name0 = _first_name

    try:
        with zipfile.ZipFile(zpath, 'r') as zf:
            for tup in product(chars, repeat=suffix_len):
                if stop_event.is_set():
                    return (False, None)

                pwd = prefix + ''.join(tup)
                try:
                    with zf.open(name0, 'r', pwd=pwd.encode('utf-8')) as fp:
                        fp.read(1)
                except RuntimeError:
                    pass
                except zipfile.BadZipFile:
                    return (False, None)
                else:
                    stop_event.set()
                    return (True, pwd)

                # 전역 카운터 갱신
                with counter.get_lock():
                    counter.value += 1
    except Exception:
        return (False, None)

    return (False, None)

def unlock_zip(zip_path):
    if not os.path.exists(zip_path):
        print('❌ ZIP 파일이 존재하지 않습니다:', zip_path)
        return

    print('패스워드 후보 문자:', CHARS)
    print('🔓 비밀번호 해킹을 시작합니다...')
    start_ts = time.time()
    print('시작 시간:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_ts)))

    first_name = None
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            if not names:
                print('❌ ZIP 내부에 파일이 없습니다.')
                return
            first_name = names[0]
    except zipfile.BadZipFile:
        print('❌ ZIP 파일이 손상되었습니다.')
        return
    except Exception as e:
        print('❌ ZIP 확인 중 오류 발생:', e)
        return

    prefixes = [''.join(p) for p in product(CHARS, repeat=PREFIX_LEN)]
    total_candidates = len(prefixes) * (len(CHARS) ** (PASS_LEN - PREFIX_LEN))

    workers = max(cpu_count() - 1, 1)
    ctx = get_context('spawn')
    stop_event = ctx.Event()
    counter = ctx.Value('Q', 0)

    print(f'병렬 작업 시작: 워커 {workers}개, 접두사 작업 {len(prefixes)}개')
    print(f'전체 후보 개수(추정): {total_candidates:,}')

    found_pwd = None
    last_print = 0

    try:
        with ctx.Pool(processes=workers,
                      initializer=_init_worker,
                      initargs=(zip_path, first_name)) as pool:

            jobs = ((pfx, stop_event, counter, total_candidates) for pfx in prefixes)

            for ok, pwd in pool.imap_unordered(_try_prefix, jobs, chunksize=5):
                now = time.time()
                done = counter.value
                if done - last_print >= PROGRESS_EVERY:
                    elapsed = now - start_ts
                    rate = done / elapsed if elapsed > 0 else 0.0
                    pct = (done / total_candidates) * 100 if total_candidates else 0.0
                    print(f'진행: {done:,}/{total_candidates:,} '
                          f'({pct:.3f}%), 경과 {elapsed:.1f}s, 속도 {rate:,.0f} pwd/s')
                    last_print = done

                if ok:
                    found_pwd = pwd
                    stop_event.set()
                    pool.terminate()
                    break

            pool.join()
    except KeyboardInterrupt:
        print('\n⏹️ 사용자가 중단했습니다.')
        return
    except Exception as e:
        print('❌ 예기치 못한 오류 발생:', e)
        return

    elapsed = time.time() - start_ts
    if found_pwd:
        print('\n✅ 비밀번호를 찾았습니다!')
        print('비밀번호:', found_pwd)
        print(f'총 시도: {counter.value:,}회, 총 소요: {elapsed:.2f}s')
        try:
            with open('password.txt', 'w', encoding='utf-8') as f:
                f.write(found_pwd + '\n')
            print('✅ password.txt 저장 완료')
        except Exception as e:
            print('❌ 비밀번호 저장 중 오류:', e)
    else:
        print('\n❌ 비밀번호를 찾지 못했습니다.')
        print(f'총 시도: {counter.value:,}회, 총 소요: {elapsed:.2f}s')

if __name__ == '__main__':
    unlock_zip('emergency_storage_key.zip')
