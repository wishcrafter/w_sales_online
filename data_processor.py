import pandas as pd
import logging
import os
import re
from datetime import datetime

class SalesDataProcessor:
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        self.store_mapping = {
            '1001': '월계점',
            '1002': '명일점',
            '1003': '반포점',
            '1004': '상월곡점',
            '1005': '월계2호',
            '1006': '월곡점'
        }
        self.output_dir = './output'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def process_excel(self, file_paths: list) -> list:
        all_processed_data = []
        
        for file_path in file_paths:
            try:
                logging.info(f"엑셀 파일 처리 시작: {file_path}")
                
                # 파일명에서 매장 코드 추출
                store_code_match = re.search(r'sales_data_(\d+)_', file_path)
                if not store_code_match:
                    logging.error(f"파일명에서 매장 코드를 찾을 수 없음: {file_path}")
                    continue
                    
                store_code = store_code_match.group(1)
                store_name = self.store_mapping.get(store_code, '알 수 없는 매장')
                
                # 엑셀 파일 읽기
                df = pd.read_excel(file_path, header=None)
                logging.info(f"파일 {file_path}의 컬럼: {df.columns.tolist()}")
                
                # 데이터가 있는 행만 처리
                data_rows = df[df[0].str.contains(r'\d{4}-\d{2}-\d{2}', na=False)]
                
                # 데이터 처리
                for _, row in data_rows.iterrows():
                    try:
                        sales_date = row[0]  # 영업일자
                        if isinstance(sales_date, str):
                            sales_date = datetime.strptime(sales_date, '%Y-%m-%d').date()
                        
                        processed_row = {
                            'store_code': store_code,
                            'store_name': store_name,
                            'sales_date': sales_date.strftime('%Y-%m-%d'),
                            'transaction_count': int(row[1]),  # 거래건수
                            'total_sales': int(row[2]),  # 매출금액
                            'discount_amount': int(row[3]),  # 할인금액
                            'net_sales': int(row[9]),  # 순매출
                            'cash_payment': int(row[10]),  # 현금결제
                            'card_payment': int(row[11]),  # 카드결제
                            'point_payment': int(row[12]),  # 포인트
                            'other_payment': int(row[13]),  # 기타결제
                            'average_sale': int(row[14])  # 주문단가
                        }
                        all_processed_data.append(processed_row)
                        
                        # 데이터베이스에 저장
                        if self.db_manager:
                            self.db_manager.insert_sales_data(processed_row)
                            
                        logging.info(f"데이터 처리 완료: {store_code} - {sales_date}")
                        
                    except Exception as e:
                        logging.error(f"행 처리 중 오류 발생: {str(e)}, 행 데이터: {row}")
                        continue
                
                logging.info(f"파일 {file_path} 처리 완료, {len(data_rows)} 행 처리됨")
                
                # 처리 완료된 파일 삭제
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logging.info(f"파일 삭제 완료: {file_path}")
                
            except Exception as e:
                logging.error(f"파일 {file_path} 처리 중 오류 발생: {str(e)}")
                continue
        
        # 데이터를 CSV 파일로 저장
        if all_processed_data:
            df = pd.DataFrame(all_processed_data)
            output_file = os.path.join(
                self.output_dir,
                f"sales_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            logging.info(f"데이터를 CSV 파일로 저장 완료: {output_file}")
        
        logging.info(f"전체 처리된 레코드 수: {len(all_processed_data)}")
        return all_processed_data