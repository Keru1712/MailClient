import base64
import socket
from email import message_from_string
import os
import json
from email import encoders

file_path = './config.json'
# Đọc dữ liệu từ file JSON
with open(file_path, 'r') as file:
    data = json.load(file)
general_data = data["General"]
rule_data = data["Filter"]
from_rules = {}
subject_rules = {}
content_rules = {}
spam_rules = {}
for rule in rule_data:
    if "From" in rule:
        from_rules = rule
    elif "Subject" in rule:
        subject_rules = rule
    elif "Content" in rule:
        content_rules = rule
    elif "Spam" in rule:
        spam_rules = rule


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
    sock.sendall(b"UIDL\r\n")
    response = sock.recv(1024)
    # Lấy số lượng email trong hộp thư
    # Tách các dòng của phản hồi
    lines = response.decode('utf-8').split('\r\n')
    # Bỏ đi dòng đầu tiên và 2 dòng cuối chứa thông tin phản hồi
    #print(lines)
    lines = lines[1:]
    lines = lines[:-2]
    # Đếm số lượng dòng còn lại (mỗi dòng là một email)
    num_messages = len(lines)
    # Lấy và hiển thị nội dung của các email
    for i in range(num_messages):
        sock.sendall(f"RETR {i+1}\r\n".encode('utf-8'))
        #response = sock.recv(1000)
        response = get_response(sock)
        #print(f"Message {i+1}:\n")
        email_content = response.decode('utf-8')
        id_mess = del_front_string(lines[i], ' ') # 'count' 'num'
        email_content = del_front_string(email_content,'\n') #Xóa kí tự ở ban đầu +OK num\r\n
        parse_email(email_content, username, id_mess)
    
    # Gửi lệnh QUIT và đóng kết nối
    sock.sendall(b"QUIT\r\n")
    sock.close()

def move_email(email_content,username, id_mess, filt):
    path = f"./database/{username}/{filt}/{id_mess}"
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        return
    msg = message_from_string(email_content)
    boundary = msg.get_boundary()
    if boundary:
        # Tách email thành các phần theo boundary
        parts = email_content.split(f"--{boundary}" )
        # Lấy nội dung của các phần text/plain và application/octet-stream
        info_part = parts[0].strip()
        text_plain_part = parts[1].strip()  # Phần text/plain
        octet_stream_parts = parts[2:len(parts)-1]  # Phần application/octet-stream, lấy phần tử thứ 2->n-1
    else:
        parts = email_content.split("Content-Type:")
        info_part = parts[0].strip()
        text_plain_part = parts[1].strip()
        text_plain_part =  "Content-Type: " + text_plain_part  
        text_plain_part = text_plain_part[:-3] # Xóa ".\n\n"
        octet_stream_parts = []
    with open(f"./database/{username}/{filt}/{id_mess}/info", 'wb') as file_result:
        file_result.write(info_part.encode())
    with open(f"./database/{username}/{filt}/{id_mess}/mess", 'wb') as file_result:
        file_result.write(text_plain_part.encode())
    i = 1
    for octet_stream_part in octet_stream_parts:
        octet_stream_part = octet_stream_part.strip()
        with open(f"./database/{username}/{filt}/{id_mess}/file{i}", 'wb') as file_result:
            file_result.write(octet_stream_part.encode())
        i += 1

def is_base64(s):
    try:
        decoded = base64.b64decode(s).decode('utf-8')
        return True
    except Exception:
        return False
    
# Hàm lấy dữ liệu lớn
def get_response(sock):
    buffer_size = 9012  
    received_data = b''
    while True:
        data = sock.recv(buffer_size)
        received_data += data
        if b'\r\n.\r\n' in data:  # Kiểm tra xem đã nhận được phần cuối của email chưa
            break  
    return received_data

def del_front_string(string, char):
    while string[0] != char:
        string = string[1:]
    string = string[1:]
    return string

def parse_email(email_content, username, id_mess):
    msg = message_from_string(email_content)
    boundary = msg.get_boundary()
    # Tách email thành các phần theo boundary
    # Lấy nội dung của các phần text/plain và application/octet-stream
    if boundary:
        parts = email_content.split(f"--{boundary}" )
        info_part = parts[0].strip()
        text_plain_part = parts[1].strip()  # Phần text/plain
    else:
        parts = email_content.split("Content-Type:")
        info_part = parts[0].strip()
        text_plain_part = parts[1].strip()
    # octet_stream_parts = parts[2:len(parts)-1]   Phần application/octet-stream, lấy phần tử thứ 2->n-1
    info = message_from_string(info_part)
    sender = info['From']
    #Nếu info có subject
    if info['Subject']:
        subject = info['Subject']
    else:
        subject = ""
    content = get_email_content(text_plain_part)
    # Filter
    # Tạo sẵn filter cho người dùng
    folder_list = ["Inbox", from_rules["To_folder"], subject_rules["To_folder"], content_rules["To_folder"], spam_rules["To_folder"]]
    for filt in folder_list:
        path = f"./database/{username}/{filt}"
        if not os.path.exists(path):
            os.makedirs(path)

    if any(addr in sender for addr in from_rules['From']):
        move_email(email_content ,username, id_mess, from_rules["To_folder"])
    elif any(word in subject for word in subject_rules['Subject']):
        move_email(email_content ,username, id_mess, subject_rules["To_folder"])
    elif any(word in content.lower() for word in content_rules['Content']):
        move_email(email_content ,username, id_mess, content_rules["To_folder"])
    elif any(word in subject.lower() or word in content.lower() for word in spam_rules['Spam']):
        move_email(email_content ,username, id_mess, spam_rules["To_folder"])
    else:
        move_email(email_content ,username, id_mess, 'Inbox')
    
def extract_info(info_part):
    info = message_from_string(info_part)
    Date = info['Date']
    From = info['From']
    To = info['To']
    CC = info['CC']
    #BCC = info['BCC']
    subject = info['Subject']
    if Date:
        print(Date)
    print(f'From: {From}')
    if To:
        print(f'To: {To}')
    if CC:
        print(f'CC: {CC}')
    # if BCC:
    #     print(f'BCC: {BCC}')
    if subject:
        print(f'Subject: {subject}')

def get_user_content(info_part):
    info = message_from_string(info_part)
    return info['From']

def get_subject_content(info_part):
    info = message_from_string(info_part)
    return info['Subject']

def get_email_content(text_plain_part):
    split_parts = text_plain_part.split("\r\n\r\n")
    if len(split_parts) > 1:
        text_plain_data = split_parts[1].strip()
    else:
    # Trường hợp không tìm thấy hoặc chỉ có một phần tử
        text_plain_data = ""
        return text_plain_data
    if is_base64(text_plain_data):
        decoded_text_plain = base64.b64decode(text_plain_data).decode()
        return decoded_text_plain
    else:
        return text_plain_data
    
def extract_mess(text_plain_part):
    split_parts = text_plain_part.split("\n\n")
    text_plain_data = ""
    if len(split_parts) > 1:
        text_plain_data = split_parts[1].strip()
        #Nếu content mail có xuống dòng
        for part in split_parts[2:]:
            text_plain_data += "\n\n" + part.strip()
    else:
    # Trường hợp không tìm thấy hoặc chỉ có một phần tử
        return text_plain_data
    if is_base64(text_plain_data):
        decoded_text_plain = base64.b64decode(text_plain_data).decode()
        print(decoded_text_plain)
    else:
        print(text_plain_data)

#Lất tên file
def extract_file_name(octet_stream_part):
    pos = octet_stream_part.find("filename=") + len("filename=")
    temp = octet_stream_part
    name = ""
    while temp[pos] != "\n":
        name += temp[pos]
        pos += 1
    # Nếu tên có dấu nháy thì xóa dấu nháy
    if '"' in name:
        name = name[1:-1]
    return name
#Trích xuất file   
def extract_file(octet_stream_part, path):
    octet_stream_data = octet_stream_part.split("\n\n")[1].strip()
    decoded_octet_stream = base64.b64decode(octet_stream_data)
    pos = octet_stream_part.find("filename=") + len("filename=")
    temp = octet_stream_part
    name = ""
    # định dạng filename=Text.rar\r\n hoặc filename="Text.rar"\r\n
    while temp[pos] != ".":
        name += temp[pos]
        pos += 1
    extension = ""
    pos +=1
    while temp[pos] != "\n":
        extension += temp[pos]
        pos += 1
    # Nếu tên có dấu nháy thì xóa dấu nháy
    if '"' in name:
        name = name[1:]
    if '"' in extension:
        extension = extension[:-1]
    #Tạo các thư mục đến đường dẫn nếu chưa có
    if not os.path.exists(path):
        os.makedirs(path)
    # Trích xuất ra dữ liệu giải mã
    with open(f"{path}/{name}.{extension}", 'wb') as file_result:
        file_result.write(decoded_octet_stream)