from pydantic_settings import BaseSettings

class Setting(BaseSettings):
    DATABASE_URL:str
    SECRET_KEY:str

    AWS_SECRET_KEY_ID:str=""
    AWS_SECRET_ACCESS_KEY:str=""
    AWS_S3_BUCKET_NAME:str=""
    AWS_REGION:str="ap-south-1"
    SES_FROM_EMAIL:str="noreply@threshold.local"

    ALGORITHM:str
    
    ACCESS_TOKEN_EXPIRE_MINUTES:int
    
    class Config:
        env_file="app/__gitignore__/.env"

setting=Setting()
