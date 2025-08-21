# door_hacking.py
# -*- coding: utf-8 -*-
# Python 3.x / 표준 라이브러리만 사용
# 6자리 소문자+숫자 패스워드 브루트포스 (병렬 처리 최적화)
# 성공 시 password.txt에 저장

import os
import time
import zlib
import zipfile
import itertools
import multiprocessing as mp


CHARS = 'abcdefghijklmnopqrstuvwxyz0123456789'  # 후보 문자(소문자+숫자)
PASS_LEN = 6                                    # 정확히 6자리
ZIP_PATH = 'emergency_storage_key.zip'          # 대상 ZIP
OUT_FILE = 'password.txt'                       # 정답 저장 파일


def _try_with_prefix(args):
    """
    워커 프로세스가 실행할 함수.
    주어진 prefix(접두사)로 시작하는 길이 6 비밀번호를 모두 시도.
    성공 시 ('FOUND', password)를 반환.
    실패 시 ('DONE', tried_count)를 반환.
    """
    zip_path, member_name, prefix, stop_flag = args

    tried = 0
    try:
        # 워커 내부에서 ZIP 1회만 오픈 → 후보마다 매번 여는 것보다 크게 빠름
        with zipfile.ZipFile(zip_path) as zf:
            for tail in itertools.product(CHARS, repeat=PASS_LEN - len(prefix)):
                # 메인 프로세스가 이미 찾았으면 빠르게 종료
                if stop_flag.is_set():
                    return ('DONE', tried)

                password = prefix + ''.join(tail)
                tried += 1

                try:
                    # 가장 작은 파일 하나만 1바이트 읽어 빠르게 검증
                    with zf.open(member_name, 'r', pwd=password.encode('utf-8')) as f:
                        _ = f.read(1)
                    # 여기까지 오면 비번 정답
                    return ('FOUND', password)

                except (RuntimeError, zlib.error, zipfile.BadZipFile, KeyError, ValueError):
                    # 틀린 비번 / 압축 해제 중 오류 → 다음 후보로
                    continue

    except zipfile.BadZipFile:
        # ZIP 자체가 손상된 경우
        return ('ERROR', 'BadZipFile')
    except FileNotFoundError:
        return ('ERROR', 'ZipNotFound')
    except Exception as e:
        return ('ERROR', str(e))

    return ('DONE', tried)


def _pick_smallest_member(zf):
    """
    압축 내부에서 가장 작은 파일 하나를 선택해 테스트 대상으로 사용.
    읽어야 할 데이터를 최소화해 속도를 끌어올림.
    """
    infos = [i for i in zf.infolist() if not i.is_dir()]
    if not infos:
        # 폴더만 있거나 비어있는 ZIP
        raise RuntimeError('ZIP 안에 파일이 없습니다.')
    # 크기 기준 최소 파일 선택
    infos.sort(key=lambda x: x.file_size)
    return infos[0].filename


def unlock_zip(zip_path: str) -> None:
    """
    비밀번호 브루트포스(병렬)로 ZIP 해제.
    - 후보는 소문자+숫자, 길이 6
    - 진행 상황과 소요 시간 출력
    - 성공 시 password.txt 저장
    """
    if not os.path.exists(zip_path):
        print('❌ ZIP 파일을 찾을 수 없습니다:', zip_path)
        return

    print('패스워드 후보 문자:', CHARS)
    print('🔓 비밀번호 해킹을 시작합니다...')
    start_ts = time.time()
    print('시작 시간:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_ts)))

    # ZIP 내부에서 가장 작은 파일 하나만 대상으로 검증 → I/O 최소화
    try:
        with zipfile.ZipFile(zip_path) as zf:
            member_name = _pick_smallest_member(zf)
    except Exception as e:
        print('❌ ZIP 점검 중 오류:', e)
        return

    # 접두사(prefix) 단위로 일을 쪼개 병렬 처리 (여기선 길이 2 접두사)
    prefixes = [''.join(p) for p in itertools.product(CHARS, repeat=2)]

    # 멀티프로세싱 준비
    cpu = max(1, mp.cpu_count() - 1)  # 사용 코어 수 (한 코어는 여유)
    stop_flag = mp.Manager().Event()  # 정답 찾으면 모든 워커 중지 신호
    total_tried = 0
    last_report = time.time()

    print(f'병렬 작업 시작: 워커 {cpu}개, 접두사 작업 {len(prefixes)}개')

    with mp.Pool(processes=cpu) as pool:
        # 워커에 전달할 인자 생성기
        args_iter = ((zip_path, member_name, prefix, stop_flag) for prefix in prefixes)

        for result_type, payload in pool.imap_unordered(_try_with_prefix, args_iter):
            # 주기적으로 진행상황 출력
            now = time.time()
            if result_type == 'DONE':
                total_tried += payload  # payload = tried count for that prefix
                if now - last_report >= 2.0:
                    elapsed = now - start_ts
                    rate = total_tried / elapsed if elapsed > 0 else 0.0
                    print(f'… 진행: {total_tried:,}회 시도, 경과 {elapsed:,.1f}s, {rate:,.0f} 시도/초')
                    last_report = now

            elif result_type == 'FOUND':
                # 정답 발견 → 모든 워커 중단
                stop_flag.set()
                password = payload
                print(f'\n✅ 비밀번호 발견! → {password}')
                # 정답 저장
                try:
                    with open(OUT_FILE, 'w', encoding='utf-8') as f:
                        f.write(password)
                    print('✅ 비밀번호를 password.txt에 저장했습니다.')
                except Exception as e:
                    print('❌ 비밀번호 저장 실패:', e)

                # 실제 압축 해제 (전체 파일)
                try:
                    with zipfile.ZipFile(zip_path) as zf:
                        zf.extractall(pwd=password.encode('utf-8'))
                    print('📦 ZIP 압축 해제 완료!')
                except Exception as e:
                    print('⚠️ 압축 해제 중 경고:', e)

                pool.terminate()
                pool.join()
                elapsed = time.time() - start_ts
                print(f'총 시도: {total_tried:,}회 (일부 워커 집계 누락 가능), 총 소요: {elapsed:,.1f}s')
                return

            elif result_type == 'ERROR':
                # 개별 워커 오류 로그
                print('⚠️ 워커 오류:', payload)

    # 여기까지 오면 실패
    elapsed = time.time() - start_ts
    print('\n❌ 비밀번호를 찾지 못했습니다.')
    print(f'총 시도: {total_tried:,}회, 총 소요: {elapsed:,.1f}s')


if __name__ == '__main__':
    # Windows에서 멀티프로세싱 안전 가드 필수
    unlock_zip(ZIP_PATH)
