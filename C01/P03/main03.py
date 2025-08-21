filename = r'D:\SW CAMP with Codyssey\C01\P03\Mars_Base_Inventory_List.csv'
danger_filename = r'D:\SW CAMP with Codyssey\C01\P03\Mars_Base_Inventory_danger.csv'
bin_filename = r'D:\SW CAMP with Codyssey\C01\P03\Mars_Base_Inventory_List.bin'

def safe_float(value):
    try:
        return float(value)
    except:
        return -1  # 변환 불가 시 음수로 처리

def read_csv(file_path):
    inventory = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:  # 빈 줄 제외
                    inventory.append(line.split(','))
    except FileNotFoundError:
        print('❌ 파일을 찾을 수 없습니다.')
    except Exception as e:
        print('❌ 파일 읽기 중 오류 발생:', e)
    return inventory

def write_csv(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for row in data:
                f.write(','.join(row) + '\n')
        print(f'✅ CSV 파일 저장 완료 → {file_path}')
    except Exception as e:
        print('❌ 파일 저장 중 오류 발생:', e)

def write_bin(file_path, data):
    try:
        with open(file_path, 'wb') as f:
            for row in data:
                # 각 행을 쉼표로 합친 후 utf-8 인코딩, 줄바꿈(\n) 포함
                line = ','.join(row) + '\n'
                f.write(line.encode('utf-8'))
        print(f'✅ 이진 파일 저장 완료 → {file_path}')
    except Exception as e:
        print('❌ 이진 파일 저장 중 오류 발생:', e)

def read_bin(file_path):
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            # utf-8로 디코딩 후 줄 단위 분리
            lines = content.decode('utf-8').strip().split('\n')
            data = [line.split(',') for line in lines]
        return data
    except FileNotFoundError:
        print('❌ 이진 파일을 찾을 수 없습니다.')
    except Exception as e:
        print('❌ 이진 파일 읽기 중 오류 발생:', e)
    return []

def main():
    inventory = read_csv(filename)
    if not inventory:
        return

    header = inventory[0]
    items = inventory[1:]

    # 인화성 기준 내림차순 정렬
    items.sort(key=lambda x: safe_float(x[4]), reverse=True)

    # 인화성 0.7 이상인 항목 필터링
    danger_items = [row for row in items if safe_float(row[4]) >= 0.7]

    # 전체 정렬된 목록 출력
    print('▶ 전체 정렬된 적재 화물 목록:')
    print(header)
    for row in items:
        print(row)

    # 인화성 0.7 이상 목록 출력
    print('\n▶ 인화성 지수 0.7 이상 목록:')
    print(header)
    for row in danger_items:
        print(row)

    # CSV 파일로 저장
    write_csv(danger_filename, [header] + danger_items)

    # --- 보너스 과제 ---
    # 이진 파일로 저장
    write_bin(bin_filename, [header] + items)

    # 이진 파일 읽어서 출력
    print('\n▶ 이진 파일에서 읽어 들인 내용:')
    bin_data = read_bin(bin_filename)
    for row in bin_data:
        print(row)

if __name__ == '__main__':
    main()
