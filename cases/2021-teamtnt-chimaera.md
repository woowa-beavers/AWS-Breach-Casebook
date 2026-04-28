---
title: 'TeamTNT Chimaera 캠페인: 클라우드 자격 증명 대량 탈취 및 자원 착취 사고 분석'
year: 2021
date: 2021-02-10
cause_type: CRED_EXPOSURE
services:
  - IAM
  - EC2
  - S3
  - Docker
  - Kubernetes
severity: High
attacker_type: TeamTNT (Cybercrime Group)
records_exposed: 약 4,000건 이상의 클라우드 자격 증명 탈취
financial_impact: '막대한 클라우드 컴퓨팅 자원 무단 점유 및 비용 발생'
ref:
  - '[LevelBlue, TeamTNT with new campaign aka Chimaera]'
  - '[Trend Micro, TeamTNT Continues Attack on the Cloud]'
---

## 개요

본 사고는 2021년 중반, 독일어권 해킹 그룹인 TeamTNT가 'Chimaera(키메라)'라는 대규모 캠페인을 통해 전 세계 클라우드 및 컨테이너 환경을 공격한 사건이다. 이들은 단순히 암호화폐 채굴에 그치지 않고, 설정이 미흡한 Docker API 및 SSH 서버를 통해 침투한 뒤 AWS, GCP, Azure 등 주요 클라우드 인프라의 자격 증명을 대량으로 수집했다. 탈취한 정보를 바탕으로 내부망에서 횡적 이동(Lateral Movement)을 수행하여 인프라 장악 범위를 기하급수적으로 넓힌 전형적인 클라우드 네이티브 공격이다.

## 타임라인

| 날짜         | 내용                                                                                          |
| :----------- | :-------------------------------------------------------------------------------------------- |
| 2021-02      | TeamTNT가 AWS 메타데이터 서비스(IMDS)를 타겟으로 자격 증명을 탈취하는 초기 스크립트 배포 시작 |
| 2021-06      | 보안 연구진(Palo Alto Networks 등)이 TeamTNT 인프라에서 'Chimaera' 스크립트 저장소 발견       |
| 2021-07      | TeamTNT, 'Chimaera' 캠페인 공식 돌입 및 자체 웹사이트를 통해 감염 통계 공개                   |
| 2021-08 ~ 09 | 글로벌 단위로 수천 건 이상의 감염 발생 확인 및 보안 업계(AT&T, Anomali 등) 분석 보고서 발표   |

## 공격 벡터

1. **초기 침투 (Initial Access):** 인터넷 스캐닝 도구(Masscan, ZGrab 등)를 사용하여 외부에 노출된 Docker API 데몬(2375, 2376 포트) 및 취약한 SSH 서버를 식별하고 초기 침투용 셸 스크립트 실행.
2. **방어 회피 및 권한 확보 (Defense Evasion):** 감염된 시스템에서 클라우드 보안 제품(Alibaba Cloud 보안 서비스 등)을 비활성화하고, `libprocesshider` 등을 사용하여 악성 프로세스를 은닉.
3. **자격 증명 대량 탈취 (Credential Access):** 'Chimaera' 툴킷에 포함된 `Lazagne` 및 자체 스크립트를 통해 `~/.aws/credentials`, SSH 키, GitHub 토큰, 클라우드 인스턴스 메타데이터(IMDS) 등을 스캐래핑하여 C&C 서버로 전송.
4. **횡적 이동 (Lateral Movement):** 탈취한 자격 증명과 SSH 키를 이용해 동일 네트워크 내의 다른 인스턴스 및 컨테이너 클러스터로 감염 확산.
5. **목적 달성 (Impact):** 장악한 인프라에 `XMRig` 암호화폐 채굴기를 설치하여 자원을 착취하고, 해당 노드를 IRC 봇넷에 편입시켜 추가 명령 대기 상태로 전환.

## 피해 범위

- **자격 증명 유출:** AWS, GCP, Azure, Docker, GitHub 등 다양한 플랫폼의 자격 증명 약 4,000건 이상 유출.
- **인프라 장악:** 약 13,000개 이상의 Docker IP 주소 및 수백 개의 컨테이너 환경이 공격 노출 범위에 포함됨.
- **자원 오남용:** 무단 크립토마이닝으로 인한 클라우드 사용 비용의 급격한 상승 및 시스템 성능 저하.

## 근본 원인

1. **클라우드 및 컨테이너 설정 미흡:** Docker API 및 SSH와 같은 관리 인터페이스가 적절한 인증이나 접근 제어 없이 인터넷에 노출됨.
2. **자격 증명 관리 부실:** 클라우드 액세스 키와 비밀번호가 시스템 내부 파일(`~/.aws/credentials` 등)에 평문으로 저장되어 있어 탈취에 취약했음.
3. **과도한 권한 설정:** 탈취된 자격 증명이 최소 권한 원칙을 무시하고 광범위한 리소스 접근 권한을 가지고 있어 횡적 이동이 용이했음.

## 대응 및 패치

- **노출 인터페이스 차단:** 인터넷에 노출된 Docker API 및 SSH 포트를 폐쇄하고, VPN 또는 상호 TLS(mTLS) 인증을 통한 접근 통제 적용.
- **자격 증명 폐기 및 교체:** 유출이 의심되는 모든 IAM 액세스 키, SSH 개인 키, API 토큰을 즉시 무효화하고 재발급.
- **인스턴스 메타데이터 보안 강화:** SSRF 공격을 통한 토큰 탈취를 방지하기 위해 IMDSv2 사용을 필수(Required)로 설정.
- **보안 모니터링 강화:** CWPP(클라우드 워크로드 보호 플랫폼)를 도입하여 비정상적인 프로세스 실행 및 자격 증명 파일 접근 행위 실시간 탐지.

## MITRE ATT&CK

| Tactic (전술)                             | Technique ID | Technique Name (기법명)                            | Procedure (구체적 행위)                                                                                            |
| :---------------------------------------- | :----------- | :------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------- |
| **Initial Access**<br>(초기 접근)         | T1190        | Exploit Public-Facing Application                  | 외부에 인증 없이 노출된 Docker API(2375 등) 및 Kubernetes 환경 악용                                                |
|                                           | T1078.004    | Valid Accounts: Cloud Accounts                     | 사전에 탈취한 클라우드 IAM 자격 증명 및 서버 계정을 사용하여 무단 접속                                             |
| **Execution**<br>(실행)                   | T1059.004    | Command and Scripting Interpreter: Unix Shell      | 초기 침투 후 악성 Bash/Shell 스크립트 실행 (리눅스 및 컨테이너 환경)                                               |
| **Defense Evasion**<br>(방어 회피)        | T1070.003    | Indicator Removal: Clear Command History           | bash history를 조작하여 명령어 기록 자체를 남기지 않거나 무력화                                                    |
|                                           | T1562.001    | Impair Defenses: Disable or Modify Tools           | 감염된 컴퓨터에서 Aegis Authenticator, Quartz 및 Alibaba 서비스 등 보안 제품을 비활성화하거나 제거                 |
| **Credential Access**<br>(자격 증명 접근) | T1552.001    | Unsecured Credentials: Credentials In Files        | `~/.aws/credentials`, `s3cfg` 등 평문으로 저장된 클라우드 키 대량 스크래핑                                         |
|                                           | T1555        | Credentials from Password Stores                   | Lazagne 등 도구를 활용해 브라우저 및 시스템 앱에 저장된 비밀번호 덤프                                              |
|                                           | T1552.005    | Unsecured Credentials: Cloud Instance Metadata API | 클라우드 인스턴스 메타데이터 서비스(IMDS)에 접근하여 임시 IAM 액세스 토큰 및 GitHub 토큰 등 탈취                   |
| **Lateral Movement**<br>(측면 이동)       | T1021.004    | Remote Services: SSH                               | 탈취한 SSH 개인 키를 활용해 내부망 내 다른 클라우드 인스턴스로 수평 확산                                           |
|                                           | T1210        | Exploitation of Remote Services                    | 내부 네트워크에서 다른 취약한 Docker/Kubernetes 노드의 API를 타겟으로 원격 서비스 악용 및 감염 전파                |
| **Command and Control**<br>(지휘 및 통제) | T1105        | Ingress Tool Transfer                              | 외부 C&C 서버로부터 Chimaera 툴킷, 크리덴셜 스틸러(Lazagne), 암호화폐 채굴기(XMRig) 등 대량의 악성 도구를 다운로드 |
|                                           | T1071.001    | Application Layer Protocol: Web Protocols          | 감염된 클라우드 인프라를 IRC 봇넷에 편입시켜 통신하고 공격자의 추가 명령 대기                                      |
| **Exfiltration**<br>(유출)                | T1041        | Exfiltration Over C2 Channel                       | 탈취한 막대한 양의 클라우드 자격 증명과 구성 데이터를 C&C 서버 채널을 통해 전송                                    |
| **Impact**<br>(영향)                      | T1496        | Resource Hijacking                                 | 장악한 클라우드 컴퓨팅 자원(CPU/메모리)을 무단으로 점유하여 모네로(Monero) 암호화폐 채굴                           |

## 교훈 및 완화 방안

- **최소 권한의 원칙(PoLP) 준수:** IAM 사용자에게는 반드시 필요한 최소한의 권한만 부여하고, 장기 자격 증명 대신 IAM 역할을 통한 임시 자격 증명 사용 권고.
- **클라우드 보안 태세 관리(CSPM):** 지속적인 스캐닝을 통해 인터넷에 노출된 포트나 잘못 설정된 S3 버킷, API 데몬 등 설정 오류를 사전에 식별하고 교정.
- **런타임 보안 실현:** 컨테이너 및 인스턴스 환경에서 발생하는 예외적인 네트워크 통신이나 파일 시스템 변경을 감시하는 행동 기반 탐지 체계 구축.
- **자격 증명 회전(Rotation):** 주요 액세스 키와 비밀번호를 정기적으로 교체하여 자격 증명이 유출되더라도 유효 기간을 최소화함으로써 피해 억제.

## 참고 링크

- [LevelBlue, TeamTNT with new campaign aka "Chimaera"](https://www.levelblue.com/blogs/spiderlabs-blog/teamtnt-with-new-campaign-aka-chimaera)
- [UNIT42, TeamTNT Actively Enumerating Cloud Environments to Infiltrate Organizations](https://unit42.paloaltonetworks.com/teamtnt-operations-cloud-environments/)
- [Trend Micro, TeamTNT Continues Attack on the Cloud, Targets AWS Credentials](https://www.trendmicro.com/en_us/research/21/c/teamtnt-continues-attack-on-the-cloud--targets-aws-credentials.html)
- [Anomali, Inside TeamTNT's Impressive Arsenal: A Look Into A TeamTNT Server](https://www.anomali.com/blog/inside-teamtnts-impressive-arsenal-a-look-into-a-teamtnt-server)
- [Trend Micro, TeamTNT Activities Probed - Credential Theft, Cryptocurrency Mining, and More](https://www.trendmicro.com/vinfo/us/security/news/cybercrime-and-digital-threats/teamtnt-activities-probed?utm_source=trendmicroresearch&utm_medium=smk&utm_campaign=0721_teamtnt)
