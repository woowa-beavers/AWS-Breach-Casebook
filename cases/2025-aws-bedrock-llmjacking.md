---
title: "퍼블릭 S3 자격증명 노출을 통한 AWS Bedrock LLMjacking 침해사고 분석"
year: 2025
date: 2025-11-28
cause_type: [CRED_EXPOSURE, S3_MISCONFIG, IAM_ESCALATION]
services: [S3, Lambda, Bedrock, IAM, EC2]
severity: Critical
[cite_start]attacker_type: Unknown (세르비아어 기반 악성 스크립트 사용 위협 조직) [cite: 1]
[cite_start]records_exposed: N/A (연산 자원 및 AI 모델 무단 사용) [cite: 1]
[cite_start]financial_impact: Denial of Wallet (고비용 AI 모델 호출 및 GPU 인프라 과금) [cite: 1]
ref:
  - [Sysdig, AI-assisted cloud intrusion achieves admin access in 8 minutes](https://sysdig.com/blog/ai-assisted-cloud-intrusion-achieves-admin-access-in-8-minutes/)
  - [Sysdig, What is LLMjacking?](https://sysdig.com/blog/what-is-llmjacking/)
---

## 개요
[cite_start]본 사고는 RAG(검색 증강 생성) 데이터 저장용 퍼블릭 S3 버킷에 방치된 자격 증명이 노출되면서 발생했다[cite: 1]. [cite_start]공격자는 탈취한 키로 초기 침투 후, AI 자동화를 통해 단 8분 만에 최고 관리자(Admin) 권한을 획득했으며, 최종적으로 고비용 AI 모델을 무단 사용하는 'LLMjacking' 및 GPU 자원 하이재킹을 수행했다[cite: 1].

## 타임라인 (Speed of Execution)
| 시간 (상대) | 내용 |
|------|------|
| 0:00:00 | [cite_start]퍼블릭 S3에서 탈취한 IAM 자격 증명으로 최초 접근 [cite: 1] |
| 0:06:00 | [cite_start]초기 정찰 및 특정 역할(`account`) 전환 성공 [cite: 1] |
| 0:08:00 | [cite_start]**권한 상승**: 과도한 권한의 Lambda 함수 코드 조작을 통해 Admin 권한 확보 [cite: 1] |
| 0:11:00 | [cite_start]**지속성 확보**: `frickbackdoor-admin` 백도어 계정 생성 및 관리자 정책 부여 [cite: 1] |
| 0:58:00 | [cite_start]**LLMjacking**: Claude, Nova 등 Bedrock 모델 13회 무단 호출 시작 [cite: 1] |
| 1:05:00 | [cite_start]SSM, Secrets Manager, RDS 등 주요 서비스 대상 광범위 내부 정보 수집 [cite: 1] |
| 1:42:00 | [cite_start]**자원 하이재킹**: `p4d.24xlarge` GPU 인스턴스 실행 성공 [cite: 1] |
| 1:51:00 | [cite_start]위협 행위자 차단 및 약 2시간의 공격 종료 [cite: 1] |

## 공격 벡터
1. [cite_start]**초기 침투 (Initial Access):** AI 챗봇의 RAG 데이터 저장용 퍼블릭 S3 버킷에서 평문으로 기록된 AWS 자격 증명(Access Key) 탈취[cite: 1].
2. [cite_start]**권한 상승 (Privilege Escalation):** `lambda:UpdateFunctionCode` 권한이 부여된 Lambda 실행 역할을 발견하고, 악성 파이썬 스크립트를 주입하여 Admin 권한 획득[cite: 1].
3. [cite_start]**방어 회피 (Defense Evasion):** '크로스 리전 추론(Cross-Region Inference)' 기능을 악용하여 전 세계 여러 리전으로 트래픽을 분산, 탐지 시스템의 임계치를 우회[cite: 1].
4. [cite_start]**지속성 유지 (Persistence):** 최고 관리자 권한을 가진 백도어 계정 생성 및 JupyterLab 서버 실행을 통한 이중 백도어 구축[cite: 1].

## 피해 범위
* [cite_start]**AI 자원 탈취:** Claude 3, DeepSeek R1, Amazon Nova 등 고비용 LLM 모델 무단 호출[cite: 1].
* [cite_start]**인프라 비용:** `p4d.24xlarge` 등 고성능 GPU 인스턴스 무단 실행에 따른 막대한 클라우드 요금 발생(Denial of Wallet)[cite: 1].
* [cite_start]**정보 유출:** Secrets Manager, RDS, SSM 내 설정 정보 및 내부 데이터 정찰 활동 수행[cite: 1].

## 근본 원인
1. [cite_start]**자격 증명 관리 정책 부재:** 관리 편의를 위해 자격 증명을 평문 설정 파일에 기록하여 퍼블릭 버킷에 방치[cite: 1].
2. [cite_start]**과도한 권한 부여:** Lambda 실행 역할에 `iam:*` 등 서비스 목적을 넘어서는 관리자급 권한 부여(최소 권한 원칙 위배)[cite: 1].
3. [cite_start]**AI 서비스 가드레일 부재:** Bedrock 모델 호출 로깅 미활성화 및 미사용 리전에 대한 SCP 차단 미적용[cite: 1].

## MITRE ATT&CK
| Tactic (전술) | Technique ID | Technique Name (기법명) | Procedure (구체적 행위 및 증거) |
| :--- | :--- | :--- | :--- |
| **Initial Access** | T1078.004 | Valid Accounts: Cloud Accounts | [cite_start]S3 버킷에 노출된 키로 초기 침투 [cite: 1] |
| **Execution** | T1648 | Serverless Execution | [cite_start]Lambda 함수에 악성 스크립트 주입 및 실행 [cite: 1] |
| **Persistence** | T1136.003 | Create Account: Cloud Account | [cite_start]`frickbackdoor-admin` 백도어 계정 생성 [cite: 1] |
| **Privilege Escalation**| T1548 | Abuse Elevation Control | [cite_start]과도한 권한의 Lambda 역할을 악용해 8분 만에 권한 상승 [cite: 1] |
| **Defense Evasion** | T1562.001 | Impair Defenses | [cite_start]크로스 리전 추론으로 임계치 기반 탐지 우회 [cite: 1] |
| **Discovery** | T1526 | Cloud Service Discovery | [cite_start]Bedrock 모델 목록 및 GPU 인스턴스 가용성 정찰 [cite: 1] |
| **Impact** | T1496 | Resource Hijacking | [cite_start]Bedrock 모델 무단 호출 및 고성능 GPU 인스턴스 실행 [cite: 1] |

## 교훈 및 완화 방안
* [cite_start]**정적 키 사용 금지:** IAM Role 및 임시 자격 증명(STS) 기반 접근 방식을 채택하고, Secrets Manager를 통해 비밀 정보 관리[cite: 1].
* [cite_start]**런타임 보안 강화:** Lambda 함수의 권한에서 `UpdateFunctionCode` 등 위험 API를 제거하고 최소 권한 원칙(PoLP) 준수[cite: 1].
* [cite_start]**AI 모델 가드레일 구축:** Bedrock 'Model Invocation Logging'을 활성화하여 프롬프트 및 응답 데이터 가시성 확보[cite: 1].
* [cite_start]**전역 가드레일 적용:** SCP를 통해 사용하지 않는 리전의 API 호출을 차단하여 '크로스 리전 추론' 악용 원천 차단[cite: 1].

## 참고 링크
* [cite_start][Sysdig TRT 공식 보고서: AI-assisted cloud intrusion](https://sysdig.com/blog/ai-assisted-cloud-intrusion-achieves-admin-access-in-8-minutes/) [cite: 1]
* [cite_start][AWS Bedrock LLMjacking 분석 가이드](https://sysdig.com/blog/what-is-llmjacking/) [cite: 1]