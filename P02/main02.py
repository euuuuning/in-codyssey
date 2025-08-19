# main02.py

file_path = r"D:\SW CAMP with Codyssey\C01\P02\mission_computer_main.log"

def read_log_file(file_path):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()[1:]  # 첫 줄은 헤더이므로 제외
        return lines
    except FileNotFoundError:
        print("❌ 파일을 찾을 수 없습니다.")
        return []
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return []

def parse_lines_to_list(lines):
    log_list = []
    for line in lines:
        parts = line.strip().split(',', 2)  # 최대 3조각으로 분할
        if len(parts) == 3:
            log_list.append(parts)
    return log_list

def print_log_list(log_list):
    print("▶ 리스트 객체:")
    for log in log_list:
        print(log)

def sort_logs_desc(log_list):
    return sorted(log_list, key=lambda x: x[0], reverse=True)

def convert_list_to_dict(log_list):
    dict_list = []
    for log in log_list:
        dict_list.append({
            "timestamp": log[0],
            "event": log[1],
            "message": log[2]
        })
    return dict_list

def save_as_json(dict_list, file_path):
    try:
        with open(file_path, 'w') as f:
            f.write('[\n')
            for i, item in enumerate(dict_list):
                json_line = '  {' + f'"timestamp": "{item["timestamp"]}", "event": "{item["event"]}", "message": "{item["message"]}"' + '}'
                if i < len(dict_list) - 1:
                    json_line += ','
                f.write(json_line + '\n')
            f.write(']')
        print(f"✅ JSON 파일 저장 완료 → {file_path}")
    except Exception as e:
        print(f"❌ JSON 저장 중 오류 발생: {e}")

# ----------------------------------------
# 🎁 보너스 과제: 특정 키워드 포함 로그 검색
# ----------------------------------------

def search_logs_by_keyword(file_path, keyword):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        print(f"\n🔍 '{keyword}'가 포함된 로그:")
        found = False
        for line in lines:
            if keyword.lower() in line.lower():
                print(line.strip())
                found = True
        if not found:
            print("해당 키워드가 포함된 로그를 찾을 수 없습니다.")
    except FileNotFoundError:
        print("❌ JSON 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"❌ 검색 중 오류 발생: {e}")

# ----------------------------------------
# 🧪 실행 흐름
# ----------------------------------------

log_path = "mission_computer_main.log"
json_path = "mission_computer_main.json"

# 1. 로그 파일 읽기
lines = read_log_file(log_path)

# 2. 리스트 변환
log_list = parse_lines_to_list(lines)

# 3. 리스트 출력
print_log_list(log_list)

# 4. 리스트 시간 역순 정렬
sorted_logs = sort_logs_desc(log_list)

# 5. 딕셔너리 변환
log_dict = convert_list_to_dict(sorted_logs)

# 6. JSON 파일로 저장
save_as_json(log_dict, json_path)

# 7. 보너스 과제 실행
# 직접 키워드 입력 가능 (아래 라인 주석 해제 시)
# keyword = input("\n검색할 키워드를 입력하세요: ")
# search_logs_by_keyword(json_path, keyword)

# 자동 실행 예시 (Oxygen 키워드 검색)
search_logs_by_keyword(json_path, "Oxygen")
