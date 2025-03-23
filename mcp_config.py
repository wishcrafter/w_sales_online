from supabase import create_client, Client
import os
import logging
from dotenv import load_dotenv

class MCPConfig:
    def __init__(self):
        load_dotenv()
        
        # Supabase 설정
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase URL과 Key가 설정되지 않았습니다.")
            
        logging.info(f"Supabase URL: {self.supabase_url}")
        logging.info(f"Supabase Key: {self.supabase_key[:10]}...")
        
        try:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            logging.info("Supabase 클라이언트 생성 성공")
        except Exception as e:
            logging.error(f"Supabase 클라이언트 생성 실패: {str(e)}")
            raise
    
    def get_supabase_client(self) -> Client:
        return self.supabase