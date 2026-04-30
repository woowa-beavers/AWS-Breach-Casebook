<div align="center">

<img src="https://github.com/woowa-beavers.png" width="130" />

<br/>

<sub>woowa-beavers · AWS Security Research</sub>

# AWS Breach Casebook

> 2014–2025 실제 AWS 침해사고를 MITRE ATT&CK 기반으로 분석한 케이스북

<br/>

![AWS](https://img.shields.io/badge/AWS-232F3E?style=flat-square&logo=amazonwebservices&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![MITRE ATT&CK](https://img.shields.io/badge/MITRE_ATT%26CK-E02222?style=flat-square)
![Cases](https://img.shields.io/badge/Cases-2014–2025-4A90D9?style=flat-square)

</div>

---

공격 벡터, TTP 매핑, 타임라인, 탐지·대응 전략을 체계적으로 정리한 케이스북입니다.  
클라우드 보안 설계 및 침해사고 대응(IR) 레퍼런스로 활용할 수 있습니다.

---

## 📁 구조

```
AWS-Breach_Casebook/
├── cases/                   # 사례 문서 ({year}-{slug}.md)
├── data/
│   └── breach_master.xlsx   # 전체 사례 메타데이터
├── taxonomy/
│   └── cause-types.md       # 원인 유형 분류 체계
└── scripts/                 # 파싱·통계 스크립트
```

---

## 📄 케이스 파일 형식

각 케이스는 `cases/{year}-{slug}.md` 형태로 저장됩니다.

```yaml
title: "Capital One Data Breach"
year: 2019
date: 2019-07-29
cause_type: SSRF / IMDSv1 Abuse
services: [EC2, S3, IAM]
severity: Critical
attacker_type: External
records_exposed: 106000000
```

---

## 🔖 원인 유형 분류

<div align="center">

| Code | 유형 |
|:---|:---|
| `CRED_EXPOSURE` | 자격증명 노출 (하드코딩, Git 유출 등) |
| `S3_MISCONFIG` | S3 퍼블릭 접근 / ACL 오설정 |
| `IAM_ESCALATION` | IAM 과도한 권한 / 권한 상승 |
| `SSRF_IMDS` | SSRF + IMDSv1 메타데이터 탈취 |
| `SUPPLY_CHAIN` | 서드파티 / 오픈소스 공급망 침해 |
| `LOGGING_ABSENT` | CloudTrail / 로깅 미설정 |
| `RANSOMWARE` | 랜섬웨어 / 데이터 삭제 |
| `INSIDER` | 내부자 위협 |
| `OTHER` | 기타 |

</div>

전체 분류 기준 → [`taxonomy/cause-types.md`](taxonomy/cause-types.md)

---

## 📊 데이터 스키마

`data/breach_master.xlsx` — 전체 사례를 스프레드시트로 관리합니다.

<div align="center">

| Column | Description |
|:---|:---|
| `year` | 사고 발생 연도 |
| `title` | 사례명 |
| `cause_type` | 원인 유형 코드 |
| `services` | 관련 AWS 서비스 |
| `severity` | 심각도 (Critical / High / Medium) |
| `attacker_type` | External / Insider / Unknown |
| `records_exposed` | 유출 레코드 수 |
| `slug` | 케이스 파일 slug |
| `ref` | 참고 링크 |

</div>

---

## 🤝 Contributing

1. `cases/` 에 `{year}-{slug}.md` 파일 추가
2. frontmatter 형식 준수
3. `data/breach_master.xlsx` 에 행 추가
4. PR 제출

---

<div align="center">
<sub>Maintained by <a href="https://github.com/woowa-beavers">woowa-beavers</a></sub>
</div>
