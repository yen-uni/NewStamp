import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os

# --- 設定常數 ---
IMG_SIZE = 200
BORDER_WIDTH = 8
RED_COLOR = (204, 34, 34)

def create_seal_image(text, font_path, s_size, n_size, s_offset, n_offset):
    # 建立「RGBA」模式圖片 (透明背景)
    img = Image.new('RGBA', (IMG_SIZE, IMG_SIZE), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # 1. 畫印章外框
    draw.rectangle(
        [(BORDER_WIDTH//2, BORDER_WIDTH//2), 
         (IMG_SIZE - BORDER_WIDTH//2, IMG_SIZE - BORDER_WIDTH//2)],
        outline=RED_COLOR, 
        width=BORDER_WIDTH
    )

    if not os.path.exists(font_path):
        st.error(f"❌ 找不到字體檔：{font_path}")
        return None

    mid = IMG_SIZE // 2
    
    # 2. 準備字體
    font_s = ImageFont.truetype(font_path, s_size)
    font_n = ImageFont.truetype(font_path, n_size)

    # 3. 處理三字排版 (右側一長條 = 姓 / 左側上下兩格 = 名)
    if len(text) == 3:
        # --- 右側：姓氏 (例如：廖) ---
        # 關鍵修正：垂直座標設為 mid (100)，讓它在印章正中間，高度才能匹配左邊兩字總和
        draw.text((mid + (mid//2) + s_offset[0], mid + s_offset[1]), 
                  text[0], font=font_s, fill=RED_COLOR, anchor="mm")

        # --- 左側：名字 (例如：玉銘) ---
        # 左上 (名1)
        draw.text((mid//2 + n_offset[0], mid//2 + n_offset[1]), 
                  text[1], font=font_n, fill=RED_COLOR, anchor="mm")
        # 左下 (名2)
        draw.text((mid//2 + n_offset[0], mid + mid//2 + n_offset[1]), 
                  text[2], font=font_n, fill=RED_COLOR, anchor="mm")

    # 4. 處理四字排版 (標準 2x2)
    elif len(text) >= 4:
        chars = text[:4]
        # 右上, 右下, 左上, 左下
        draw.text((mid + mid//2 + s_offset[0], mid//2 + s_offset[1]), chars[0], font=font_n, fill=RED_COLOR, anchor="mm")
        draw.text((mid + mid//2 + s_offset[0], mid + mid//2 + s_offset[1]), chars[1], font=font_n, fill=RED_COLOR, anchor="mm")
        draw.text((mid//2 + n_offset[0], mid//2 + n_offset[1]), chars[2], font=font_n, fill=RED_COLOR, anchor="mm")
        draw.text((mid//2 + n_offset[0], mid + mid//2 + n_offset[1]), chars[3], font=font_n, fill=RED_COLOR, anchor="mm")
    
    # 5. 二字排版 (左右均分)
    elif len(text) == 2:
        draw.text((mid + mid//2 + s_offset[0], mid + s_offset[1]), text[0], font=font_s, fill=RED_COLOR, anchor="mm")
        draw.text((mid//2 + n_offset[0], mid + n_offset[1]), text[1], font=font_s, fill=RED_COLOR, anchor="mm")

    return img

# --- Streamlit 介面 ---
st.set_page_config(page_title="專業印章產生器", layout="wide")

st.sidebar.title("🎨 比例調教面版")
# 設定預設值：如果是 3 字，姓氏通常要比名字大兩倍
s_size = st.sidebar.slider("姓氏大小 (建議: 160)", 50, 250, 160)
n_size = st.sidebar.slider("名字大小 (建議: 85)", 30, 150, 85)

st.sidebar.markdown("---")
st.sidebar.write("📍 位置微調")
s_x = st.sidebar.slider("姓氏左右", -30, 30, 0)
s_y = st.sidebar.slider("姓氏上下", -30, 30, 0)
n_x = st.sidebar.slider("名字左右", -30, 30, 0)
n_y = st.sidebar.slider("名字上下", -30, 30, 0)

st.title("🪭 正統結構印章產生器")
user_input = st.text_input("輸入名字 (如：廖玉銘)", "廖玉銘")

# 請確認字體檔名為 font.ttf
target_font = "標楷體.ttf" 

if user_input:
    seal_img = create_seal_image(user_input, target_font, s_size, n_size, (s_x, s_y), (n_x, n_y))
    
    if seal_img:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(seal_img, caption="正統 1:2 結構預覽", width=250)
            
            buf = io.BytesIO()
            seal_img.save(buf, format="PNG")
            st.download_button(label="📥 下載透明印章", data=buf.getvalue(), file_name=f"{user_input}_seal.png")
        with col2:
            st.success("核心邏輯已修正：右側姓氏現在為全高度欄位。")
            st.info("💡 調整建議：將「姓氏大小」拉大到 170 左右，它就會自動頂滿右半部的高度。")
