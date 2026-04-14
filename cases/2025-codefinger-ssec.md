---
title: "S3 SSE-C 기반 랜섬웨어 확산 (Codefinger)"
year: 2025
date: 2025-01-13
cause_type: CRED_EXPOSURE
services: [S3, IAM]
severity: Critical
attacker_type: External
records_exposed: 0
financial_impact:
ref:
  - https://www.halcyon.ai/blog/abusing-aws-native-services-ransomware-encrypting-s3-buckets-with-sse-c
  - https://www.theregister.com/2025/01/13/ransomware_crew_abuses_compromised_aws/
---

## 목차

- [1. 개요](#1-개요)
  - [1.1 사고 배경](#11-사고-배경)
  - [1.2 사고 요약](#12-사고-요약)
- [2. 공격 분석](#2-공격-분석)
  - [2.1 공격 흐름 (Attack Flow)](#21-공격-흐름-attack-flow)
  - [2.2 단계별 공격 프로세스](#22-단계별-공격-프로세스)
  - [2.3 Attacker TTPs (MITRE ATT&CK 매핑)](#23-attacker-ttps-mitre-attck-매핑)
- [3. 대응 방안](#3-대응-방안)
  - [3.1 즉각 대응 절차](#31-즉각-대응-절차)
  - [3.2 사후 조치 및 재발 방지](#32-사후-조치-및-재발-방지)
- [참고 자료](#참고-자료)

---

## **1. 개요**

### **1.1 사고 배경**

 2025년 1월, AWS S3를 대상으로 한 랜섬웨어 캠페인 **Codefinger**가 보고되었다. 기존 랜섬웨어가 파일 암호화 멀웨어에 의존하는 것과 달리, 이 공격은 SSE-C(고객 제공 키를 사용한 서버 측 암호화)와 같은 AWS 네이티브 암호화 기능 자체를 악용한다. AWS Customer Incident Response Team(CIRT)은 S3 버킷에서 비정상적인 암호화 활동이 증가하고 있음을 확인하였으며, 이 공격이 AWS 서비스 자체의 취약점이 아닌 노출된 자격증명을 악용한 침해 사고임을 밝혔다.

### **1.2 사고 요약**

| 항목 | 내용 |
| --- | --- |
| 발생 시기 | 2025년 1월 (최초 보고: 2025년 1월 13일) |
| 발견 주체 | Halcyon Research Team |
| 위협 행위자 | Codefinger |
| 침해 경로 | 탈취된 공개 AWS 자격증명 악용 → s3:GetObject / s3:PutObject / s3:PutLifecycleConfiguration 권한 악용|
| 핵심 기법 | 공격자가 생성한 AES-256 키로 S3 객체 재암호화(SSE-C) 및 7일 후 데이터를 삭제하는 수명 주기 정책 적용 |
| 피해 범위 | 피해 기업은 암호화 키 없이 데이터 접근이 불가하며 비트코인 몸값 요구를 받음 |
| 근본 원인 | 장기 IAM 자격증명 노출 + SSE-C 미제한 + S3 버전 관리 미적용 |

 Halcyon 위협 헌터들은 2024년 12월 Codefinger를 처음 발견했으며, 이후 수 주 사이 AWS를 주요 인프라로 사용하는 소프트웨어 개발사 두 곳이 피해를 입은 것을 확인했다.

---

## **2. 공격 분석**

### **2.1 공격 흐름 (Attack Flow)**

 공격은 인터넷에 노출된 IAM Access Key 획득에서 시작하여, S3 버킷 열거 → SSE-C 재암호화 → 수명 주기 정책 변경 및 랜섬 노트 삽입 → 복호화 불가 및 몸값 요구 순으로 진행된다.

### **2.2 단계별 공격 프로세스**

1. **초기 접근 및 탐색 (Initial Access & Discovery)**

 Codefinger는 공격을 시작하기 위해 피해자의 AWS 자격증명을 먼저 확보한다. 주로 GitHub 등 공개 저장소에 평문으로 노출된 AWS 키를 수집하거나, 세션 하이재킹을 통해 유효한 인증 토큰을 탈취하는 방식이 사용되었다. 자격증명을 확보한 공격자는 s3:ListObjectsV2 등의 API로 버킷과 객체를 열거하며 타깃을 선별한다.

> **※ 주의:** IAM Access Key + Secret Key는 CLI/SDK/API 전용 자격증명이다. 콘솔 로그인은 IAM User 패스워드 기반이므로, Access Key만으로는 AWS 관리 콘솔에 직접 접근할 수 없다. 공격자는 **AWS CLI 또는 SDK를 통해** 버킷을 탐색하고 공격을 수행한다.

2. **네이티브 암호화 기능 악용 (Encryption via SSE-C)**

 위협 행위자는 별도의 멀웨어 없이 AWS 네이티브 암호화 기능 자체를 무기화한다. 공격자는 먼저 로컬 환경에서 256비트 AES 키를 생성한다. 이후 피해자의 객체를 다운로드(s3:GetObject)한 뒤, x-amz-server-side-encryption-customer-algorithm 헤더에 자신이 생성한 키를 포함하여 동일한 위치에 다시 업로드(s3:PutObject)하며 원본을 덮어쓴다.

 AWS는 이 키를 사용해 AES-256 암호화를 수행하지만, 원본 키를 절대 저장하지 않는다. 향후 객체 복호화 시 키 검증을 위해 키의 HMAC(Hash-Based Message Authentication Code)을 해당 S3 객체의 메타데이터와 함께 S3 내부에 저장한다 (CloudTrail에도 원본 키는 기록되지 않고 HMAC만 남음). 이 HMAC은 원본 키를 복구하거나 데이터를 복호화하는 데 사용할 수 없으므로, 공격자의 키 없이는 데이터에 접근할 수 없게 된다.

3. **복구 차단 (Inhibit Recovery)**

 공격자는 s3:PutLifecycleConfiguration API를 통해 S3 버킷의 수명 주기 정책(Lifecycle Configuration)을 변경한다. 객체가 7일 뒤 자동 삭제되도록 보존 기간을 단축시키며, 특히 구버전 객체가 삭제되도록 유도한다. 이로 인해 S3 버전 관리를 사전 적용해둔 조직이라 할지라도 암호화 이전의 원본 데이터를 복원할 수 없게 된다.

4. **몸값 요구 (Ransom Demand)**

 피해 기업은 각 영향받은 디렉터리에서 랜섬 노트를 발견했다. 노트에는 7일 이내 Bitcoin으로 결제하지 않으면 데이터를 영구 삭제하겠다는 경고와 함께 복호화 키 제공 조건이 명시되어 있었다. Codefinger는 협상 과정에서 피해자가 계정 권한을 변경하거나 자체적인 대응 조치를 취할 경우 협상을 중단하겠다고 위협했다.

### **2.3 Attacker TTPs (MITRE ATT&CK 매핑)**

| **전술 (Tactic)** | **기법 ID** | **기법 (Technique)** | **설명** |
| --- | --- | --- | --- |
| **Reconnaissance** | T1589.001 | Gather Victim Identity Information: Credentials | GitHub 레포지터리 등 공개 저장소에서 노출된 AWS Access Key 수집 |
| **Initial Access** | T1078.004 | Valid Accounts: Cloud Accounts | 탈취된 IAM Access Key로 피해자 AWS 계정에 접근 |
| **Discovery** | T1619 | Cloud Storage Object Discovery | s3:ListObjectsV2 등 API로 S3 버킷 열거 및 공격 대상 선별 |
| **Collection** | T1530 | Data from Cloud Storage | s3:GetObject로 암호화 이전 S3 객체 조회 및 수집 |
| **Impact** | T1486 | Data Encrypted for Impact | 공격자가 생성한 키와 SSE-C를 악용해 S3 객체를 재암호화하여 데이터 접근 차단 |
| **Impact** | T1490 | Inhibit System Recovery | S3 수명 주기 정책을 단기 만료 및 삭제로 변경하여 복구 차단 |
| **Impact** | T1657 | Financial Theft / Extortion | 복호화 키를 대가로 Bitcoin 결제 요구 및 랜섬 노트 삽입 |

---

## **3. 대응 방안**

### **3.1 즉각 대응 절차**

**[1단계] 피해 범위 파악 (비정상 암호화 식별)**

 CloudTrail 로그에서 s3:PutObject 이벤트 중 x-amz-server-side-encryption-customer-algorithm 헤더가 포함된 비정상적인 요청 이력을 식별한다.

> **⚠️ 중요:** s3:GetObject, s3:PutObject와 같은 S3 데이터 플레인 작업은 **CloudTrail Management Events에는 기록되지 않는다.** 해당 이벤트를 탐지하려면 CloudTrail에서 **S3 Data Events를 별도로 활성화**해야 한다. S3 Data Events는 기본 비활성 상태이며, 활성화 전에는 SSE-C 재암호화 시도를 CloudTrail 로그로 탐지할 수 없다.

| **이벤트 유형** | **CloudTrail 유형** | **활성화 여부** |
| --- | --- | --- |
| PutBucketLifecycleConfiguration | Management Event | 기본 활성화 |
| s3:PutObject (SSE-C 재암호화) | **S3 Data Event** | **별도 활성화 필요** |
| s3:GetObject | **S3 Data Event** | **별도 활성화 필요** |

**[2단계] 자격증명 무효화**

 비정상 접근에 사용된 IAM Access Key를 비활성화하고 삭제한다. 이때 --user-name 옵션으로 대상 사용자를 명시해야 정확하게 처리된다.

```bash
# 1. 키 비활성화
aws iam update-access-key --access-key-id AKIA... --status Inactive --user-name <유저명>

# 2. 키 삭제
aws iam delete-access-key --access-key-id AKIA... --user-name <유저명>
```

**[3단계] 수명 주기 정책 복구**

 공격자가 s3:PutLifecycleConfiguration API를 통해 변경한 S3 버킷 수명 주기 정책을 확인하고 원래 상태로 되돌린다. 7일 단기 삭제 타이머가 설정된 버킷이 있다면 데이터가 영구 소실되기 전에 우선으로 처리해야 한다.

**[4단계] 복구 가능 여부 확인**

 SSE-C로 암호화된 객체는 공격자의 키 없이는 복호화할 수 없다. 단, S3 버전 관리가 사전에 활성화되어 있었고, 공격자의 수명 주기 정책 조작으로 인해 구버전이 아직 삭제되지 않았다면 암호화 이전 원본 버전이 남아 있을 수 있으므로 복원을 시도한다.

**[5단계] 외부 공유 및 보고**

 내부 CISO 및 법무팀에 보고하고, AWS Support에 사고 사실을 통보한다. AWS는 노출된 키가 탐지되면 해당 고객에게 통보하고 필요에 따라 격리 정책을 적용한다.

### **3.2 사후 조치 및 재발 방지**

1. **장기 IAM 자격증명 제거**

 이 사건의 근본 원인은 장기 IAM Access Key의 노출이다. 소스 코드나 환경 변수 파일에 정적 키를 하드코딩하는 방식을 지양하고, IAM Role 기반의 임시 자격증명(Temporary Credentials)으로 전환해야 한다.

 AWS IAM Identity Center, STS, EC2/Lambda Instance Profile 등을 활용해 애플리케이션이나 워크로드(Pod)가 실행되는 시점에 필요한 권한만 동적으로 할당받도록 구성하는 것이 권장된다. 임시 자격증명은 만료 시간이 설정되어 있어 키가 탈취되더라도 피해 범위를 제한할 수 있다. 아울러 Trufflehog, Gitleaks 등의 시크릿 스캐닝 도구를 CI/CD 파이프라인에 통합해 코드베이스 내 자격증명 노출을 사전에 차단해야 한다.

2. **SSE-C 사용 제한**

 애플리케이션이 SSE-C를 사용하지 않는다면, 버킷 정책(Bucket Policy) 또는 AWS Organizations의 리소스 제어 정책(RCP)으로 SSE-C 사용을 원천 차단해야 한다.

```json
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "s3:PutObject",
  "Resource": "arn:aws:s3:::YOUR-BUCKET/*",
  "Condition": {
    "Null": {
      "s3:x-amz-server-side-encryption-customer-algorithm": "false"
    }
  }
}
```

(※ 주석: SSE-C 요청 헤더가 존재할 경우, 즉 Null이 아닐 경우 해당 PutObject 요청을 즉각 거부(Deny)한다는 의미)

> **참고:** AWS는 2026년 4월 6일부터 모든 신규 S3 범용 버킷에 SSE-C를 기본 비활성화 정책을 적용하였다.

3. **S3 버전 관리 및 Object Lock 적용**

 버전 관리(Versioning)를 활성화하면 암호화 이전 원본 객체를 복원할 수 있다. 단, 이번 Codefinger 사례처럼 공격자가 수명 주기 정책을 변경해 구버전까지 강제 삭제할 수 있으므로 버전 관리만으로는 충분하지 않다. 따라서 S3 Object Lock(Compliance Mode)을 함께 적용해 일정 기간 동안 그 누구도 객체를 삭제하거나 덮어쓸 수 없도록 데이터를 물리적으로 보호해야 한다.

4. **지속적 모니터링 강화**

 수명 주기 정책 변경과 SSE-C 재암호화 시도를 실시간으로 탐지하기 위해 아래와 같은 아키텍처 및 알림 체계를 구성해야 한다.

- **서버리스 탐지 파이프라인 구축:** EventBridge, Lambda, Athena를 조합하여 CloudTrail 로그 내 비정상적인 암호화 및 설정 변경 이벤트를 실시간으로 추적한다.

- **Amazon GuardDuty 활성화:** GuardDuty의 S3 Protection과 Extended Threat Detection을 활성화하여 VPC Flow Logs, DNS Logs, CloudTrail 관리 이벤트(Management Events) 및 데이터 플레인 이벤트를 소스로 한 ML 기반 위협 탐지(비트코인 마이닝, 비인가 접근, IAM 이상 행위 등)를 수행한다.

| **기능** | **활성화 방법** | **모니터링 소스** |
| --- | --- | --- |
| **GuardDuty 기본 위협 탐지** | GuardDuty 활성화만으로 제공 | CloudTrail Management Events, VPC Flow Logs, Route53 DNS Query Logs |
| **Extended Threat Detection** | GuardDuty 활성화만으로 제공 (추가 설정 불필요) | 기본 소스 통합 분석 (ML 기반 이상 탐지) |
| **S3 Protection** | **별도 유료 활성화 필요** | S3 Data Plane Events 추가 모니터링 (GetObject, PutObject 등) |

*※ 이 공격에서 SSE-C 재암호화(s3:PutObject)를 GuardDuty로 탐지하려면 S3 Protection 활성화가 필요하다.*

- **핵심 이벤트 실시간 알림:** CloudWatch Metric Filter와 SNS를 조합해 다음 행위 발생 시 보안팀에 즉각 알림을 전송한다.
    - 대량의 PutObject 요청 (특히 SSE-C 헤더 포함)
    - PutBucketLifecycleConfiguration API 호출 (수명 주기 정책 조작)
    - 단일 IAM Access Key의 비정상적인 대량 사용 및 Credential Access 전술 탐지

---

## **참고 자료**

- **Halcyon Research Blog (2025.01.13):** Codefinger Ransomware Campaign Targeting AWS S3 — https://www.halcyon.ai/blog/abusing-aws-native-services-ransomware-encrypting-s3-buckets-with-sse-c
- **The Register (2025.01.13):** Ransomware crew abuses AWS native encryption — https://www.theregister.com/2025/01/13/ransomware_crew_abuses_compromised_aws/
- **DevOpsSchool:** AWS Security Operations: Object Storage — https://www.devopsschool.com/slides/aws/aws-security-operations-object-storage/index.html#/
- **HackSignal:** AWS Cloud Storage at Risk: New Ransomware Weaponizes S3 Encryption Features — https://hacksignal.com/news/aws-cloud-storage-at-risk-new-ransomware-weaponizes-s3-encryption-features/
- **MITRE ATT&CK:** T1589.001, T1078.004, T1619, T1530, T1486, T1490, T1657 — https://attack.mitre.org/
- **AWS Security Blog (2025.01.17, 업데이트 2025.03.18):** Preventing unintended encryption of Amazon S3 objects — https://aws.amazon.com/blogs/security/preventing-unintended-encryption-of-amazon-s3-objects/
- **Trend Micro (2025.01.18):** Breaking Down S3 Ransomware: Variants, Attack Paths and Trend Vision One™ Defenses — https://www.trendmicro.com/en_us/research/25/k/s3-ransomware.html
- **Panther (2025):** Detecting and Hunting for Cloud Ransomware Part 1: AWS S3 — https://panther.com/blog/detecting-and-hunting-for-cloud-ransomware-part-1-aws-s3
- **Arctic Wolf (2025):** Ransomware Campaign Encrypting Amazon S3 Buckets using SSE-C — https://arcticwolf.com/resources/blog/ransomware-campaign-encrypting-amazon-s3-buckets-using-sse-c/
- **Rewind (2025):** Codefinger: How an emerging ransomware threat exploited an AWS S3 encryption feature — https://rewind.com/blog/codefinger-how-an-emerging-ransomware-threat-exploited-an-aws-s3-encryption-feature-to-hold-data-hostage/
