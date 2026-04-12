# AWS Breach Casebook

> AWS 환경에서 발생한 실제 보안 침해 사례 아카이브 (2014-2025)

보안 사고의 원인 유형, 공격 벡터, 타임라인, 대응 방법을 체계적으로 정리하여,
클라우드 보안 엔지니어링 설계 및 침해사고 대응(IR) 시 참고 자료로 활용하기 위한 케이스북입니다.

---

## 구조

    AWS-Breach_Casebook/
    cases/                  # 사례 문서 ({year}-{slug}.md)
    data/
        breach_master.xlsx  # 전체 사례 메타데이터 (필터/분석용)
    taxonomy/
        cause-types.md      # 원인 유형 분류 체계
    scripts/                # 파싱/통계 스크립트
    README.md

---

## 케이스 파일 형식

각 케이스는 cases/{year}-{slug}.md 형태로 저장됩니다.

    cases/
    2019-capital-one.md
    2020-twilio-s3.md
    ...

파일 상단 frontmatter 예시:

    title: "Capital One Data Breach"
    year: 2019
    date: 2019-07-29
    cause_type: SSRF / IMDSv1 Abuse
    services: [EC2, S3, IAM]
    severity: Critical
    attacker_type: External
    records_exposed: 106000000

---

## 원인 유형 분류 (Cause Types)

| 코드 | 유형 |
|------|------|
| CRED_EXPOSURE | 자격증명 노출 (하드코딩, Git 유출 등) |
| S3_MISCONFIG | S3 퍼블릭 접근/ACL 오설정 |
| IAM_ESCALATION | IAM 과도한 권한/권한 상승 |
| SSRF_IMDS | SSRF + IMDSv1 메타데이터 탈취 |
| SUPPLY_CHAIN | 서드파티/오픈소스 공급망 침해 |
| LOGGING_ABSENT | CloudTrail/로깅 미설정 |
| RANSOMWARE | 랜섬웨어/데이터 삭제 |
| INSIDER | 내부자 위협 |
| OTHER | 기타 |

전체 분류 기준 -> taxonomy/cause-types.md

---

## 데이터

data/breach_master.xlsx - 전체 사례를 스프레드시트로 관리합니다.

| 컬럼 | 설명 |
|------|------|
| year | 사고 발생 연도 |
| title | 사례명 |
| cause_type | 원인 유형 코드 |
| services | 관련 AWS 서비스 |
| severity | 심각도 (Critical / High / Medium) |
| attacker_type | External / Insider / Unknown |
| records_exposed | 유출 레코드 수 |
| slug | 케이스 파일 slug |
| ref | 참고 링크 |

---

## Contributing

1. cases/ 에 {year}-{slug}.md 파일 추가
2. frontmatter 형식 준수
3. data/breach_master.xlsx 행 추가
4. PR 제출

---

*Maintained by woowa-beavers*
