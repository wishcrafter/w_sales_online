from playwright.async_api import async_playwright, Browser, Page
from loguru import logger
import os
from datetime import datetime
from dotenv import load_dotenv
import asyncio
import logging

load_dotenv()

class OrderQueenScraper:
    def __init__(self, headless: bool = False):
        self.base_url = "https://www.orderqueen.kr"
        self.download_dir = "./downloads"
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.target_stores = os.getenv('STORE_CODES', '1001,1003,1004,1005').split(',')
        
        # 다운로드 디렉토리 생성
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            
        # 로그인 정보
        self.credentials = {
            'id': os.getenv('USERNAME'),
            'password': os.getenv('PASSWORD')
        }
        
        if not self.credentials['id'] or not self.credentials['password']:
            raise ValueError("환경 변수에서 로그인 정보를 찾을 수 없습니다.")

    async def initialize(self):
        try:
            logging.info("Playwright 초기화 시작")
            self.playwright = await async_playwright().start()
            
            logging.info("브라우저 시작")
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=['--start-maximized'],
                slow_mo=500
            )
            
            logging.info("브라우저 컨텍스트 생성")
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                accept_downloads=True
            )
            
            logging.info("새 페이지 생성")
            self.page = await self.context.new_page()
            
            logging.info("브라우저 초기화 완료")
            return True
            
        except Exception as e:
            logging.error(f"브라우저 초기화 중 오류 발생: {str(e)}")
            await self.close()
            raise

    async def login(self):
        try:
            logging.info("로그인 페이지로 이동")
            await self.page.goto(f"{self.base_url}/backoffice_admin/login.itp")
            await asyncio.sleep(2)
            
            logging.info("로그인 정보 입력")
            await self.page.fill('input[name="userId"]', self.credentials['id'])
            await self.page.fill('input[name="pw"]', self.credentials['password'])
            
            logging.info("로그인 버튼 클릭")
            await self.page.click('#btnLoginNew')
            await asyncio.sleep(3)
            
            # 로그인 성공 확인
            current_url = self.page.url
            if 'login.itp' in current_url:
                raise Exception("로그인 실패")
                
            logging.info("로그인 성공")
            return True
            
        except Exception as e:
            logging.error(f"로그인 중 오류 발생: {str(e)}")
            raise

    async def download_sales_data(self, start_date: str, end_date: str) -> list:
        try:
            logging.info(f"매출 데이터 다운로드 시작: {start_date} ~ {end_date}")
            
            # 매출 관리 페이지로 이동
            sales_url = f"{self.base_url}/backoffice_admin/BSL01010.itp"
            await self.page.goto(sales_url)
            await asyncio.sleep(3)
            
            # JavaScript를 사용하여 날짜 입력
            await self.page.evaluate(f"""
                document.querySelector('#schSDate').value = '{start_date}';
                document.querySelector('#schEDate').value = '{end_date}';
            """)
            await asyncio.sleep(1)
            
            all_files = []
            for store_code in self.target_stores:
                try:
                    logging.info(f"매장 {store_code} 선택")
                    await self.page.select_option('#schStoreNo', store_code)
                    await asyncio.sleep(2)
                    
                    # 검색 버튼 클릭
                    search_button = await self.page.wait_for_selector('#btn-search button')
                    await search_button.click()
                    await asyncio.sleep(3)
                    
                    # 엑셀 다운로드
                    async with self.page.expect_download() as download_info:
                        excel_button = await self.page.wait_for_selector('#btn-excel button')
                        await excel_button.click()
                        download = await download_info.value
                        
                        # 파일명에 매장 코드 포함
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        file_path = os.path.join(
                            self.download_dir,
                            f"sales_data_{store_code}_{timestamp}.xlsx"
                        )
                        
                        # 다운로드 완료까지 대기
                        await download.save_as(file_path)
                        all_files.append(file_path)
                        
                        logging.info(f"매장 {store_code} 데이터 다운로드 완료: {file_path}")
                    
                except Exception as e:
                    logging.error(f"매장 {store_code} 데이터 다운로드 중 오류 발생: {str(e)}")
                    continue
            
            return all_files
            
        except Exception as e:
            logging.error(f"매출 데이터 다운로드 중 오류 발생: {str(e)}")
            raise

    async def close(self):
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            logging.info("브라우저 리소스 정리 완료")
        except Exception as e:
            logging.error(f"브라우저 종료 중 오류 발생: {str(e)}")
            raise