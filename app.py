import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os

# 設定網頁標題與圖示
st.set_page_config(page_title="線上印章生成器", page_icon="🧧")

def generate_stamp(surname, given_name, font_path="標楷體.ttf"):
    # 檢查字體檔是否存在
    if not os.path.exists(font_path):
        st.error(f"❌ 找不到字體檔：{font_path}。請確認檔案已上傳至 GitHub 根目錄。")
        return None

    size = (300, 300)
    center = (150, 150)
    radius = 130
    red_color = (255, 0, 0)
    
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius], 
                 outline=red_color, width=12)
    
    # 根據名字長度調整字體大小
    font_size = 120 if len(given_name) == 1 else 100
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        st.error(f"字體讀取失敗：{e}")
        return None

    # 右姓左名排版邏輯
    draw.text((160, 150), surname, font=font, fill=red_color, anchor="mm")
    if len(given_name) == 1:
        draw.text((100, 150), given_name, font=font, fill=red_color, anchor="mm")
    else:
        draw.text((100, 100), given_name[0], font=font, fill=red_color, anchor="mm")
        draw.text((100, 200), given_name[1], font=font, fill=red_color, anchor="mm")
    
    return img

# --- Streamlit 介面渲染 ---
st.title("🧧 線上印章生成器")
st.write("輸入姓名，即時生成透明背景的標楷體印章。")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        surname = st.text_input("輸入姓氏", max_chars=1, value="陳")
    with col2:
        given_name = st.text_input("輸入名字", max_chars=2, value="小明")

if st.button("✨ 立即生成印章"):
    with st.spinner('正在製作中...'):
        result_img = generate_stamp(surname, given_name)
        if result_img:
            st.image(result_img, caption="生成結果預覽", width=200)
            
            buf = io.BytesIO()
            result_img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="📥 下載透明背景印章 (PNG)",
                data=byte_im,
                file_name=f"stamp_{surname}{given_name}.png",
                mime="image/png"
            )
