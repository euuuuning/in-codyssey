import numpy as np

# 파일 경로 지정
file1 = "D:/SW CAMP with Codyssey/C01/P05/mars_base_main_parts-001.csv"
file2 = "D:/SW CAMP with Codyssey/C01/P05/mars_base_main_parts-002.csv"
file3 = "D:/SW CAMP with Codyssey/C01/P05/mars_base_main_parts-003.csv"

# CSV 파일을 ndarray로 읽기 (헤더 제외)
arr1 = np.genfromtxt(file1, delimiter=',', skip_header=1)
arr2 = np.genfromtxt(file2, delimiter=',', skip_header=1)
arr3 = np.genfromtxt(file3, delimiter=',', skip_header=1)

# 배열 합치기
parts = np.vstack((arr1, arr2, arr3))

# 평균값 계산
mean_values = np.mean(parts, axis=0)

# 평균값이 50 미만인 행 추출
low_parts = parts[np.mean(parts, axis=1) < 50]

# 결과 저장
output_path = "D:/SW CAMP with Codyssey/C01/P05/parts_to_work_on.csv"
try:
    np.savetxt(output_path, low_parts, delimiter=",", fmt="%.3f")
    print(f"✅ parts_to_work_on.csv 저장 완료: {output_path}")
except Exception as e:
    print(f"❌ 저장 중 오류 발생: {e}")

# 🎁 보너스 과제
try:
    parts2 = np.genfromtxt(output_path, delimiter=",")
    parts3 = parts2.T  # 전치행렬
    print("📐 전치 행렬:")
    print(np.round(parts3, 3))
except Exception as e:
    print(f"❌ 보너스 과제 수행 중 오류 발생: {e}")
