# -*- coding: utf-8 -*-
import os

def caesar_cipher_decode(target_text, dictionary):
    """
    target_text: 암호화된 문자열
    dictionary: 해독 성공 여부를 판단할 단어 리스트
    모든 시프트(0~25)를 시도하며 사전 단어 발견 시 자동 종료
    return: (shift, decoded_text) 또는 None
    """
    for shift in range(26):
        decoded = ""
        for char in target_text:
            if 'A' <= char <= 'Z':
                decoded += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            elif 'a' <= char <= 'z':
                decoded += chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
            else:
                decoded += char

        print(f"[Shift={shift}] {decoded}")  # 눈으로 확인 가능

        # 사전 단어 감지
        for word in dictionary:
            if word.lower() in decoded.lower():
                print(f"🔍 사전 단어 '{word}' 발견! (Shift={shift})")
                return shift, decoded

    return None, None  # 사전 단어 발견 실패

def main():
    password_path = r"D:\SW CAMP with Codyssey\C02\P02\password.txt"
    result_path = r"D:\SW CAMP with Codyssey\C02\P02\result.txt"

    # --- 사전 단어 리스트 ---
    dictionary = ["password", "secret", "hello", "mars", "love", "python"]

    # --- 파일 읽기 ---
    try:
        with open(password_path, "r", encoding="utf-8") as f:
            encrypted_text = f.read().strip()
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {password_path}")
        return
    except Exception as e:
        print(f"❌ 파일 읽는 중 오류 발생: {e}")
        return

    # --- 자동 해독 ---
    shift, decoded_text = caesar_cipher_decode(encrypted_text, dictionary)

    if shift is not None:
        # --- 결과 저장 ---
        try:
            with open(result_path, "w", encoding="utf-8") as f:
                f.write(decoded_text)
            print(f"✅ 암호 해독 완료! Shift={shift}")
            print(f"✅ '{result_path}'에 저장되었습니다.")
        except Exception as e:
            print(f"❌ 파일 저장 중 오류 발생: {e}")
    else:
        print("🔍 사전 단어 발견 실패. 수동 확인 필요.")
        # 수동 입력 옵션 제공
        try:
            shift_choice = int(input("정답으로 보이는 shift 번호를 입력하세요 (0~25): "))
            if 0 <= shift_choice < 26:
                decoded_text = ""
                for char in encrypted_text:
                    if 'A' <= char <= 'Z':
                        decoded_text += chr((ord(char) - ord('A') - shift_choice) % 26 + ord('A'))
                    elif 'a' <= char <= 'z':
                        decoded_text += chr((ord(char) - ord('a') - shift_choice) % 26 + ord('a'))
                    else:
                        decoded_text += char
                with open(result_path, "w", encoding="utf-8") as f:
                    f.write(decoded_text)
                print(f"✅ '{result_path}'에 저장되었습니다. (Shift={shift_choice})")
            else:
                print("❌ 유효하지 않은 숫자입니다. 종료합니다.")
        except ValueError:
            print("❌ 숫자가 입력되지 않았습니다. 종료합니다.")
        except Exception as e:
            print(f"❌ 파일 저장 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
