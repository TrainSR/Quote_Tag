import streamlit as st
import json
import omni
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload
import io


# Lấy thông tin credentials từ secrets
creds_dict = dict(st.secrets["gcp_service_account"])
credentials = service_account.Credentials.from_service_account_info(creds_dict)
drive_service = build('drive', 'v3', credentials=credentials)

def extract_folder_id(url):
    if "folders/" in url:
        return url.split("folders/")[1].split("?")[0]
    elif "id=" in url:
        return url.split("id=")[1].split("&")[0]
    else:
        return None
def list_json_files_in_folder(folder_id):
    query = f"'{folder_id}' in parents and mimeType='application/json' and trashed = false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    return results.get('files', [])
def upload_json_to_drive(file_id, data):
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    fh = io.BytesIO(json_str.encode('utf-8'))
    media = MediaIoBaseUpload(fh, mimetype='application/json')

    drive_service.files().update(fileId=file_id, media_body=media).execute()



st.title("Quote Tag Workplace")
st.sidebar.header("Chọn folder chứa JSON")
folder_url = st.sidebar.text_input("Dán link thư mục Google Drive ở đây:")

folder_id = extract_folder_id(folder_url)
data = {}

if folder_id:
    files = list_json_files_in_folder(folder_id)
    file_names = [f['name'] for f in files]

    selected_file_name = st.sidebar.selectbox("Chọn file JSON:", file_names if file_names else ["Không có file JSON"])
    
    if selected_file_name and selected_file_name != "Không có file JSON":
        selected_file_id = next(f['id'] for f in files if f['name'] == selected_file_name)
        
        # Kiểm tra nếu đã có trong session_state thì không cần tải lại
        if 'loaded_file_id' not in st.session_state or st.session_state.loaded_file_id != selected_file_id:
            request = drive_service.files().get_media(fileId=selected_file_id)
            from io import BytesIO
            from googleapiclient.http import MediaIoBaseDownload

            fh = BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()

            fh.seek(0)
            try:
                data = json.load(fh)
                st.session_state.data = data  # Lưu JSON vào session
                st.session_state.loaded_file_id = selected_file_id
                st.success(f"Đã tải file `{selected_file_name}` thành công.")
            except json.JSONDecodeError:
                st.error("File không đúng định dạng JSON.")
        else:
            data = st.session_state.data  # Dùng lại JSON đã lưu

else:
    st.warning("Vui lòng nhập link folder hợp lệ.")
if 'data' in st.session_state and st.sidebar.button("💾 Lưu thay đổi lên Google Drive"):
    upload_json_to_drive(st.session_state.loaded_file_id, st.session_state.data)
    st.sidebar.success("Đã cập nhật file JSON trên Google Drive.")


keys_option = []
# Recursive function to extract keys
def extract_keys(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            keys_option.append(key)
            extract_keys(value)
    elif isinstance(obj, list):
        for item in obj:
            extract_keys(item)

extract_keys(data)
keys_option = sorted(list(keys_option), key=lambda x: x)
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📌 Lấy Tag", "🌿 Thêm Nhánh", "🪵 Chèn Cành", "🗑️ Xóa Cành", "✏️ Sửa nội dung"])
with tab1:
    tag_path = set()
    tag_p = set()
    with st.form("my_form"):
        selected = st.multiselect("Tìm và chọn tag: ", keys_option, key='sectlect4')
        submitted = st.form_submit_button('Xác nhận')

    if submitted and selected:
        for select_note in selected:
            tag_x = omni.find_path(data, select_note)
            tag_p.update(tag_x)
            omni.clean_data(tag_x)
            tag_path.update(tag_x)
        st.write("Kết quả tag path:")
        st.code(" ".join(sorted(tag_path, key=lambda x: x.lower())), language='text')
        st.write("Kết quả prompt path:")
        st.code(", ".join(sorted(omni.clean_set(tag_p - tag_path), key=lambda x: x.lower())), language='text')
        
with tab2:
    selected = st.selectbox("Rẻ từ nhánh: ", keys_option, key='sectlect1')
    select_note = selected if selected else None

    user_input = st.text_input("Tên nhánh mới: ", key='confirm_button12')

    if st.button('Xác nhận', key='confirm_button31'):
        omni.add_branch(data, select_note, user_input)
        st.session_state.data = data
        st.rerun()


with tab3:
    selected = st.selectbox("Là parent của: ", keys_option, key='sectlect2')
    select_note = selected if selected else None

    user_input = st.text_input("Tên cành mới: ", key='confirm_button2')

    if st.button('Xác nhận', key='confirm_button22'):
        omni.insert_parent(data, select_note, user_input)
        st.session_state.data = data
        st.rerun()


with tab4:
    selected = st.selectbox("Chọn nhánh cần xóa: ", keys_option[1:], key='sectlect3')
    select_note = selected if selected else None
    if st.button('Xác nhận', key='confirm_button3'):
        omni.remove_key_once(data, select_note)
        st.session_state.data = data
        st.rerun()

with tab5:
    selected = st.selectbox("Chọn nhánh cần đổi tên: ", keys_option, key='rename_select')
    new_key = st.text_input("Tên mới cho nhánh đã chọn: ", key='rename_input')

    if st.button("Xác nhận đổi tên", key='rename_confirm'):
        found = [False]  # Dùng list thay cho biến nonlocal

        def rename_key(obj):
            if isinstance(obj, dict):
                if selected in obj:
                    obj[new_key] = obj.pop(selected)
                    found[0] = True
                    return
                for v in obj.values():
                    rename_key(v)
            elif isinstance(obj, list):
                for item in obj:
                    rename_key(item)

        rename_key(data)

        if found[0]:
            st.session_state.data = data
            st.success(f"Đã đổi tên nhánh '{selected}' thành '{new_key}'.")
            st.rerun()
        else:
            st.warning("Không tìm thấy nhánh để đổi tên.")

