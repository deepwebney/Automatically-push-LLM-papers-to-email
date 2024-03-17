import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(receiver_emails=['892904582@qq.com'], title="test", text="", html=""):
    sender_email = "1157118923@qq.com"  # 发件人邮箱
    # receiver_email = "sunmengxin98@163.com"  # 收件人邮箱
    password = "adpyyfdfthdbjgfc"  # QQ邮箱授权码

    message = MIMEMultipart("alternative")
    message["Subject"] = title
    message["From"] = sender_email

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    # 注意QQ邮箱的SMTP服务器地址是smtp.qq.com，端口号为465
    with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
        server.login(sender_email, password)
        for r in receiver_emails:
            message["To"] = r
            server.sendmail(sender_email, r, message.as_string())
            print("Email sent to {}!".format(r))
        print('over!')
   
    
    
if __name__ == '__main__':
    send_email(['zhangxiao_202003@163.com'], '宣朴副业第一弹')
    