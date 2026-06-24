from pydantic_settings import BaseSettings

class Setting(BaseSettings):
    DATABASE_URL:str
    SECRET_KEY:str

    AWS_SECRET_KEY_ID:str
    AWS_SECRET_ACCESS_KEY:str
    AWS_S3_BUCKET_NAME:str
    AWS_REGION:str
    SES_FROM_EMAIL:str

    ALGORITHM:str
    
    ACCESS_TOKEN_EXPIRE_MINUTES:int
    
    class Config:
        env_file=r"app\__gitignore__\.env"

setting=Setting()
