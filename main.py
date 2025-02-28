import streamlit as st
import requests
import subprocess
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import socket

st.markdown(
    """
    <style>
    body {
        background-color: #f5f5f5;
    }
    </style>
    """, unsafe_allow_html=True
)

st.title("DEVICE MANAGER")

st.markdown(
    """
    <style>
    input[type="text"] {
        border: 2px solid #3498db;
        border-radius: 5px;
        background-color: #f5f5f5;
        padding: 10px;
        width: 100%;
        box-sizing: border-box;
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 5px;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        border: 2px solid #000;
    }
    th, td {
        border: 2px solid #000;
        padding: 8px;
    }
    tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    th {
        background-color: #CCE5FF;
        color: white;
        text-align: center;
    }
    td {
        text-align: center;
    }
    .custom-text {
        font-family: 'Times New Roman';
        font-size: 20px;
        color: #000;
    }
    .highlight-number {
        color: #FF5733;
        font-size: 24px;
    }
    </style>
    """, unsafe_allow_html=True)

def check_ip(ip):
    url = f"http://{ip}"
    try:
        response = requests.get(url, timeout=1)
        if response.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        return False

    return False

def get_mac_address(ip):
    try:
        # Thực hiện lệnh arp để lấy bảng ARP
        result = subprocess.run(['arp', '-a', ip], capture_output=True, text=True)
        output = result.stdout

        # Sử dụng biểu thức chính quy để tìm địa chỉ MAC trong kết quả lệnh arp
        mac_address = re.search(r'([0-9a-f]{2}[:\-]){5}[0-9a-f]{2}', output.lower())

        if mac_address:
            return mac_address.group(0)
        else:
            return "Không tìm thấy địa chỉ MAC"
    except Exception as e:
        return str(e)

def scan_ip(ip):
    if check_ip(ip):
        mac = get_mac_address(ip).upper()
        name = get_device_name(ip)
        return ip, mac, name
    return ip, None, None


def get_device_name(ip):
    try:
        host_name = socket.gethostbyaddr(ip)
        return host_name[0]
    except socket.herror:
        return


def main():

    # Tạo danh sách các địa chỉ IP cần kiểm tra
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        IP11 = st.text_input(" ", key="IP1")
        IP12 = st.text_input(" ", key="IP2")
    with col2:
        IP21 = st.text_input(" ", key="IP21")
        IP22 = st.text_input(" ", key="IP22")
    with col3:
        IP31 = st.text_input(" ", key="IP31")
        IP32 = st.text_input(" ", key="IP32")
    with col4:
        start = st.text_input(" ", key="IP41")
        end = st.text_input(" ", key="IP42")

    if IP11 == "" or IP12 == "" or IP21 == "" or IP22 == "" or IP31 == "" or IP32 == "" or start == "" or end == "":
        st.warning("INPUT VALUE!")
    else:
        try:
            IP11, IP12, IP21, IP22, IP31, IP32, start, end = \
                int(IP11), int(IP12), int(IP21), int(IP22), int(IP31), int(IP32), int(start), int(end)

            ips = [f"{IP11}.{IP21}.{IP31}.{i}" for i in range(start, end + 1)]
            ok_ips = []
            progress_bar = st.progress(0)

            if st.button("SCAN"):
                # Sử dụng ThreadPoolExecutor để quét song song
                with ThreadPoolExecutor(max_workers=20) as executor:
                    futures = [executor.submit(scan_ip, ip) for ip in ips]
                    for i, future in enumerate(futures):
                        ip, mac, name = future.result()
                        if mac:
                            ok_ips.append([ip, mac, name])
                        progress_bar.progress((i + 1) / len(ips))

                # Hiển thị kết quả
                st.markdown(
                    f'<p class="custom-text">Có <span class="highlight-number">{len(ok_ips)}</span> thiết bị phản hồi:</p>',
                    unsafe_allow_html=True)
                df = pd.DataFrame(ok_ips, columns=["IP Address", "Mac Address", "Device Name"])
                # st.write(f"Có {len(ok_ips)} thiết bị phản hồi:")
                st.table(df)

        except Exception as e:
            st.error(f"{e}.")

if __name__ == "__main__":
    main()
