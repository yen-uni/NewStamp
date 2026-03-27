import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os

# --- 設定常數 ---
IMG_SIZE = 400
BORDER_WIDTH = 16
RED_COLOR = (204, 34, 34)

def draw_stretched_text(text, font_path, box, fill_color):
    """
    強行拉伸文字以填滿指定的 box (x1, y1, x2, y2)
    """
    x1, y1, x2, y2 = box
    target_w = x2 - x1
    target_h = y2 - y1
    if target_w <= 0 or target_h <= 0: return None
    
    temp_img = Image.new('RGBA', (800, 800), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    try:
        temp_font = ImageFont.truetype(font_path, 400)
    except:
        return None
        
    temp_draw.text((400, 400), text, font=temp_font, fill=fill_color, anchor="mm")
    
    bbox = temp_img.getbbox()
    if not bbox: return None
    char_img = temp_img.crop(bbox)
    
    char_img = char_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    return char_img

def create_seal_image(text, font_path, padding):
    img = Image.new('RGBA', (IMG_SIZE, IMG_SIZE), (255, 255, 255, 0))
    
    inner_start = BORDER_WIDTH + padding
    inner_end = IMG_SIZE - BORDER_WIDTH - padding
    mid = IMG_SIZE // 2

    if not os.path.exists(font_path):
        st.error(f"找不到字體檔: {font_path}")
        return None

    layout_boxes = []

    if len(text) == 1:
        layout_boxes.append((text[0], (inner_start, inner_start, inner_end, inner_end)))

    elif len(text) == 2:
        # --- 關鍵修正：兩字改為直式 (上姓, 下名) ---
        # 上方字：寬度全開 (inner_start 到 inner_end)，高度佔上半部
        layout_boxes.append((text[0], (inner_start, inner_start, inner_end, mid)))
        # 下方字：寬度全開 (inner_start 到 inner_end)，高度佔下半部
        layout_boxes.append((text[1], (inner_start, mid, inner_end, inner_end)))

    elif len(text) == 3:
        # 三字：右姓 (全高), 左名1 (上半), 左名2 (下半)
        layout_boxes.append((text[0], (mid, inner_start, inner_end, inner_end)))
        layout_boxes.append((text[1], (inner_start, inner_start, mid, mid)))
        layout_boxes.append((text[2], (inner_start, mid, mid, inner_end)))

    elif len(text) >= 4:
        # 四字：右上, 右下, 左上, 左下
        t = text[:4]
        layout_boxes.append((t[0], (mid, inner_start, inner_end, mid)))
        layout_boxes.append((t[1], (mid, mid, inner_end, inner_end)))
        layout_boxes.append((t[2], (inner_start, inner_start, mid, mid)))
        layout_boxes.append((t[3], (inner_start, mid, mid, inner_end)))

    # 執行繪製
    for char, box in layout_boxes:
        char_img = draw_stretched_text(char, font_path, box, RED_COLOR)
        if char_img:
            img.paste(char_img, (box[0], box[1]), char_img)

    draw = ImageDraw.Draw(img)
    draw.rectangle([BORDER_WIDTH//2, BORDER_WIDTH//2, IMG_SIZE-BORDER_WIDTH//2, IMG_SIZE-BORDER_WIDTH//2], 
                   outline=RED_COLOR, width=BORDER_WIDTH)
    
    return img

# --- Streamlit 介面 ---
st.set_page_config(page_title="印章產生器", layout="centered")
st.title("🪭 正統印章產生器")

padding = st.sidebar.slider("邊距微調", 0, 50, 10)
user_input = st.text_input("輸入名字 (預設：王小明)", "王小明")

target_font = "標楷體.ttf" 

if user_input:
    seal_img = create_seal_image(user_input, target_font, padding)
    if seal_img:
        st.image(seal_img, caption=f"「{user_input}」的印章預覽", width=300)
        
        buf = io.BytesIO()
        seal_img.save(buf, format="PNG")
        st.download_button(label="📥 下載透明 PNG", data=buf.getvalue(), file_name=f"{user_input}_seal.png")
