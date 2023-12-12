from pop3 import fetch_emails, extract_info, extract_mess, extract_file, get_subject_content, get_user_content
from smtp import send_email, cc_send_email, bcc_send_email
import os

# Điếm số tệp có trong folder đường dẫn
def count_files(path):
    count = 0
    for filename in os.listdir(path):
        # Kiểm tra từ file có trong tên tệp hay không
        if 'file' in filename:
            count += 1
    return count

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
def view_list_mail_non_read(path):
    list_id_mail = []
    for index, id in enumerate(os.listdir(path), start=1):
        list_id_mail.append(id)
        temp_path = path + f'/{id}'
        form_mail_view(index, temp_path)
#In mess lấy từ database 
def print_message(path):
    path_info = path + "/info"
    path_mess = path + "/mess"
    path_file = path + "/file"
    with open(path_info, 'r') as file:
        content = file.read()
    extract_info(content)
    with open(path_mess, 'r') as file:
        content = file.read()
    extract_mess(content)
    num_file = count_files(path)
    print(f'So tep attachment: {num_file}')

def save_file(path_file, path_save):
    count = 0
    for filename in os.listdir(path_file):
        if 'file' in filename:
            count +=1
            temp_path = path_file + f"/file{count}"
            with open(temp_path, 'r') as file:
                content = file.read()
            extract_file(content, path_save)
    
#if __name__ == "__main__":
    #print_message("./database/2@gmail.com/Important/1072")
    #fetch_emails("127.0.0.1", 3335, "2@gmail.com", "123")
    # sender_name = "Thanh Vinh"
    # sender = "lethanhvinh@gmail.com"
    # recipient_str = input("To: ")
    # cc_str = input("CC: ")
    # bcc_str = input("BCC: ")
    # subject = input('Subject: ')
    # message = input("Message: ")
    # attachment_path = "./Text.rar"  # Thay đổi đường dẫn tệp đính kèm của bạn
    # attachment_paths = ["./Text.rar", "./Text.txt"]
    
def send(sender_name, sender):
    print("Đây là thông tin soạn email: (nếu không điền vui lòng nhấn enter để bỏ qua)")
    to = input("To: ")
    cc = input("CC: ")
    bcc = input("BCC: ")
    subject = input("Subject: ")
    content = input("Content: ")
    attach_file = input("Có gửi kèm file (1. có, 2. không): ")
    if attach_file == '1':
        # Lấy file path
        num_files = int(input("Số lượng file muốn gửi: "))
        files = []
        for i in range(num_files):
            file_path = input(f"Cho biết đường dẫn file thứ {i + 1}: ")
            files.append(file_path)
        # Thưck hiện gửi email
        if to:
            send_email("127.0.0.1", 2225, sender_name, sender, 'your_password', to, subject, content, files)
        if cc:
            cc_send_email("127.0.0.1", 2225, sender_name, sender, 'your_password', cc, subject, content, files)
        if bcc:
            bcc_send_email("127.0.0.1", 2225, sender_name, sender, 'your_password', bcc, subject, content, files)
        print("Đã gửi email thành công")
    else:
        if to:
            send_email("127.0.0.1", 2225, sender_name, sender, 'your_password', to, subject, content)
        if cc:
            cc_send_email("127.0.0.1", 2225, sender_name, sender, 'your_password', cc, subject, content)
        if bcc:
            bcc_send_email("127.0.0.1", 2225, sender_name, sender, 'your_password', bcc, subject, content)
        # Thực hiện gửi email không có file đính kèm ở đây
        print("Đã gửi email thành công")

def view(user):
    print("Đây là danh sách các folder trong mailbox của bạn:")
    # Code để lấy danh sách các folder và hiển thị
    folder_list = ["Inbox", "Project", "Important", "Work", "Spam"]
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
            view_list_mail(path_folder)
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
            view_list_mail_non_read(path)
            pass
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
                    save_file(path, path_save)
                    print(f"Đã lưu file tại đường dẫn {path_save}")
                else:
                    print("Không lưu file")

def main():
    sender_name = "Thanh Vinh"
    sender = "<lethanhvinh@gmail.com>"
    user = "2@gmail.com"
    while True:
        print("Vui lòng chọn Menu:")
        print("1. Để gửi email")
        print("2. Để xem danh sách các email đã nhận")
        print("3. Thoát")
        choice = input("Bạn chọn: ")
        if choice == '1':
            send(sender_name, sender)
        elif choice == '2':
            view(user)
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")

if __name__ == "__main__":
    main()

