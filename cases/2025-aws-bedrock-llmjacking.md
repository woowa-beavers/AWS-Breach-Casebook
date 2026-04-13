---
title: "퍼블릭 S3 자격증명 노출을 통한 AWS Bedrock LLMjacking 침해사고 분석"
year: 2025
date: 2025-11-28
cause_type: CRED_EXPOSURE
services: [S3, Lambda, Bedrock, IAM, EC2, CloudTrail, GuardDuty]
severity: Critical
attacker_type: Unknown (세르비아어 기반 악성 스크립트 사용 위협 조직)
records_exposed: 0
financial_impact: Denial of Wallet (고비용 AI 모델 호출 및 GPU 인프라 과금)
ref:
  - https://sysdig.com/blog/ai-assisted-cloud-intrusion-achieves-admin-access-in-8-minutes/
  - https://sysdig.com/blog/what-is-llmjacking/
---

## 목차

- [1. 개요](#1-개요)
  - [1.1 사고 배경](#11-사고-배경)
  - [1.2 사고 요약](#12-사고-요약)
- [2. 공격 분석](#2-공격-분석)
  - [2.1 공격 흐름 (Attack Flow & Timeline)](#21-공격-흐름-attack-flow--timeline)
  - [2.2 단계별 공격 프로세스](#22-단계별-공격-프로세스)
  - [2.3 Attacker TTPs (MITRE ATT&CK 매핑)](#23-attacker-ttps-mitre-attck-매핑)
- [3. 대응 방안](#3-대응-방안)
  - [3.1 즉각 대응 절차](#31-즉각-대응-절차)
  - [3.2 사후 조치 및 재발 방지](#32-사후-조치-및-재발-방지)
- [참고 자료](#참고-자료)

---

## **1. 개요**

### **1.1 사고 배경**

 2025년 11월, 방치된 클라우드 자격 증명과 **AI(LLM) 자동화 기술이 결합한 신종 클라우드 침해사고**가 발생했다. 위협 행위자는 피해 기업이 자체 AI 챗봇의 검색 증강 생성(RAG) 데이터를 저장하기 위해 구축한 퍼블릭 S3 버킷에서 하드코딩된 AWS 자격 증명을 탈취했다. 이 사고는 AI의 지원을 받아 단 **8분 만에** 최고 관리자 권한을 획득하고, 데이터 탈취가 아닌 고비용 AI 모델 무단 사용(LLMjacking)을 목적으로 했다는 점에서 클라우드 위협 모델의 패러다임 변화를 시사한다.

### **1.2 사고 요약**

| 항목 | 내용 |
| --- | --- |
| 발생 시기 | 2025년 11월 28일 (Sysdig TRT 공식 보고) |
| 발견 주체 | Sysdig Threat Research Team (TRT) |
| 위협 행위자 | 미상의 사이버 위협 조직 (세르비아어 주석 스크립트 사용) |
| 침해 경로 | 퍼블릭 S3 내 RAG 설정 파일에 노출된 IAM Access Key 악용 |
| 핵심 기법 | `lambda:UpdateFunctionCode` 권한 악용 및 크로스 리전 추론(Cross-Region Inference)을 통한 탐지 우회 |
| 피해 범위 | Amazon Bedrock 무단 호출(13회) 및 p4d.24xlarge GPU 인스턴스 무단 실행에 따른 과금 폭탄 (Denial of Wallet) |
| 근본 원인 | 정적 자격 증명 관리 부재 + Lambda 실행 역할 최소 권한 원칙 위배 + Bedrock 모니터링/로깅 미비 |

---

## **2. 공격 분석**

### **2.1 공격 흐름 (Attack Flow & Timeline)**

 클라우드 트레일(CloudTrail) 분석 결과, 최초 침투부터 공격 종료까지 약 2시간이 소요되었으며 그 속도는 전례 없이 빨랐다.

* **0:00:00 (초기 침투)**: S3에서 탈취한 IAM 사용자 자격 증명으로 최초 접근
* **0:06:00 (정찰)**: 다수의 관리자 역할 전환 실패 후 특정 역할(`account`) 전환 성공
* **0:08:00 (권한 상승)**: 과도한 권한이 부여된 Lambda 함수 코드 조작 → 최고 관리자 권한 획득
* **0:11:00 (지속성 확보)**: `frickbackdoor-admin` 등 백도어 계정 생성
* **0:58:00 (LLMjacking 시작)**: Claude, Amazon Nova 등 파운데이션 모델 무단 호출
* **1:42:00 (자원 하이재킹)**: p4d.24xlarge 고성능 GPU 인스턴스 실행 성공
* **1:51:00 (공격 종료)**: 관리자에 의한 접근 차단 조치

### **2.2 단계별 공격 프로세스**

1. **초기 접근 및 탐색 (Initial Access & Reconnaissance)**

 공격자는 AI 관련 리소스를 타깃으로 `rag`, `ai`, `chatbot` 등의 일반적인 명명 규칙을 활용해 정찰을 수행했다. 그 결과, 퍼블릭 S3 버킷에 저장된 챗봇 설정 파일 내에서 평문으로 된 AWS Access Key와 Secret Key를 탈취하여 환경에 침투했다. 이후 총 19개의 서로 다른 AWS 보안 주체(Principals) 간에 역할을 전환하며 내부망을 은밀하게 탐색했다.

2. **서버리스 코드 주입을 통한 권한 상승 (Privilege Escalation via Lambda)**

 정찰 중 `lambda:UpdateFunctionCode`와 같이 과도한 IAM 권한이 부여된 Lambda 실행 역할을 발견했다. 공격자는 이를 악용해 기존 코드를 세르비아어가 포함된 악성 파이썬 스크립트로 덮어썼으며, 이 스크립트가 실행되면서 단 8분 만에 자신에게 최고 관리자 정책(AdministratorAccess)을 할당했다.

> **※ AI 자동화 공격의 결정적 증거 (Hallucination)**: 공격자가 주입한 악성 코드 내부에는 존재하지 않는 GitHub 저장소(`anthropic/training-scripts.git`)를 클론하려는 시도가 포함되어 있었다. 이는 위협 행위자가 LLM을 활용해 실시간으로 공격 코드를 생성하는 과정에서 발생한 'AI 환각' 현상으로, 이번 공격이 자동화된 AI의 지원을 받았음을 명백히 증명한다.

3. **탐지 우회 및 LLMjacking (Defense Evasion & Impact)**

 최고 권한을 얻은 공격자는 단일 리전 임계치 기반의 보안 알람을 피하기 위해 AWS의 **크로스 리전 추론(Cross-Region Inference)** 기능을 악용했다. 트래픽을 전 세계 리전으로 교묘히 분산시켰으며, 사전에 `bedrock:GetModelInvocationLoggingConfiguration` API를 호출해 로깅 비활성화 상태를 확인하는 치밀함을 보였다. 이후 막대한 비용의 AI 모델과 GPU 연산 자원을 탈취했다.

### **2.3 Attacker TTPs (MITRE ATT&CK 매핑)**

| **전술 (Tactic)** | **기법 ID** | **기법 (Technique)** | **설명** |
| --- | --- | --- | --- |
| **Initial Access** | T1078.004 | Valid Accounts: Cloud | 퍼블릭 S3 버킷에 노출된 IAM Access Key 탈취 |
| **Execution** | T1648 | Serverless Execution | `UpdateFunctionCode`를 통한 람다 내 악성 스크립트 주입 및 실행 |
| **Persistence** | T1136.003 | Create Account: Cloud | 최고 권한을 지닌 백도어 IAM 사용자(`frickbackdoor-admin`) 생성 |
| **Privilege Escalation** | T1548 | Abuse Elevation Control | 과도한 권한의 Lambda 실행 역할을 악용해 관리자 권한 즉각 확보 |
| **Defense Evasion**| T1562.001 | Impair Defenses | 크로스 리전 추론으로 트래픽을 분산시켜 임계치 기반 탐지 우회 |
| **Discovery** | T1526 | Cloud Service Discovery | Bedrock 모델 목록(`ListFoundationModels`) 및 고비용 자원 열거 |
| **Lateral Movement** | T1550 | Use Alternate Auth | 19개의 보안 주체(Principals) 간 역할 전환(AssumeRole) 수행 |
| **Impact** | T1496 | Resource Hijacking | Bedrock 모델 무단 호출(LLMjacking) 및 GPU 인스턴스 하이재킹 |

---

## **3. 대응 방안**

### **3.1 즉각 대응 절차**

**[1단계] 위협 식별 및 차단**
 노출된 초기 Access Key를 즉시 비활성화(`Inactive`) 및 삭제하고, CloudTrail을 분석하여 공격자가 생성한 백도어 계정(`frickbackdoor-admin` 등)과 탈취한 세션을 모두 강제 종료한다.

**[2단계] 악성 리소스 정리**
 공격자에 의해 수정된 Lambda 함수의 코드를 파악하여 복원하거나 격리하고, 비정상적으로 생성된 고성능 GPU 인스턴스(p4d 등)를 즉시 중지(Stop) 또는 종료(Terminate)하여 과금을 방지한다.

### **3.2 사후 조치 및 재발 방지**

1. **최소 권한의 원칙 (PoLP) 엄격 적용**
 Lambda 함수의 실행 역할에서 `iam:*`, `lambda:UpdateFunctionCode`, `iam:PassRole`과 같은 파괴적인 권한을 제거해야 한다. IAM Access Analyzer를 활용해 미사용 권한을 정기적으로 회수한다.

2. **정적 자격 증명 하드코딩 근절**
 소스 코드나 설정 파일(.properties, .env 등)에 AWS Key를 하드코딩하는 것을 금지한다. 워크로드에는 IAM Role 기반의 임시 자격 증명(STS)을 사용하고, 중요 데이터는 AWS Secrets Manager를 통해 안전하게 관리해야 한다.

3. **서비스 제어 정책(SCP)을 통한 가드레일 구축**
 크로스 리전 추론 기능을 무분별하게 악용하지 못하도록, 조직(Organizations) 레벨에서 기업이 사용하지 않는 해외 리전의 모든 API 호출을 차단(`Deny`)하는 SCP를 적용해야 한다.

4. **AI 워크로드 전용 모니터링 활성화**
 Amazon Bedrock의 **Model Invocation Logging**을 반드시 활성화하여 프롬프트와 응답 데이터를 S3 또는 CloudWatch에 기록해야 한다. 더불어 AWS Budgets 및 CloudWatch Billing Alarm을 설정해 AI 자원 요금이 비정상적으로 치솟을 때(Denial of Wallet 징후) 담당자에게 즉시 알람이 발생하도록 구성한다.

---

## **참고 자료**

- **Sysdig TRT (2026.02)**: AI-assisted cloud intrusion achieves admin access in 8 minutes — https://sysdig.com/blog/ai-assisted-cloud-intrusion-achieves-admin-access-in-8-minutes/
- **Sysdig**: What is LLMjacking? — https://sysdig.com/blog/what-is-llmjacking/
- **MITRE ATT&CK**: T1078.004, T1648, T1548, T1496 — https://attack.mitre.org/