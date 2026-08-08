"""Shared configuration."""
import os
from typing import Literal
ENVIRONMENT:str=os.getenv("ENVIRONMENT",os.getenv("APP_ENV","local")).lower()
APP_ENV:str=ENVIRONMENT;DEBUG:bool=ENVIRONMENT not in("production","prod")
DATABASE_URL:str=os.getenv("DATABASE_URL","sqlite+aiosqlite:///./eco_nojin.db")
REDIS_URL:str=os.getenv("REDIS_URL","redis://localhost:6379/0")
SECRET_KEY:str=os.getenv("SECRET_KEY","change-me-in-production")
ACCESS_TOKEN_EXPIRE_MINUTES:int=int(os.getenv("ACCESS_TOKEN_EXPIRE","60"))
LLM_PROVIDER:Literal["openai","anthropic","ollama","xai"]|None=os.getenv("LLM_PROVIDER","ollama")#type:ignore
LLM_API_KEY:str|None=os.getenv("LLM_API_KEY");LLM_MODEL:str=os.getenv("LLM_MODEL","llama3")
SERVICE_TOKENS:dict[str,str]={"api":os.getenv("SERVICE_TOKEN_API",""),"cms":os.getenv("SERVICE_TOKEN_CMS",""),"ai":os.getenv("SERVICE_TOKEN_AI",""),"simulation":os.getenv("SERVICE_TOKEN_SIM",""),"ml":os.getenv("SERVICE_TOKEN_ML","")}
