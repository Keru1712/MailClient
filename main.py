from pop3 import fetch_emails, extract_info, extract_mess, extract_file, extract_file_name, get_subject_content, get_user_content, data, from_rules, subject_rules, content_rules, spam_rules
from smtp import send_email
import os
import threading
import time
general = data["General"]
# Hiển thị dữ liệu đã đọc
mail = general["Username"]
mail_in = mail.split('<')[1].split('>')[0]
print(mail)
pas = general["Password"]
smtp_port = general["SMTP"]
pop3_port = general["POP3"]
mail_server = general["MailServer"]
auto_load = general["Autoload"]

# Điếm số tệp có trong folder đường dẫn
def count_files(path):
    count = 0
    for filename in os.listdir(path):
        # Kiểm tra từ file có trong tên tệp hay không
        if 'file' in filename:
            count += 1
    return count

def check_path(path):
    print(path)
    if not os.path.exists(path):
        print("Đường dẫn không tồn tại")
        return False
    if not os.path.isdir(path):
        print("Đường dẫn không phải là thư mục")
        return False
    if len(os.listdir(path)) == 0 :
        return False
    return True

def check_seen(path):
    for filename in os.listdir(path):
        if filename == "seen":
            return True
    return False
def create_seen(path):
    path_seen = path + "/seen"
    with open(path_seen, 'wb') as file_result:
        file_result.write(b'seen')

# Form email khi hiển thị
def form_mail_view(index, path):
    if check_seen(path):
        seen = ""
    else:
        seen = "(Chưa đọc) "
    path_info = path + "/info"
    with open(path_info, 'r') as file:
        content = file.read()
    subject = get_subject_content(content)
    user = get_user_content(content)
    print(f"{index}. {seen}{user}, <{subject}>")

# Hiển thị số lượng mail có trong đường dẫn
def view_list_mail(path):
    list_id_mail = []
    for index, id in enumerate(os.listdir(path), start=1):
        list_id_mail.append(id)
        temp_path = path + f'/{id}'
        form_mail_view(index, temp_path)
    read(list_id_mail, path)
#Hàm non read trả lại danh sách các list mới, khi vẫn trong hàm read
def view_list_mail_non_read(path):
    list_id_mail = []
    for index, id in enumerate(os.listdir(path), start=1):
        list_id_mail.append(id)
        temp_path = path + f'/{id}'
        form_mail_view(index, temp_path)
    return list_id_mail


#In mess lấy từ database 
def print_message(path):
    path_info = path + "/info"
    path_mess = path + "/mess"
    with open(path_info, 'r') as file:
        content = file.read()
    extract_info(content)
    with open(path_mess, 'r') as file:
        content = file.read()
    extract_mess(content)
    num_file = count_files(path)
    print(f'Số tệp attachment: {num_file}')
    if num_file > 0:
        for i in range(num_file):
            path_file = path + f"/file{i+1}"
            with open(path_file, 'r') as file:
                content = file.read()
            file_name = extract_file_name(content)
            print(f'{i+1}. {file_name}')


def get_size_file(file_path):
    try:
        size=os.path.getsize(file_path)
        return size
    except FileNotFoundError:
        print("File không tồn tại")
        return 0
    
def save_file(path_file, path_save):
    count = 0
    for filename in os.listdir(path_file):
        if 'file' in filename:
            count +=1
            temp_path = path_file + f"/file{count}"
            with open(temp_path, 'r') as file:
                content = file.read()
            extract_file(content, path_save)

    
def send(ip, port, sender, pas):
    print("Đây là thông tin soạn email: (nếu không điền vui lòng nhấn enter để bỏ qua)")
    while True:
        to = input("To: ")
        cc = input("CC: ")
        bcc = input("BCC: ")
        #Phân loại
        recipients = ''
        type_sends = {}
        if to:
            type_sends["To"] = to
            recipients += "," + to
        if cc:
            type_sends["CC"] = cc
            recipients += "," + cc
        if bcc:
            type_sends["BCC"] = bcc
            recipients += "," + bcc
        if type_sends == {}:
            print("Bạn phải nhập người nhận!")
        else:
            break
    recipients = recipients[1:]
    # Nhập tiếp
    subject = input("Subject: ")
    content = input("Content: ")
    attach_file = input("Có gửi kèm file (1. có, 2. không): ")
    if attach_file == '1':
        max_size_file = 3 * 1024 * 1024
        size  = max_size_file + 1
        while(size > max_size_file):
            size = 0
            num_files = input("Số lượng file muốn gửi: ")
            # Kiểm tra num_files
            flag = True
            try:
                num_files = int(num_files)
            except ValueError:
                print("Bạn phải nhập số!")
                flag = False
            if not flag:
                size  = max_size_file + 1
                continue
            files = []
            # Nếu duyệt qua thành flag false đường dẫn nhập sai
            for i in range(num_files):
                file_path = input(f"Cho biết đường dẫn file thứ {i + 1}: ")
                if not os.path.exists(file_path):
                    print("Đường dẫn không tồn tại")
                    flag = False
                    break
                files.append(file_path)
            if not flag:
                size  = max_size_file + 1
                continue

            for i in files:
                size += get_size_file(i)
            if size > max_size_file:
                    print("Kích thước file vượt quá giới hạn cho phép")
        # Thực hiện gửi email
        send_email(ip, port, sender, pas, recipients, subject, content, type_sends, files)
        print("Đã gửi email thành công")
    else:
        send_email(ip, port, sender, pas, recipients, subject, content, type_sends)
        # Thực hiện gửi email không có file đính kèm ở đây
        print("Đã gửi email thành công")

def view(user):
    print("Đây là danh sách các folder trong mailbox của bạn:")
    # Code để lấy danh sách các folder và hiển thị
    folder_list = ["Inbox", from_rules["To_folder"], subject_rules["To_folder"], content_rules["To_folder"], spam_rules["To_folder"]]
    for index, folder in enumerate(folder_list, start=1):
        print(f"{index}. {folder}")

    folder_choice = input("Bạn muốn xem email trong folder nào: ")
    # Thực hiện xem email trong folder được chọn

    if folder_choice.isdigit():
        folder_choice = int(folder_choice)
        if 1 <= folder_choice <= len(folder_list):
            folder_name = folder_list[folder_choice - 1]
            print(f"Đây là danh sách email trong {folder_name} folder")
            path_folder = f"./database/{user}/{folder_name}"
            if check_path(path_folder):
                view_list_mail(path_folder)
            else:
                print(f'Không có email nào trong {folder_name}')
        else:
            print("Lựa chọn không hợp lệ")
    else:
        print("Thoát ra ngoài")

def read(list_id_mail, path):
    while True:
        email_choice = input("Bạn muốn đọc Email thứ mấy: ")
        if email_choice == '':
            break
        elif email_choice == '0':
            # Hiển thị lại danh sách email trong folder
            list_id_mail = view_list_mail_non_read(path)
        elif email_choice.isdigit():
            # Thực hiện đọc email thứ đã chọn
            email_choice = int(email_choice)
            print(f"Nội dung email của email thứ {email_choice}: ")
            path_id = path + f'/{list_id_mail[email_choice-1]}'
            print_message(path_id)
            create_seen(path_id)
            # Nếu có attach file
            if count_files(path_id) != 0:
                has_attachment = input("Trong email này có attached file, bạn có muốn save không: ")
                if has_attachment.lower() == 'có':
                    path_save = input("Cho biết đường dẫn bạn muốn lưu: ")
                    save_file(path_id, path_save)
                    print(f"Đã lưu file tại đường dẫn {path_save}")
                else:
                    print("Không lưu file")

def pop_from_server():
    while True:
        fetch_emails(mail_server, pop3_port, mail_in, pas)
        time.sleep(auto_load)

def main():
    pop_thread = threading.Thread(target=pop_from_server)
    pop_thread.daemon = True
    pop_thread.start()
    while True:
        print("Vui lòng chọn Menu:")
        print("1. Để gửi email")
        print("2. Để xem danh sách các email đã nhận")
        print("3. Thoát")
        choice = input("Bạn chọn: ")
        if choice == '1':
            send(mail_server, smtp_port, mail, pas)
        elif choice == '2':
            view(mail_in)
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")
        print("\n\r")

if __name__ == "__main__":
    main()

