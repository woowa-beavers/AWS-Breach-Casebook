---
title: 'Kaspersky 서드파티 AWS SES 토큰 탈취 및 피싱 악용 사고 분석'
year: 2021
date: 2021-11-01
cause_type: CREDENTIAL_EXPOSURE
services:
  - IAM
  - SES
severity: High
attacker_type: Unknown
records_exposed: '직접적인 침해, 피해는 발생하지 않음'
financial_impact: '브랜드 신뢰도 하락'
ref:
  - "[BleepingComputer, Kaspersky's stolen Amazon SES token used in Office 365 phishing]"
  - '[보안뉴스, 카스퍼스키가 도난당한 아마존 SES 토큰, 피싱 공격에 활용돼]'
---

## 개요

본 사고는 2021년 11월, 글로벌 보안 기업 카스퍼스키(Kaspersky)의 미래 예측 프로젝트 웹사이트(2050.earth)를 운영하는 서드파티 인프라에서 AWS SES(Amazon Simple Email Service) 토큰이 유출된 클라우드 자격 증명 노출 사고이다. 공격자는 탈취한 토큰을 이용해 카스퍼스키 공식 도메인으로 위장한 피싱 메일을 발송하였으며, 이는 정상적인 클라우드 인프라를 공격 도구로 전환하여 기존 보안 필터를 우회한 전형적인 LoC(Living-off-the-Cloud) 공격이다.

## 타임라인

| 날짜            | 내용                                                                                                                                            |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| 2021-10 하순    | 보안 연구원들이 카스퍼스키 공식 도메인(`noreply@sm.kaspersky.com`)에서 발송되는 악성 피싱 이메일 캠페인 최초 발견                               |
| 2021-10 ~ 11 초 | 공격자들이 다크웹 피싱 키트(lamtheboss, MIRCBOOT 등)에 탈취한 AWS SES 토큰을 연동하여 Office 365 계정 탈취용 피싱 메일 대량 발송                |
| 2021-11-01      | BleepingComputer 등 주요 외신을 통해 카스퍼스키의 도난당한 AWS SES 토큰 악용 사실 공식 보도                                                     |
| 2021-11 초      | 카스퍼스키 측, 해당 토큰이 자사 내부망이 아닌 서드파티 웹사이트(2050.earth)에서 유출된 것임을 확인하고 즉시 토큰 폐기(Revoke) 및 조치 완료 발표 |

## 공격 벡터

1.  **자격 증명 노출 (Credential Exposure):** 카스퍼스키의 서드파티 계약자가 운영하는 테스트 환경(2050.earth)의 설정 오류(Misconfiguration)로 인해 AWS SES 발송 권한을 가진 자격 증명(IAM Access Key 또는 SMTP Credential)이 외부에 노출됨.
2.  **도구 확보 및 연동 (Resource Development):** 공격자는 다크웹에서 유통되는 자동화된 피싱 툴킷(lamtheboss 등)을 확보한 뒤, 탈취한 AWS SES 토큰을 시스템에 연동.
3.  **보안 우회 및 발송 (Living-off-the-Cloud & Evasion):** 정상적인 카스퍼스키의 AWS SES 인프라를 통해 메일을 발송했기 때문에 이메일 인증 체계(SPF, DKIM) 및 수신 측 스팸 필터를 무사히 통과하여 신뢰된 발신자로 인식됨.
4.  **피싱 및 크리덴셜 탈취 (Phishing & Credential Access):** 피해자들에게 '부재중 팩스 알림' 등으로 위장한 메일을 발송하고, 본문의 악성 링크 클릭 시 가짜 Office 365 로그인 페이지로 유도하여 계정 정보를 탈취하려 시도.

## 피해 범위

- **브랜드 신뢰도 악용:** 카스퍼스키의 신뢰할 수 있는 공식 도메인이 피싱 메일 발송에 악용되어 브랜드 이미지에 타격 발생.
- **자격 증명 탈취:** 이메일을 수신한 불특정 다수 사용자를 대상으로 대규모 Microsoft Office 365 자격 증명 탈취 시도.
- **내부망 보안 (영향 없음):** 해당 토큰은 서드파티에 한정된 권한만 가지고 있어 카스퍼스키 내부망 및 고객 데이터베이스에 대한 직접적인 침해는 발생하지 않음.

## 근본 원인

1.  **서드파티 인프라 설정 오류 및 관리 부실**: 외부 협력사가 운영하는 테스트 환경의 설정 오류로 클라우드 자격 증명이 노출되었으며, 원청(카스퍼스키) 차원의 보안 감사 및 통제가 이루어지지 않아 위협에 무방비로 노출됨.
2.  **최소 권한의 원칙 미적용:** 테스트용으로 발급된 클라우드 자격 증명에 발송량 제한이나 IP 접근 제어와 같은 세부적인 안전장치(Guardrails)가 부족했음.

## 대응 및 패치

- **자격 증명 무효화 (Revoke):** 유출 사실 확인 즉시 해당 AWS SES 발송 자격 증명(IAM Access Key 및 SMTP Credential)을 폐기하여 추가 발송 차단.
- **영향도 파악 및 로그 분석:** 유출된 토큰으로 발송된 피싱 메일 건수와 대상자를 파악하고 관련 내용 공지.
- **인프라 보안 강화:** 해당 서드파티 웹사이트의 설정 오류 취약점을 식별하고 보안 패치 및 조치 완료.

## MITRE ATT&CK

| Tactic (전술)                                                | Technique ID | Technique Name (기법명)                     | Procedure (구체적 행위 및 증거)                                                              |
| :----------------------------------------------------------- | :----------- | :------------------------------------------ | :------------------------------------------------------------------------------------------- |
| **Resource Development (자원 개발)**                         | T1588        | Obtain Capabilities                         | 다크웹 등에서 유통되는 피싱 키트(lamtheboss 등)를 획득하여 공격 인프라로 활용                |
| **Credential Access (크리덴셜 접근)**                        | T1552.001    | Unsecured Credentials: Credentials In Files | 서드파티 테스트 환경 및 파일 내에 잘못된 설정으로 노출된 AWS SES 자격 증명 탈취              |
| **Initial Access / Defense Evasion (초기 침투 / 방어 회피)** | T1078.004    | Valid Accounts: Cloud Accounts              | 탈취한 정상 AWS SES 계정을 사용하여 기존 이메일 보안 필터를 우회하고 합법적인 메일 발송 수행 |
| **Initial Access (초기 침투)**                               | T1566.002    | Phishing: Spearphishing Link                | '부재중 팩스 알림' 등으로 위장하여 악성 링크가 포함된 피싱 메일을 불특정 다수에게 대량 발송  |
| **Credential Access (크리덴셜 접근)**                        | T1056        | Input Capture                               | 피해자를 가짜 Office 365 로그인 페이지로 유도하여 입력되는 자격 증명(ID/Password) 수집       |

## 교훈 및 완화 방안

- **서드파티 위험 관리(TPRM) 강화:** 외부 협력사나 벤더사에 클라우드 자격 증명을 제공할 경우, 주기적인 보안 감사와 인프라 설정 모니터링이 필수적임.
- **클라우드 IAM 최소 권한의 원칙(PoLP) 적용:** 이벤트 및 테스트용으로 발급되는 API 토큰은 반드시 발송량 제한(Rate Limit), 접근 가능 IP 제한, 엄격한 IAM 권한 축소를 적용해야 함.
- **주기적인 크리덴셜 교체(Rotation):** 사용하지 않거나 방치된 클라우드 자격 증명은 정기적으로 회전 및 폐기하여 유출되더라도 즉각적인 피해로 이어지지 않도록 예방.
- **이상 징후 모니터링:** 평소와 다른 과도한 이메일 발송 트래픽이나 비정상적인 템플릿 사용이 발생할 경우 즉시 탐지할 수 있도록 AWS CloudTrail 및 SES 지표 모니터링 활성화.

## 참고 링크

- [Kaspersky Knowledge Base, Phishing advisory issued on November 1, 2021](https://support.kaspersky.com/vulnerability/list-of-advisories/12430#01112021_phishing)
- [BleepingComputer, Kaspersky's stolen Amazon SES token used in Office 365 phishing](https://www.bleepingcomputer.com/news/security/kasperskys-stolen-amazon-ses-token-used-in-office-365-phishing/)
- [Cyber News Group, Office 365 Phishing Campaign – Uses Kaspersky’s Amazon SES Token!](https://cybernewsgroup.co.uk/office-365-phishing-campaign-uses-kasperskys-amazon-ses-token/)
- [보안뉴스, 카스퍼스키가 도난당한 아마존 SES 토큰, 피싱 공격에 활용돼](https://www.boannews.com/media/view.asp?idx=102146)
