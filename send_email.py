import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(receiver_emails=[to_email_list], title="test", text="", html=""):
    sender_email = "your_emial"  # 发件人邮箱
    # receiver_email = ""  # 收件人邮箱
    password = ""

    message = MIMEMultipart("alternative")
    message["Subject"] = title
    message["From"] = sender_email

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
        server.login(sender_email, password)
        for r in receiver_emails:
            message["To"] = r
            server.sendmail(sender_email, r, message.as_string())
            print("Email sent to {}!".format(r))
        print('over!')
   
    
    
if __name__ == '__main__':
    send_email([''], '')
    
