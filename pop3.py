import base64
import socket
from email import message_from_string
import os
from email import encoders

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
        id_mess = lines[i][2:] # 'count' 'num'
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
    # Tách email thành các phần theo boundary
    parts = email_content.split(f"--{boundary}" )
    # Lấy nội dung của các phần text/plain và application/octet-stream
    info_part = parts[0].strip()
    text_plain_part = parts[1].strip()  # Phần text/plain
    octet_stream_parts = parts[2:len(parts)-1]  # Phần application/octet-stream, lấy phần tử thứ 2->n-1
    with open(f"./database/{username}/{filt}/{id_mess}/info", 'wb') as file_result:
        file_result.write(info_part.encode())
    with open(f"./database/{username}/{filt}/{id_mess}/mess", 'wb') as file_result:
        file_result.write(text_plain_part.encode())
    i = 1
    for octet_stream_part in octet_stream_parts:
        with open(f"./database/{username}/{filt}/{id_mess}/file{i}", 'wb') as file_result:
            file_result.write(octet_stream_part.encode())
        i += 1
    
# Hàm lấy dữ liệu lớn
def get_response(sock):
    buffer_size = 9012  # Đặt timeout cho socket (ví dụ, 5 giây)
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
    parts = email_content.split(f"--{boundary}" )
    # Lấy nội dung của các phần text/plain và application/octet-stream
    info_part = parts[0].strip()
    text_plain_part = parts[1].strip()  # Phần text/plain
    octet_stream_parts = parts[2:len(parts)-1]  # Phần application/octet-stream, lấy phần tử thứ 2->n-1
    info = message_from_string(info_part)
    sender = info['From']
    subject = str(info['Subject'])
    content = get_email_content(text_plain_part)
    # Filter
    if any(addr in sender for addr in ['ahihi@testing.com', 'ahuu@testing.com']):
        move_email(email_content ,username, id_mess, 'Project')
    elif any(word in subject.lower() for word in ['urgent', 'asap']):
        move_email(email_content ,username, id_mess, 'Important')
    elif any(word in content.lower() for word in ['report', 'meeting']):
        move_email(email_content ,username, id_mess, 'Work')
    elif any(word in subject.lower() or word in content.lower() for word in ['virus', 'hack', 'crack']):
        move_email(email_content ,username, id_mess, 'Spam')
    else:
        move_email(email_content ,username, id_mess, 'Inbox')
    
def extract_info(info_part):
    info = message_from_string(info_part)
    From = info['From']
    To = info['To']
    CC = info['CC']
    BCC = info['BCC']
    subject = info['Subject']
    print(f'From: {From}')
    if To:
        print(f'To: {To}')
    if CC:
        print(f'CC: {CC}')
    if BCC:
        print(f'BCC: {BCC}')
    if subject:
        print(f'subject: {subject}')
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
    decoded_text_plain = base64.b64decode(text_plain_data).decode()
    return decoded_text_plain
def extract_mess(text_plain_part):
    split_parts = text_plain_part.split("\n\n")
    if len(split_parts) > 1:
        text_plain_data = split_parts[1].strip()
    else:
    # Trường hợp không tìm thấy hoặc chỉ có một phần tử
        text_plain_data = ""
        return text_plain_data
    decoded_text_plain = base64.b64decode(text_plain_data).decode()
    print(decoded_text_plain)

#Trích xuất file   
def extract_file(octet_stream_part, path):
    octet_stream_data = octet_stream_part.split("\n\n")[1].strip()
    decoded_octet_stream = base64.b64decode(octet_stream_data)
    pos = octet_stream_part.find("filename=") + len("filename=")
    temp = octet_stream_part
    name = ""
    # định dạng filename=Text.rar\r\n
    while temp[pos] != ".":
        name += temp[pos]
        pos += 1
    extension = ""
    pos +=1
    while temp[pos] != "\n":
        extension += temp[pos]
        pos += 1
    #Tạo các thư mục đến đường dẫn nếu chưa có
    if not os.path.exists(path):
        os.makedirs(path)
    # Trích xuất ra dữ liệu giải mã
    with open(f"{path}/{name}.{extension}", 'wb') as file_result:
        file_result.write(decoded_octet_stream)