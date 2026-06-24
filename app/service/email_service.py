import boto3
from botocore.exceptions import ClientError
from ..utils.config import setting
from fastapi import HTTPException,status

def get_ses_client():
    return boto3.client('ses',region_name=setting.AWS_REGION,
                        aws_secret_access_key=setting.AWS_SECRET_ACCESS_KEY,
                        aws_access_key_id=setting.AWS_SECRET_KEY_ID)

def send_email(to_email:str,subject:str,body:str):
    try:
        get_ses_client().send_email(
            Source=setting.SES_FROM_EMAIL,
            Destination={"ToAddresses":[to_email]},
            Message={
                "Subject":{"Data":subject},
                "Body":{"Text":{"Data":body}},
            })
        

    except ClientError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Unable to send the email --{e}")



def send_appointment_email(email:str):
    send_email(email,
               "Your appointment is fixed ",
               f"Please visit the clinic as per your time")
    

