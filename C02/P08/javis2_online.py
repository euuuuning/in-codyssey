#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
javis2_online.py

- ./records 폴더에서 WAV 파일을 찾아 Google STT로 변환
- CSV로 저장 (time, text)
- 한국어 지원
- 무료 범위(월 60분) 내 사용량 확인 메시지 출력
"""

import os
import csv
import time
from pathlib import Path
import wave

# Google STT 라이브러리
try:
    import speech_recognition as sr
except ImportError:
    raise SystemExit("speech_recognition 라이브러리가 필요합니다. 설치: pip install SpeechRecognition")

# 설정
RECORDS_DIR = Path.cwd() / "records"
CSV_HEADERS = ["time", "text"]
GOOGLE_FREE_MINUTES = 60  # 한 달 기준 무료 60분

def find_wav_files(directory: Path):
    """디렉터리에서 WAV 파일 목록 반환"""
    return sorted([f for f in directory.iterdir() if f.suffix.lower() == ".wav"])

def seconds_to_hhmmss(seconds: float) -> str:
    """초를 HH:MM:SS.mmm 형식 문자열로 변환"""
    total_ms = int(round(seconds * 1000))
    s, ms = divmod(total_ms, 1000)
    h, rem = divmod(s, 3600)
    m, s2 = divmod(rem, 60)
    return f"{h:02}:{m:02}:{s2:02}.{ms:03}"

def transcribe_wav_to_csv(wav_path: Path, recognizer: sr.Recognizer):
    """Google STT로 WAV 파일 변환 후 CSV 저장"""
    csv_path = wav_path.with_suffix(".CSV")
    with sr.AudioFile(str(wav_path)) as source:
        audio = recognizer.record(source)
    try:
        # 한국어 지정
        text = recognizer.recognize_google(audio, language="ko-KR")
    except sr.UnknownValueError:
        text = ""
    except sr.RequestError as e:
        raise SystemExit(f"Google STT 요청 실패: {e}")

    # WAV 길이 추출 (초 단위)
    with wave.open(str(wav_path), 'rb') as wf:
        duration_sec = wf.getnframes() / wf.getframerate()

    # CSV 저장
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)
        if text:
            writer.writerow([seconds_to_hhmmss(0), text])

    return csv_path, duration_sec

def main():
    if not RECORDS_DIR.exists():
        print(f"녹음 폴더가 없습니다: {RECORDS_DIR}")
        return

    wav_files = find_wav_files(RECORDS_DIR)
    if not wav_files:
        print(f"WAV 파일이 없습니다: {RECORDS_DIR}")
        return

    recognizer = sr.Recognizer()
    total_used_minutes = 0.0

    print("Google STT 변환 시작...")
    for wav_file in wav_files:
        print(f"  · 처리 중: {wav_file.name}")
        try:
            csv_file, duration_sec = transcribe_wav_to_csv(wav_file, recognizer)
            total_used_minutes += duration_sec / 60
            remaining_minutes = max(GOOGLE_FREE_MINUTES - total_used_minutes, 0)
            print(f"    → 저장 완료: {csv_file} (길이 {duration_sec:.1f}s)")
            print(f"    → 무료 범위 남은 시간: {remaining_minutes:.1f}분")
        except Exception as exc:
            print(f"    ! 오류: {exc}")

    print("모든 파일 처리 완료.")
    print(f"이번 실행 총 사용 시간: {total_used_minutes:.1f}분 / 무료 범위 {GOOGLE_FREE_MINUTES}분")

if __name__ == "__main__":
    main()
