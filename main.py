import os
import asyncio
import logging
from datetime import datetime, timedelta
import argparse
from dotenv import load_dotenv
from scraper import OrderQueenScraper
from data_processor import SalesDataProcessor
from mcp_config import MCPConfig

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

async def process_sales_data(start_date: str, end_date: str):
    try:
        # 환경 변수 로드
        load_dotenv()
        
        # MCP 설정 초기화
        mcp = MCPConfig()
        supabase = mcp.get_supabase_client()
        logging.info("MCP 초기화 완료")
        
        # 웹 스크래퍼 초기화
        scraper = OrderQueenScraper(headless=False)
        await scraper.initialize()
        logging.info("브라우저 초기화 완료")
        
        # 로그인
        await scraper.login()
        logging.info("로그인 완료")
        
        # 매출 데이터 다운로드
        excel_files = await scraper.download_sales_data(start_date, end_date)
        if not excel_files:
            logging.error("매출 데이터 다운로드 실패")
            return
        
        # 데이터 처리
        processor = SalesDataProcessor()
        processed_data = processor.process_excel(excel_files)
        
        # Supabase에 데이터 저장
        for record in processed_data:
            try:
                response = supabase.table('daily_sales').insert(record).execute()
                logging.info(f"데이터 저장 완료: {record['store_code']} - {record['sales_date']}")
            except Exception as e:
                logging.error(f"데이터 저장 중 오류 발생: {str(e)}")
                continue
        
        logging.info(f"{len(processed_data)}개의 레코드가 성공적으로 처리되었습니다.")
        
    except Exception as e:
        logging.error(f"처리 중 오류 발생: {str(e)}")
        raise
    
    finally:
        # 브라우저 종료
        await scraper.close()
        logging.info("브라우저 종료 완료")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='매출 데이터 수집 스크립트')
    parser.add_argument('--mode', choices=['once', 'daily'], required=True,
                      help='실행 모드 선택 (once: 1회 실행, daily: 매일 실행)')
    parser.add_argument('--start-date', type=str, help='시작 날짜 (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='종료 날짜 (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    if args.mode == 'once':
        if not args.start_date or not args.end_date:
            parser.error('시작 날짜와 종료 날짜를 모두 지정해야 합니다.')
        asyncio.run(process_sales_data(args.start_date, args.end_date))
    
    elif args.mode == 'daily':
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        asyncio.run(process_sales_data(yesterday, yesterday))