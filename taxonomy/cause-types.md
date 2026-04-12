# Cause Type Taxonomy

AWS 보안 침해 사례의 원인 유형 분류 체계입니다.

---

## 분류 코드

### CRED_EXPOSURE - 자격증명 노출
AWS Access Key, Secret Key, 토큰 등이 외부에 노출된 경우.
- 소스코드 하드코딩
- GitHub/GitLab 등 VCS 유출
- 환경변수 로그 노출
- 퍼블릭 AMI/스냅샷에 포함

### S3_MISCONFIG - S3 오설정
S3 버킷의 잘못된 접근 제어로 인한 데이터 노출.
- Public ACL / Bucket Policy
- 퍼블릭 접근 차단(Block Public Access) 미설정
- Amazon S3 Files ClientRootAccess 오남용
- 잘못된 CORS 설정

### IAM_ESCALATION - IAM 권한 문제
과도한 IAM 권한 부여 또는 권한 상승 경로 악용.
- *:* 와일드카드 정책
- AssumeRole 남용
- PassRole 권한 오남용
- 미사용 IAM 사용자/키 방치

### SSRF_IMDS - SSRF + IMDSv1 메타데이터 탈취
서버사이드 요청 위조(SSRF)로 EC2 인스턴스 메타데이터 서비스(IMDS) 접근.
- http://169.254.169.254/ 탈취
- IMDSv2 미적용 환경
- WAF/네트워크 제어 부재

### SUPPLY_CHAIN - 공급망 침해
서드파티 라이브러리, SaaS, 오픈소스 컴포넌트를 통한 침해.
- 악성 npm/PyPI 패키지
- 서드파티 스크립트 탈취 (Magecart 유형)
- CI/CD 파이프라인 침해

### LOGGING_ABSENT - 로깅/모니터링 미설정
CloudTrail, VPC Flow Logs, Config 등 감사 로그 부재로 탐지 실패.
- CloudTrail 비활성화
- GuardDuty 미사용
- 로그 보존 기간 미설정

### RANSOMWARE - 랜섬웨어/데이터 파괴
S3, RDS, EC2 등의 데이터 암호화 또는 삭제.
- S3 객체 삭제/버전 관리 미적용
- RDS 스냅샷 삭제
- EC2 볼륨 암호화 후 키 삭제

### INSIDER - 내부자 위협
직원/계약자/전직 직원에 의한 의도적 침해.

### OTHER - 기타
위 분류에 해당하지 않는 사례.

---

## 복합 원인

하나의 사고가 여러 원인을 포함할 경우 cause_type 에 / 로 구분하여 기재합니다.
예: SSRF_IMDS / IAM_ESCALATION

주요 원인을 앞에 기재합니다.
