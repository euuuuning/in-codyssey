# design_dome.py

# 🎯 전역변수 선언
material = ""
diameter = 0.0
thickness = 1.0
area = 0.0 # cm² 단위
weight = 0.0 # kg 단위

# 🎯 재질별 밀도 (g/cm³)
material_density = {
    "유리": 2.4,
    "알루미늄": 2.7,
    "탄소강": 7.85
}

# 🎯 화성 중력 비율 (지구 중력 기준 0.38배)
mars_gravity = 0.38

# 🎯 반구체 면적 및 무게 계산 함수
def sphere_area(diameter, material="유리", thickness=1.0):
    global area, weight

    # 단위 변환 (m → cm)
    r = (diameter / 2) * 100

    # 면적 계산 (반구의 겉넓이: 2 * π * r²) # cm²
    area = round(2 * 3.1415926535 * r**2, 3)  

    # 밀도 가져오기
    density = material_density.get(material)
    if density is None:
        print("❌ 재질 정보가 잘못되었습니다.")
        return

    # 무게 계산 (면적 × 두께 × 밀도 × 화성중력), g → kg 단위 변환
    weight = area * thickness * density * mars_gravity / 1000
    weight = round(weight, 3)

    return round(area,3), weight

# 🎁 보너스 과제: 예외 처리 포함 사용자 입력 반복
while True:
    print("\n🏗️ 반구형 돔 무게 계산기 (종료하려면 'q' 입력)")

    # 지름 입력
    diameter_input = input("지름을 입력하세요 (단위: m): ")
    if diameter_input.lower() == 'q':
        print("프로그램을 종료합니다.")
        break

    try:
        diameter = float(diameter_input)
        if diameter == 0:
            print("❌ 지름은 0이 될 수 없습니다.")
            continue
    except ValueError:
        print("❌ 숫자 형식으로 입력해주세요.")
        continue

    # 재질 입력
    material_input = input("재질을 입력하세요 (유리, 알루미늄, 탄소강): ")
    if material_input not in material_density:
        print("❌ 지원하지 않는 재질입니다. (유리, 알루미늄, 탄소강 중 선택)")
        continue
    material = material_input

    # 두께 입력
    thickness_input = input("두께를 입력하세요 (단위: cm, 기본값 1): ")
    if thickness_input == "":
        thickness = 1.0
    else:
        try:
            thickness = float(thickness_input)
        except ValueError:
            print("❌ 숫자 형식으로 입력해주세요.")
            continue

    # 함수 호출
    sphere_area(diameter, material, thickness)
    
    # 면적 단위 변환: cm² → m²
    area_m2 = round(area / 10000, 3)

    # 결과 출력 (소수점 이하 3자리까지)
    print(f"재질 ⇒ {material}, 지름 ⇒ {diameter:.3f}, 두께 ⇒ {thickness:.3f}, 면적 ⇒ {area_m2:.3f} m², 무게 ⇒ {weight:.3f} kg")
