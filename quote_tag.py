import streamlit as st
import json
import omni

st.title("Quote Tag Workplace")
try:
    with open('tag.json','r') as f:
        data = json.load(f)
        st.write("File loaded successfully.")

except json.JSONDecodeError:
    st.error("File không đúng định dạng JSON.")
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
with st.expander("Lấy Tag"):
    tag_path = set()
    with st.form("my_form"):
        selected = st.multiselect("Tìm và chọn tag: ", keys_option, key='sectlect4')
        submitted = st.form_submit_button('Xác nhận')

    if submitted and selected:
        for select_note in selected:
            tag_x = omni.find_path(data, select_note)
            omni.clean_data(tag_x)
            tag_path.update(tag_x)
        st.write("Kết quả tag_path:")
        st.write(sorted(list(tag_path), key=lambda x: x.lower()))

with st.expander("Thêm Nhánh"):
    selected = st.multiselect("Rẻ từ nhánh: ", keys_option, key='sectlect1')
    select_note = selected[0] if selected else None

    user_input = st.text_input("Tên nhánh mới: ", key='confirm_button12')

    if st.button('Xác nhận', key='confirm_button31'):
        omni.add_branch(data, select_note, user_input)
        with open('tag.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        st.rerun()


with st.expander("Chèn cành"):
    selected = st.multiselect("Là parent của: ", keys_option, key='sectlect2')
    select_note = selected[0] if selected else None

    user_input = st.text_input("Tên cành mới: ", key='confirm_button2')

    if st.button('Xác nhận', key='confirm_button22'):
        omni.insert_parent(data, select_note, user_input)
        with open('tag.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        st.rerun()


with st.expander("Xóa Cành và Nhánh Con"):
    selected = st.multiselect("Chọn nhánh cần xóa: ", keys_option[1:], key='sectlect3')
    select_note = selected[0] if selected else None
    if st.button('Xác nhận', key='confirm_button3'):
        omni.remove_key_once(data, select_note)
        with open('tag.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        st.rerun()

