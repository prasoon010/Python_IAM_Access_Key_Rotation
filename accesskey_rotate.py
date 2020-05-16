import boto3
from botocore.exceptions import ClientError
import os
import datetime
import smtplib
import email.message

e_username = os.environ.get('EMAIL_ID')   # fetches environment variable EMAIL_ID(gmail id)
e_password = os.environ.get('EMAIL_PASS')      # fetches environment variable EMAIL_PASS
admin_email_id = ['']   # Provide your admin email id inside the list
exclude_list = ['']     # Provide IAM user list to exclude from key rotation
expiry = 30    # Provide key rotation interval, default set to 30 days
warn_expiry = 1   # Default warning 1 day before expiry, you may set a value less that 'expiry/key_age'

d = datetime.datetime
t1 = d.now().strftime("%Y-%m-%d_%H:%M:%S")
current = d.strptime(t1, "%Y-%m-%d_%H:%M:%S")
client = boto3.client('iam')
iam_raw = client.list_users()
iam_list = []


def send_email(new_access_key, new_secret_key, user,
               count, access_key, email_id=None):
    report = email.message.EmailMessage()
    report['From'] = e_username
    if email_id is None:
        report['To'] = admin_email_id
    else:
        report['To'] = [email_id]
    if new_access_key is not None and new_secret_key is not None:
        report['Subject'] = 'New Access Key for user: {}'.format(user)
        report.set_content('IAM User {} set {}: Deleted Access Key: {}\
                          \nNew Access Key is {} and New Secret Key is {}\
                          '.format(user, count, access_key,
                                   new_access_key, new_secret_key))

    else:
        report['Subject'] = 'Warning: Expiry: Access Key for user: {}'.format(user)
        report.set_content('IAM User {}: Access key {} expires in warn_expiry days'.format(user, access_key))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:  # edit based on mail server conf
        smtp.login(e_username, e_password)

        try:
            smtp.send_message(report)
        except smtplib.SMTPException:
            del report['To']
            del report['Subject']
            report['To'] = admin_email_id
            report['Subject'] = 'Failed:Email ID>>{}<<:AccessKey for user: {}'.format(email_id, user)
            smtp.send_message(report)


for user in iam_raw['Users']:
    if user['UserName'] not in exclude_list:
        iam_list.append(user['UserName'])

for i in iam_list:
    c_expiry = expiry
    count = 0
    email_id = None
    response = client.list_access_keys(UserName=i)['AccessKeyMetadata']
    tags = client.list_user_tags(UserName=i)['Tags']
    for tag in tags:
        if tag['Key'] == 'email' and tag['Value'].strip():
            email_id = tag['Value']
        if tag['Key'] == 'key_age' and tag['Value'].strip():
            c_expiry = int(tag['Value'])
    for key in response:
        count += 1
        t2 = key['CreateDate'].strftime("%Y-%m-%d_%H:%M:%S")
        old = d.strptime(t2, "%Y-%m-%d_%H:%M:%S")
        diff = current - old
        email_warn = c_expiry - diff.days
        access_key = key['AccessKeyId']
        if diff.days >= c_expiry:
            client.delete_access_key(UserName=i, AccessKeyId=access_key)
            create_response = client.create_access_key(UserName=i)['AccessKey']
            new_access_key = create_response['AccessKeyId']
            new_secret_key = create_response['SecretAccessKey']
            send_email(new_access_key, new_secret_key, i, count, access_key,
                       email_id=email_id)
        elif email_warn == warn_expiry:
            new_access_key = None
            new_secret_key = None
            send_email(new_access_key, new_secret_key, i, count, access_key,
                       email_id=email_id)
