# main.py
# C01-P01

print('Hello Mars')


filename = r'D:\SW CAMP with Codyssey\C01\P01\mission_computer_main.log'
output = 'log_analysis.md'
problem_output = 'problem_logs.md'

try:
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print(lines)

    # oxygen 포함 로그만 필터링
    accident_logs = [line.strip() for line in lines if 'oxygen' in line.lower()]

    # 시간 문자열 기준으로 역순 정렬 (문자열 정렬로 처리)
    accident_logs.sort(
        key=lambda log: log.split(',')[0],  # 시간 부분만 비교
        reverse=True
    )

    # 문제 로그: explosion 또는 unstable 포함
    keywords = ['explosion', 'unstable']
    problem_logs = [
        log for log in accident_logs if any(k in log.lower() for k in keywords)
    ]

    # 사고 보고서 작성 (log_analysis.md)
    with open(output, 'w', encoding='utf-8') as f:
        f.write('# 사고 로그 보고서\n\n')
        f.write('##  사고 원인 분석\n')
        if problem_logs:
            f.write('- 로그에 따르면, 산소 탱크의 이상 상태 후 폭발이 발생함.\n')
            f.write('- 시간 흐름상 다음의 문제가 나타남:\n')
            for log in sorted(problem_logs, key=lambda l: l.split(',')[0]):  # 시간순 정렬
                f.write(f'  - {log}\n')
        else:
            f.write('- 심각한 문제 로그는 발견되지 않았습니다.\n')

        f.write('\n## 사고 관련 로그 (시간 역순)\n\n')
        if accident_logs:
            for log in accident_logs:
                f.write(f'- {log}\n')
        else:
            f.write('사고 관련 로그가 없습니다.\n')

    # 문제 로그 파일 작성 (problem_logs.md)
    with open(problem_output, 'w', encoding='utf-8') as f:
        f.write('#  문제 로그 모음\n\n')
        if problem_logs:
            for log in problem_logs:
                f.write(f'- {log}\n')
        else:
            f.write('문제 로그가 없습니다.\n')

    print(f' 사고 보고서 생성 완료: {output}')
    print(f' 문제 로그 저장 완료: {problem_output}')

except FileNotFoundError:
    print(' 로그 파일을 찾을 수 없습니다.')
except Exception as e:
    print(' 오류 발생:', e)
