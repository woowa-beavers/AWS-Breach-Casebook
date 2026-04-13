---
title: "베트남 핀테크(암호화폐 거래소) 플랫폼 ONUS의 Log4Shell 침해사고 분석"
year: 2021
date: 2021-12-11
cause_type: IAM_ESCALATION
services: [IAM, S3, EC2]
severity: Critical
attacker_type: Unknown (해킹 포럼 'vndcio' 계정 사용자)
records_exposed: 약 200만 명
financial_impact: 500만 달러(약 60억 원) 랜섬 요구 (지불 거절)
ref:

  - [CyStack, The attack on ONUS – A real-life case of the Log4Shell vulnerability](https://cystack.net/vi/research/the-attack-on-onus-a-real-life-case-of-the-log4shell-vulnerability)
  - [BleepingComputer, Fintech firm hit by Log4j hack refuses to pay $5 million ransom](https://www.bleepingcomputer.com/news/security/fintech-firm-hit-by-log4j-hack-refuses-to-pay-5-million-ransom/)
---

## 개요

본 사고는 2021년 발생한 Log4Shell(CVE-2021-44228) 취약점을 통해 서드파티 솔루션 서버가 장악된 후, 내부 파일에 노출된 과도한 권한의 AWS 자격 증명을 이용해 약 200만 명의 고객 데이터를 유출 및 삭제한 공급망 및 클라우드 설정 오류 복합 사고이다.

## 타임라인

| 날짜 | 내용 |
|------|------|
| 2021-12-09 | Log4Shell(CVE-2021-44228) 취약점 전 세계 최초 공개 |
| 2021-12-11 \~ 13 | 공격자가 ONUS의 Cyclos 샌드박스 서버 스캔 및 Log4Shell 악용, 백도어(kworker) 설치 |
| 2021-12-14 | 서드파티 제조사(Cyclos)의 패치 권고에 따라 ONUS가 패치를 적용했으나 이미 침해된 상태 |
| 2021-12-23 | ONUS와 보안 파트너사(CyStack)가 S3 데이터 삭제 확인 및 사고 대응 시작 (Access Key 비활성화) |
| 2021-12-24 | 공격자가 텔레그램을 통해 500만 달러의 랜섬 요구, ONUS는 이를 거절하고 고객 공지 |
| 2021-12-25 | 공격자가 해킹 포럼(RaidForums)에 200만 명의 고객 데이터 판매 게시글 업로드 |
| 2021-12-28 | 연구원(Wjbuboyz)에 의해 추가적인 S3 구성 취약점 발견 및 조치 |

## 공격 벡터

1.  **초기 침투 (Initial Access):** ONUS가 사용 중인 서드파티 결제 솔루션 'Cyclos'의 샌드박스 서버에서 Log4Shell 취약점을 악용하여 원격 코드 실행(RCE) 성공.
2.  **지속성 유지 (Persistence):** Golang 기반의 'kworker' 백도어를 설치하고 SSH/SOCKS 터널을 구축하여 외부 C\&C 서버와 연결.
3.  **권한 탈취 (Privilege Escalation):** 침투한 서버 내 설정 파일(`cyclos.properties`) 및 백업 스크립트에서 평문으로 하드코딩된 AWS Access Key를 탈취.
4.  **측면 이동 및 유출 (Lateral Movement & Exfiltration):** 탈취한 키가 `AmazonS3FullAccess` 권한을 가지고 있어 이를 이용해 프로덕션 S3 버킷에 접근, 데이터를 유출한 후 원본 삭제.

## 피해 범위

  * **노출 데이터:** 약 200만 명의 고객 개인정보 (이름, 이메일, 전화번호, 주소, 암호화된 비밀번호, 거래 내역 등).
  * **KYC 데이터:** 비대면 실명확인(E-KYC)을 위해 제출된 신분증, 여권 사진 및 얼굴 인증 비디오 셀카 클립.
  * **서비스 영향:** 프로덕션 환경의 S3 버킷 데이터가 삭제되어 서비스 운영에 차질 발생 및 대규모 랜섬 협박.

## 근본 원인

1.  **공급망 취약점 관리 미흡:** 내부 시스템이 아닌 서드파티 솔루션(Cyclos)에 포함된 라이브러리 취약점에 대한 즉각적인 대응 실패.
2.  **자격 증명 노출:** 소스코드 및 설정 파일 내에 AWS Access Key를 평문으로 하드코딩하여 관리.
3.  **권한 설정 오류 (Misconfiguration):** 테스트용 샌드박스 서버에 프로덕션 데이터에 접근할 수 있는 `AmazonS3FullAccess`라는 과도한 권한 부여 (최소 권한 원칙 위배).
4.  **환경 분리 미비:** 개발/테스트 환경과 프로덕션 환경의 권한이 엄격히 분리되지 않음.

## 대응 및 패치

  * **취약점 조치:** 취약한 Log4j 라이브러리 업데이트 및 서드파티 솔루션 패치 적용.
  * **자격 증명 무효화:** 유출된 AWS Access Key를 즉시 비활성화하고 새로운 자격 증명으로 교체.
  * **투명성 확보:** 해커의 랜섬 요구를 거절하고 고객들에게 침해 사실과 유출 범위를 투명하게 공지함.
  * **보안 강화:** 전문 보안 기업(CyStack)과 협력하여 전반적인 클라우드 인프라 진단 및 강화 작업 수행.
  
## MITRE ATT&CK
| Tactic (전술) | Technique ID | Technique Name (기법명) | Procedure (구체적 행위 및 증거) |
| :--- | :--- | :--- | :--- |
| **Initial Access (초기 침투)** | T1190 | Exploit Public-Facing Application | 서드파티 결제 솔루션(Cyclos) 샌드박스 서버의 Log4j 취약점(CVE-2021-44228) 악용<br>45.147.230.219 서버의 82번 포트로 페이로드 전송 |
| **Execution (실행)** | T1059.004 | Command and Scripting Interpreter: Unix Shell | Log4Shell의 JNDI 인젝션을 통해 악성 페이로드 실행<br>history 명령어를 통해 공격자의 쉘 명령어 실행 흔적 확인 |
| **Defense Evasion (방어 회피)** | T1036.004 | Masquerading: Task or Service | 리눅스 정상 서비스인 kworker로 위장한 백도어(Golang 1.17.2 빌드)를 다운로드 및 실행하여 탐지 우회 |
| **Command and Control (명령 및 제어)** | T1572<br>T1090 | Protocol Tunneling<br>Proxy | kworker 백도어를 통해 SSH 프로토콜(포트 81) 터널을 생성하여 C\&C 통신을 캡슐화하고 은닉함<br>연결 단절 시 백업용 SOCKS 연결 자격 증명 사용 |
| **Credential Access (크리덴셜 접근)** | T1552.001 | Unsecured Credentials: Credentials In Files | 서버 내 cyclos.properties 파일과 DB 백업 스크립트를 cat 명령어로 읽어 평문으로 저장된 AWS Access Key 및 DB 계정 정보 탈취 |
| **Privilege Escalation (권한 상승)** | T1078.004 | Valid Accounts: Cloud Accounts | 탈취한 AWS 키가 프로덕션 S3 버킷에 대한 최고 권한(AmazonS3FullAccess)을 가지고 있어 즉시 클라우드 제어권 획득 |
| **Discovery (탐색)** | T1619 | Cloud Storage Object Discovery | 확보한 권한으로 프로덕션 S3 버킷을 스캔하여 타깃 데이터(고객 DB, KYC 비디오 등) 위치 파악 |
| **Collection (수집)** | T1530 | Data from Cloud Storage | S3 버킷 내 200만 명의 개인정보, 거래 기록, E-KYC 파일(신분증 사본 등) 수집 |
| **Exfiltration (유출)** | T1567.002 | Exfiltration Over Web Service: Exfiltration to Cloud Storage | 수집된 막대한 양의 클라우드 스토리지 데이터를 공격자가 통제하는 외부 인프라로 다운로드 |
| **Impact (영향)** | T1485 | Data Destruction | 데이터 유출 후 랜섬(500만 달러) 협박을 위해 \*\*S3 원본 데이터를 삭제(파괴)\*\*하여 서비스 장애 유발 |

## 교훈 및 완화 방안

  * **최소 권한 원칙(PoLP) 준수:** IAM 권한은 반드시 필요한 수준으로만 제한하며, 관리자 권한(`FullAccess`) 부여를 지양해야 함.
  * **자격 증명 관리 강화:** 소스코드나 설정 파일에 키를 하드코딩하는 대신 AWS Secrets Manager와 같은 전문 관리 서비스를 사용해야 함.
  * **공급망 보안 및 SBOM 도입:** 사용 중인 모든 소프트웨어의 라이브러리 구성을 파악(SBOM)하고, 취약점 발생 시 즉각 대응할 수 있는 가시성을 확보해야 함.
  * **환경 격리:** 샌드박스/테스트 환경에서 프로덕션 데이터에 접근할 수 없도록 네트워크 및 IAM 레벨에서 엄격한 격리 필요.
  * **클라우드 로깅 활성화:** S3 객체 수준의 이벤트(Data Events) 로깅을 활성화하여 데이터 유출 및 삭제 행위를 즉시 탐지하고 추적할 수 있어야 함.

## 참고 링크

  * [CyStack, The attack on ONUS – A real-life case of the Log4Shell vulnerability](https://cystack.net/vi/research/the-attack-on-onus-a-real-life-case-of-the-log4shell-vulnerability)
  * [BleepingComputer, Fintech firm hit by Log4j hack refuses to pay $5 million ransom](https://www.bleepingcomputer.com/news/security/fintech-firm-hit-by-log4j-hack-refuses-to-pay-5-million-ransom/)
  * [Anomali, Anomali Cyber Watch: $5 Million Breach Extortion, APTs Using DGA Subdomains...](https://www.anomali.com/blog/anomali-cyber-watch-5-million-breach-extortion-apts-using-dga-subdomains-cyberespionage-group-incorporates-a-new-tool-and-more)
  * [StealthLabs, Crypto Firm ONUS Suffers Data Breach, Data of 2 Mn Customers Put for Sale!](https://www.stealthlabs.com/news/crypto-firm-onus-suffers-data-breach-data-of-2-mn-customers-put-for-sale/)