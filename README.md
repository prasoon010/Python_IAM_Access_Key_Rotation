# Python_IAM_Access_Key_Rotation
This python script will rotate the IAM user access/secret key after an interval and send the new access/secret key details via email

NOTE:
1) The service/IAM user used to connect to AWS account should have permission to make changes to IAM users
2) All IAM user should have tag(Key as 'email' and Value as email id to which access/secret key should be send; another tag for key age or rotation interval with Key as 'key_age' and 'Value' as your required number of days(in number)) otherwise default values will be taken.
3) Edit the script with your custom variables as mentioned in the comments, such as 'expiry' for rotation interval, admin_email_id (to which new access/secret key should be send in case IAM user do not have 'email' tag set as mentioned earlier), warn_expiry(email warning day before the expiry)
4) Exclude IAM user for which you do not want to rotate key
5) script uses a gmail id, so the smtp section should be modified according to your email server conf. From email logins are environment variables EMAIL_ID and EMAIL_PASS. You can set that in your .bashrc or .bash_profile file.
6) If you are using gmail id for mail sending, turn on less secure application access in security.
