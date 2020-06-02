import logging
import boto3
from botocore.exceptions import ClientError
import smtplib
import os


def create_presigned_url(bucket_name, object_name, expiration=36000):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_post(bucket_name,
                                                     object_name,
                                                     ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


def send_email(subject, destination, msg):
    email = os.environ["EMAIL"]
    password = os.environ["PASSWORD"]
    try:
        server = smtplib.SMTP("smtp.gmail.com:587")
        server.ehlo()
        server.starttls()
        server.login(email,password)
        message = f"Subject: {subject}\n\n{msg}"
        server.sendmail(email,destination,message)
        server.quit()
        print("success: email sent")
    except:
        print("email fail to send...")