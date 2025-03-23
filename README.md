# 온라인 매출 데이터 수집 시스템

## 개요
이 프로젝트는 온라인 매출 데이터를 자동으로 수집하고 Supabase 데이터베이스에 저장하는 자동화 시스템입니다.

## 설치 방법

1. 레포지토리 클론
```bash
git clone https://github.com/wishcrafter/w_sales_online.git
cd w_sales_online
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
- `.env.example` 파일을 `.env`로 복사하고 필요한 정보 입력

## 사용 방법

### 1. 직접 실행
```bash
# 오늘 날짜 데이터 수집
python main.py --mode once

# 특정 기간 데이터 수집
python main.py --mode once --start-date YYYY-MM-DD --end-date YYYY-MM-DD
```

### 2. Make 웹서비스를 통한 자동화
1. Make 웹서비스에서 새 시나리오 생성
2. GitHub 앱 연결
3. Python 스크립트 실행 설정
4. Supabase 연동 설정
5. 실행 스케줄 설정

## 주요 기능
- 웹사이트 자동 로그인
- 매출 데이터 자동 수집
- Supabase 데이터베이스 저장
- 에러 처리 및 로깅

## 데이터베이스 구조

### daily_sales 테이블
- store_code: 매장 코드
- store_name: 매장명
- sales_date: 매출 날짜
- total_sales: 총 매출
- total_orders: 총 주문 수
- average_order_value: 평균 주문 금액

## 문의사항
이슈를 통해 문의해주세요.