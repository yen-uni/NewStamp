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

    # 3. 處理三字排版 (右姓左名)
    if len(text) == 3:
        # --- 右側：姓氏 (廖) ---
        # 計算置中 (使用 anchor='mm' 可以精準地以文字中心點對齊座標)
        # s_offset[0] 是水平微調, s_offset[1] 是垂直微調
        draw.text((mid + (mid//2) + s_offset[0], mid + s_offset[1]), 
                  text[0], font=font_s, fill=RED_COLOR, anchor="mm")

        # --- 左側：名字 (玉銘) ---
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

    return img

# --- Streamlit 介面設定 ---
st.set_page_config(page_title="專業印章產生器", layout="wide")

st.sidebar.title("🎨 印章微調面板")
st.sidebar.info("如果覺得字體太小或位置不對，請調整下方滑桿。")

# --- 側邊欄控制項 ---
s_size = st.sidebar.slider("姓氏大小 (右側)", 50, 250, 160)
n_size = st.sidebar.slider("名字大小 (左側)", 30, 150, 85)

st.sidebar.markdown("---")
st.sidebar.write("📍 位置微調 (左右 / 上下)")
s_x = st.sidebar.slider("姓氏水平微調", -30, 30, 0)
s_y = st.sidebar.slider("姓氏垂直微調", -30, 30, 0)
n_x = st.sidebar.slider("名字水平微調", -30, 30, 0)
n_y = st.sidebar.slider("名字垂直微調", -30, 30, 0)

# --- 主要區域 ---
st.title("🪭 專業版印章產生器")
user_input = st.text_input("輸入名字 (1~4個字)", "廖玉銘")

# 這裡請確認你的字體檔名 (font.ttf 或 標楷體.ttf)
target_font = "標楷體.ttf" 

if user_input:
    seal_img = create_seal_image(
        user_input, 
        target_font, 
        s_size, n_size, 
        (s_x, s_y), (n_x, n_y)
    )
    
    if seal_img:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(seal_img, caption="即時預覽 (透明背景)", width=250)
            
            buf = io.BytesIO()
            seal_img.save(buf, format="PNG")
            st.download_button(
                label="📥 下載透明 PNG",
                data=buf.getvalue(),
                file_name=f"{user_input}_seal.png",
                mime="image/png"
            )
        with col2:
            st.success("✅ 已根據你的設定即時更新預覽！")
            st.write("💡 **使用小技巧：**")
            st.write("1. 調整「大小」讓字體填滿方框。")
            st.write("2. 如果字體重心偏掉，調整「位置微調」讓視覺更平衡。")
