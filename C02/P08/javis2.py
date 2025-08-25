#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
 j a v i s 2 . p y

문제 7에서 생성된 녹음 파일(.wav)을 찾아
각 파일에 대해 오프라인 STT(음성→텍스트)를 수행하고,
인식 결과를 "시간, 텍스트" 형식의 CSV로 저장한다.

- 기본 탐색 경로:
  1) 현재 경로의 ./records
  2) 상위 폴더의 ./P07/records
  (둘 다 존재하면 둘 다 처리)

- STT 엔진: Vosk (오프라인)
  pip install vosk
  모델 경로는 환경변수 VOSK_MODEL 또는 --model 옵션으로 지정.
  (예: 한국어 소형 모델: vosk-model-small-ko-0.22)

- CSV 저장 규칙:
  원본 오디오 파일명과 동일하게 하되 확장자를 .CSV 로 저장(같은 디렉터리)
  열: time, text

사용 예시:
  python javis2.py
  python javis2.py --records-dir ../P07/records --model ./models/vosk-model-small-ko-0.22
'''

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
from typing import Iterable, List, Optional
import wave

# --- 외부 라이브러리 (STT 전용 허용) ---
try:
    from vosk import Model, KaldiRecognizer  # type: ignore
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        'Vosk 라이브러리가 필요합니다.\n'
        '설치: pip install vosk\n'
        '안내: https://alphacephei.com/vosk'
    ) from exc


# --------------------------- 설정 ---------------------------
DEFAULT_SEARCH_DIRS: List[Path] = [
    Path.cwd() / 'records',
    Path.cwd().parent / 'P07' / 'records',
]
CHUNK_SIZE = 8_000  # bytes; 16-bit PCM 기준 약 4k 샘플
CSV_HEADERS = ['time', 'text']


# ------------------------ 유틸 함수 -------------------------

def find_wav_files(dirs: Iterable[Path]) -> List[Path]:
    files: List[Path] = []
    for d in dirs:
        if d.exists() and d.is_dir():
            for p in sorted(d.iterdir()):
                if p.is_file() and p.suffix.lower() == '.wav':
                    files.append(p)
    return files


def load_vosk_model(path: Optional[Path]) -> Model:
    '''Vosk 모델을 로드한다.''' 
    # 우선순위: --model 옵션 > 환경변수 VOSK_MODEL
    model_dir = path
    if model_dir is None:
        env = os.environ.get('VOSK_MODEL')
        if env:
            model_dir = Path(env)

    if not model_dir:
        raise SystemExit(
            'Vosk 모델 경로가 지정되지 않았습니다.\n'
            '옵션 --model <DIR> 또는 환경변수 VOSK_MODEL 로 모델 폴더를 지정하세요.\n'
            '예) --model ./models/vosk-model-small-ko-0.22'
        )

    if not model_dir.exists():
        raise SystemExit(f'모델 경로가 없습니다: {model_dir}')

    return Model(str(model_dir))


def seconds_to_hhmmss(seconds: float) -> str:
    total_ms = int(round(seconds * 1_000))
    s, ms = divmod(total_ms, 1_000)
    h, rem = divmod(s, 3_600)
    m, s2 = divmod(rem, 60)
    return f'{h:02}:{m:02}:{s2:02}.{ms:03}'


# ------------------------- STT 로직 -------------------------

def transcribe_wav_to_csv(model: Model, wav_path: Path) -> Path:
    '''
    WAV 파일을 읽어 STT 수행 후 결과를 같은 폴더에 .CSV 로 저장한다.
    CSV는 (time, text) 형식으로 "부분 결과" 단위로 기록한다.
    '''
    with wave.open(str(wav_path), 'rb') as wf:
        if wf.getsampwidth() != 2:
            raise SystemExit(
                f'지원하지 않는 샘플 폭({wf.getsampwidth()*8}bit): {wav_path}. 16-bit PCM 필요.'
            )
        rate = wf.getframerate()
        channels = wf.getnchannels()
        if channels != 1:
            raise SystemExit(
                f'현재 스크립트는 모노(1채널)만 지원합니다. 채널수={channels}, 파일={wav_path}'
            )

        rec = KaldiRecognizer(model, rate)
        rec.SetWords(True)

        rows: List[List[str]] = []
        while True:
            data = wf.readframes(CHUNK_SIZE // 2)  # 2 bytes per sample
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                part = json.loads(rec.Result())
                text, ts = extract_text_and_time(part)
                if text:
                    rows.append([seconds_to_hhmmss(ts), text])
        # 잔여 결과
        last = json.loads(rec.FinalResult())
        text, ts = extract_text_and_time(last)
        if text:
            rows.append([seconds_to_hhmmss(ts), text])

    # CSV 저장
    csv_path = wav_path.with_suffix('.CSV')
    with csv_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)
        writer.writerows(rows)

    return csv_path


def extract_text_and_time(vosk_result: dict) -> tuple[str, float]:
    '''
    Vosk의 결과 JSON(dict)에서 텍스트와 시작 시간을 추출한다.
    - 단어 리스트가 있으면 첫 단어의 start 를 시간으로 사용
    - 없으면 전체 텍스트만 사용하며 시간은 0.0
    '''
    text = str(vosk_result.get('text', '')).strip()
    words = vosk_result.get('result') or []
    if words:
        ts = float(words[0].get('start', 0.0))
    else:
        ts = 0.0
    return text, ts


# --------------------------- CLI ----------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='javis2.py',
        description='녹음 파일들을 STT로 변환하고 CSV로 저장합니다.',
    )
    parser.add_argument(
        '--records-dir',
        metavar='DIR',
        type=Path,
        default=None,
        help='녹음 파일(.wav) 탐색 디렉터리. 지정하지 않으면 기본 경로들을 사용.',
    )
    parser.add_argument(
        '--model',
        metavar='DIR',
        type=Path,
        default=None,
        help='Vosk 모델 디렉터리 경로. 미지정 시 환경변수 VOSK_MODEL 사용.',
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    model = load_vosk_model(args.model)

    search_dirs: List[Path]
    if args.records_dir:
        search_dirs = [args.records_dir]
    else:
        search_dirs = [d for d in DEFAULT_SEARCH_DIRS if d.exists()]
        if not search_dirs:
            # records 폴더가 없더라도 친절히 안내
            search_dirs = [DEFAULT_SEARCH_DIRS[0]]

    wav_files = find_wav_files(search_dirs)
    if not wav_files:
        print('처리할 WAV 파일이 없습니다. 경로를 확인하세요:')
        for d in search_dirs:
            print(f' - {d}')
        return

    print('STT 시작...')
    for wav_path in wav_files:
        print(f'  · 처리 중: {wav_path}')
        try:
            csv_path = transcribe_wav_to_csv(model, wav_path)
            print(f'    → 저장 완료: {csv_path}')
        except SystemExit as err:
            # 개별 파일 에러는 보고만 하고 계속 진행
            print(f'    ! 오류: {err}')
        except Exception as exc:  # pragma: no cover
            print(f'    ! 예기치 못한 오류: {exc}')

    print('모든 처리가 완료되었습니다.')


if __name__ == '__main__':
    main()
