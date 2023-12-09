import base64
import socket
from email import message_from_string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

def send_email(host, port, sender, password, recipient_str, subject, message, attachment_paths, type_send = 'To') :
    recipients = recipient_str.split(' ')

    # Tạo đối tượng MIMEMultipart
    msg = MIMEMultipart()
    msg['From'] = sender
    msg[type_send] = recipient_str
    msg['Subject'] = subject

    # Thêm nội dung email
    msg.attach(MIMEText(message, 'plain','utf-8'))
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
        sock.sendall('AUTH LOGIN'.encode('utf-8') + b'\r\n')
        response = sock.recv(1024)

        # Gửi thông tin tài khoản
        sock.sendall(base64.b64encode(sender.encode('utf-8')) + b"\r\n")
        response = sock.recv(1024)

        sock.sendall(base64.b64encode(password.encode('utf-8')) + b'\r\n')
        response = sock.recv(1024)

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

def cc_send_email(host, port, sender, password, cc_str, subject, message, attachment_path):
    send_email(host, port, sender, password, cc_str, subject, message, attachment_path, 'Cc')
    
def bcc_send_email(host, port, sender, password, bcc_str, subject, message, attachment_path):
    bcc_list = bcc_str.split(' ')
    for bcc in bcc_list:
        send_email(host, port, sender, password, bcc, subject, message, attachment_path, 'Bcc')

#pop3

def fetch_emails(host, port, username, password):
    # Kết nối đến server POP3
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    response = sock.recv(1024)
    
    # Gửi lệnh USER và nhận phản hồi
    sock.sendall(f"USER {username}\r\n".encode('utf-8'))
    response = sock.recv(1024)
    
    # Gửi lệnh PASS và nhận phản hồi
    sock.sendall(f"PASS {password}\r\n".encode('utf-8'))
    response = sock.recv(1024)

    # Gửi lệnh LIST để lấy danh sách các email và nhận phản hồi
    sock.sendall(b"LIST\r\n")
    response = sock.recv(1024)
    
    # Lấy số lượng email trong hộp thư
    # Tách các dòng của phản hồi
    lines = response.decode('utf-8').split('\r\n')
    # Bỏ đi dòng đầu tiên chứa thông tin phản hồi
    print(lines)
    lines = lines[1:]
    lines = lines[:-2]
    
    # Đếm số lượng dòng còn lại (mỗi dòng là một email)
    num_messages = len(lines)
    
    # Lấy và hiển thị nội dung của các email
    for i in range(num_messages):
        sock.sendall(f"RETR {i+1}\r\n".encode('utf-8'))
        response = sock.recv(1024)
        print(f"Message {i+1}:\n")
        email_content = response.decode('utf-8')
        email_content = del_front_string(email_content,'\n') #Xóa kí tự ở ban đầu +OK num\r\n
        parse_email(email_content)
    
    # Gửi lệnh QUIT và đóng kết nối
    sock.sendall(b"QUIT\r\n")
    sock.close()

def del_front_string(string, char):
    while string[0] != char:
        string = string[1:]
    string = string[1:]
    return string

def parse_email(email_content):
    msg = message_from_string(email_content)
    boundary = msg.get_boundary()
    # Tách email thành các phần theo boundary
    parts = email_content.split(f"--{boundary}" )
    print(parts)
    # Lấy nội dung của các phần text/plain và application/octet-stream
    text_plain_part = parts[1].strip()  # Phần text/plain
    octet_stream_parts = parts[2:]  # Phần application/octet-stream
    # Lấy dữ liệu base64 từ các phần
    text_plain_data = text_plain_part.split("\r\n\r\n")[1].strip()
    # Giải mã dữ liệu base64
    decoded_text_plain = base64.b64decode(text_plain_data).decode("utf-8")
    print("Text/Plain Data:")
    print(decoded_text_plain)
    for octet_stream_part in octet_stream_parts:
        octet_stream_part = octet_stream_part.strip()
        print(octet_stream_part)
        extract_file(octet_stream_part)
#Trích xuất file   
def extract_file(octet_stream_part):
    # Lấy dữ liệu base64 từ octet-stream
    octet_stream_data = octet_stream_part.split("\r\n\r\n")[1].strip()
    # Giải mã dữ liệu base64
    decoded_octet_stream = base64.b64decode(octet_stream_data)
    #Tìm name & đuôi extension
    pos = octet_stream_part.find("filename=") + len("filename=")
    temp = octet_stream_part
    name = ""
    # định dạng filename=Text.rar\r\n
    while temp[pos] != ".":
        name += temp[pos]
        pos += 1
    extension = ""
    pos +=1
    while temp[pos] != "\r":
        extension += temp[pos]
        pos += 1
    print(extension)
    #Tạo các thư mục đến đường dẫn nếu chưa có
    if not os.path.exists(os.path.dirname(f"./folder/{name}.{extension}")):
        os.makedirs(os.path.dirname(f"./folder/{name}.{extension}"))
    # Trích xuất ra dữ liệu giải mã
    with open(f"./folder/{name}.{extension}", 'wb') as file_result:
        file_result.write(decoded_octet_stream)

if __name__ == "__main__":
    fetch_emails("127.0.0.1", 3335, "1@gmail.com", "123")
    # sender = "lethanhvinh@gmail.com"
    # recipient_str = input("To: ")
    # cc_str = input("CC: ")
    # bcc_str = input("BCC: ")
    # subject = input('Subject: ')
    # message = input("Message: ")
    # attachment_path = "./Text.rar"  # Thay đổi đường dẫn tệp đính kèm của bạn
    # attachment_paths = ["./Text.rar", "./Text.txt"]
    # send_email("127.0.0.1", 2225, sender, 'your_password', recipient_str, subject, message, attachment_paths)
    # if cc_str:
    #     cc_send_email("127.0.0.1", 2225, sender, 'your_password', cc_str, subject, message, attachment_paths)
    # if bcc_str:
    #     bcc_send_email("127.0.0.1", 2225, sender, 'your_password', bcc_str, subject, message, attachment_paths)
    #Menu
    # while True:
    #     print('Menu')
    #     print('2.Inbox')
    #     print('3.Exit')
    #     a = input('Choose: ')
    #     if a == 1:{

    #     }

    #     if a == 2:{

    #     }

    #     if a == 3:
    #         break
