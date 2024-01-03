import base64
import socket
from datetime import datetime
from email import message_from_string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import formataddr
from email import encoders
import os

    
def send_email(host, port, sender, password, recipient_str, subject, message, type_sends, attachment_paths = None) :
    #gắn ngày giờ
    date = datetime.now()
    date = date.strftime('%a, %d %b %Y %H:%M:%S %z')
    recipients = recipient_str.split(',')
    # Tạo đối tượng MIMEMultipart
    # sender_formatted = formataddr((sender_name, sender))
    msg = MIMEMultipart()
    msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
    msg['From'] = sender
    flag = False
    if 'To' in type_sends:
        msg['To'] = type_sends['To']
        flag = True
    if 'CC' in type_sends:
        msg['CC'] = type_sends['CC']
        flag = True
    #Nếu không có thì in To: undisclosed-recipients: ;
    if not flag:
        msg['To'] = " undisclosed-recipients: ;"
    msg['Subject'] = subject

    # Thêm nội dung email
    msg.attach(MIMEText(message, 'plain','utf-8'))
    if attachment_paths != None:
        for attachment_path in attachment_paths:
            attach_file(msg, attachment_path)

    # Kết nối đến máy chủ SMTP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))

        # Gửi lệnh EHLO
        ehlo_command = f"EHLO {host}\r\n"
        sock.sendall(ehlo_command.encode('utf-8'))
        response = sock.recv(1024)
        print(response.decode('utf-8'))

        # Gửi lệnh AUTH LOGIN
        #sock.sendall('AUTH LOGIN'.encode('utf-8') + b'\r\n')
        #response = sock.recv(1024)

        # Gửi thông tin tài khoản
        #sock.sendall(base64.b64encode(sender.encode('utf-8')) + b"\r\n")
        #response = sock.recv(1024)

        #sock.sendall(base64.b64encode(password.encode('utf-8')) + b'\r\n')
        #response = sock.recv(1024)

        # Gửi lệnh MAIL FROM
        sock.sendall(b"MAIL FROM: <" + sender.encode('utf-8') + b">\r\n")
        response = sock.recv(1024)

        # Gửi lệnh RCPT TO cho mỗi người nhận
        for recipient in recipients:
            sock.sendall(b"RCPT TO: <" + recipient.encode('utf-8') + b">\r\n")
            response = sock.recv(1024)
        # Gửi lệnh DATA
        sock.sendall("DATA".encode('utf-8') + b'\r\n')
        response = sock.recv(1024)

        # Gửi nội dung email
        sock.sendall(msg.as_string().encode('utf-8') + b"\r\n")

        # Gửi lệnh QUIT
        sock.sendall(b"\r\n.\r\n")
        response = sock.recv(1024)

        sock.sendall(b"QUIT\r\n")

def attach_file(msg, attachment_path):
    # Mở và đọc nội dung của tệp tin đính kèm
    with open(attachment_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename={os.path.basename(attachment_path)}")
        msg.attach(part)

# def cc_send_email(host, port, sender, password, cc_str, subject, message, attachment_path = None):
#     send_email(host, port, sender, password, cc_str, subject, message, attachment_path, 'CC')
    
# def bcc_send_email(host, port, sender, password, bcc_str, subject, message, attachment_path = None):
#     bcc_list = bcc_str.split(',')
#     for bcc in bcc_list:
#         send_email(host, port, sender, password, bcc, subject, message, attachment_path, 'BCC')