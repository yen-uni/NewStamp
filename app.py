import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os

# --- 設定常數 ---
IMG_SIZE = 400  # 提高解析度讓印章更精緻
BORDER_WIDTH = 16
RED_COLOR = (204, 34, 34)

def draw_stretched_text(draw_obj, text, font_path, box, fill_color):
    """
    box: (x1, y1, x2, y2) 代表文字要填滿的格子範圍
    核心邏輯：先畫出文字，去背裁切，然後強行縮放至 box 的大小
    """
    x1, y1, x2, y2 = box
    target_w = x2 - x1
    target_h = y2 - y1
    
    # 1. 在超大臨時畫布上畫文字
    temp_font = ImageFont.truetype(font_path, 300)
    # 建立一個足夠大的透明畫布
    temp_img = Image.new('RGBA', (600, 600), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    temp_draw.text((300, 300), text, font=temp_font, fill=fill_color, anchor="mm")
    
    # 2. 裁切出文字實際有顏色的部分 (去掉字體自帶的空白邊際)
    bbox = temp_img.getbbox()
    if not bbox: return None
    char_img = temp_img.crop(bbox)
    
    # 3. 強行拉伸/縮放到目標格子的尺寸
    # 這裡就是關鍵：不論原本字體比例如何，都會被拉到填滿 target_w x target_h
    char_img = char_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    return char_img

def create_seal_image(text, font_path, padding):
    img = Image.new('RGBA', (IMG_SIZE, IMG_SIZE), (255, 255, 255, 0))
    
    # 計算內部可用空間 (扣除外框與使用者設定的 Padding)
    inner_start = BORDER_WIDTH + padding
    inner_end = IMG_SIZE - BORDER_WIDTH - padding
    inner_size = inner_end - inner_start
    mid = IMG_SIZE // 2

    if not os.path.exists(font_path):
        st.error(f"找不到字體檔: {font_path}")
        return None

    # --- 處理三字排版 ---
    if len(text) == 3:
        # 右側：姓氏 (廖) -> 佔據 1/2 寬度，1/1 高度
        s_box = (mid, inner_start, inner_end, inner_end)
        char_s = draw_stretched_text(None, text[0], font_path, s_box, RED_COLOR)
        if char_s: img.paste(char_s, (s_box[0], s_box[1]), char_s)

        # 左側：名字 (玉銘) -> 垂直平分
        # 左上 (名1)
        n1_box = (inner_start, inner_start, mid, mid)
        char_n1 = draw_stretched_text(None, text[1], font_path, n1_box, RED_COLOR)
        if char_n1: img.paste(char_n1, (n1_box[0], n1_box[1]), char_n1)

        # 左下 (名2)
        n2_box = (inner_start, mid, mid, inner_end)
        char_n2 = draw_stretched_text(None, text[2], font_path, n2_box, RED_COLOR)
        if char_n2: img.paste(char_n2, (n2_box[0], n2_box[1]), char_n2)

    # --- 處理四字排版 (2x2) ---
    elif len(text) >= 4:
        chars = text[:4]
        boxes = [
            (mid, inner_start, inner_end, mid),   # 右上
            (mid, mid, inner_end, inner_end),     # 右下
            (inner_start, inner_start, mid, mid), # 左上
            (inner_start, mid, mid, inner_end)    # 左下
        ]
        for i in range(4):
            char_img = draw_stretched_text(None, chars[i], font_path, boxes[i], RED_COLOR)
            if char_img: img.paste(char_img, (boxes[i][0], boxes[i][1]), char_img)

    # 繪製最外層邊框 (最後畫才不會被文字遮到)
    draw = ImageDraw.Draw(img)
    draw.rectangle([BORDER_WIDTH//2, BORDER_WIDTH//2, IMG_SIZE-BORDER_WIDTH//2, IMG_SIZE-BORDER_WIDTH//2], 
                   outline=RED_COLOR, width=BORDER_WIDTH)
    
    return img

# --- Streamlit 介面 ---
st.set_page_config(page_title="UNI-印章產生器", layout="centered")
st.title("🪭 「UNI」印章產生器")

# 側邊欄只留一個 Padding 調整
padding = st.sidebar.slider("邊距微調 (控制字體離邊框多遠)", 0, 50, 10)

user_input = st.text_input("輸入名字 (如：廖玉銘)", "廖玉銘")
target_font = "標楷體.ttf" # 請確認你的檔名

if user_input:
    seal_img = create_seal_image(user_input, target_font, padding)
    if seal_img:
        st.image(seal_img, caption="自動拉伸結構預覽", width=300)
        
        buf = io.BytesIO()
        seal_img.save(buf, format="PNG")
        st.download_button(label="📥 下載透明印章", data=buf.getvalue(), file_name=f"{user_input}_seal.png")
