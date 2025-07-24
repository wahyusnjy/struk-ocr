import streamlit as st
import easyocr
import numpy as np
import cv2
from PIL import Image, ImageDraw
import json
import re
from datetime import datetime

# Inisialisasi EasyOCR
@st.cache_resource
def get_reader():
    return easyocr.Reader(['en'], gpu=False)

reader = get_reader()

def process_image(img: Image.Image):
    # Convert PIL Image to numpy
    img_np = np.array(img)
    img_rgb = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB) if img_np.shape[2] == 3 else img_np

    # OCR
    results = reader.readtext(img_rgb)

    # Sort results vertically (top to bottom) based on the y-coordinate of the first point in bbox
    results_sorted = sorted(results, key=lambda r: r[0][0][1])

    # Draw bounding boxes on copy of image
    boxed_img = img.copy()
    draw = ImageDraw.Draw(boxed_img)
    for bbox, text, conf in results:
        pts = [tuple(point) for point in bbox]
        draw.line(pts + [pts[0]], fill='yellow', width=3)
        draw.text(pts[0], text, fill='red')

    return results_sorted, boxed_img

def extract_shell_receipt_details(ocr_results):
    """
    Extracts specific details from OCR results if it's a Shell receipt.
    Includes basic cleaning for common OCR errors (e.g., 'o' vs '0').
    Attempts to extract 'amount' from specific line, and 'rate' from line 31.
    """
    details = {
        "location": None,
        "date_time": None,
        "fuel_type": None,
        "amount": None,
        "volume": None,
        "rate": None
    }

    cleaned_all_text = " ".join([text for bbox, text, conf in ocr_results])
    cleaned_all_text = re.sub(r'[oO]', '0', cleaned_all_text)
    cleaned_all_text = re.sub(r'(?<![a-zA-Z])l(?!\w)', '1', cleaned_all_text)
    cleaned_all_text = re.sub(r'(?<![a-zA-Z])i(?!\w)', '1', cleaned_all_text)
    all_text_lower = cleaned_all_text.lower()

    # --- Lokasi pembelian: Coba ambil dari indeks ke-1 jika tersedia ---
    # Prioritas 1: Mencari pola "shell [alamat]" di seluruh teks
    if len(ocr_results) > 0: # Memastikan index 0 ada
        potential_location_from_index_0 = ocr_results[0][1].strip() # Ambil teks dari index 0
        # Bersihkan teks ini juga dari kesalahan OCR umum
        potential_location_from_index_0_cleaned = re.sub(r'[oO]', '0', potential_location_from_index_0)
        potential_location_from_index_0_cleaned = re.sub(r'(?<![a-zA-Z])l(?!\w)', '1', potential_location_from_index_0_cleaned)
        potential_location_from_index_0_cleaned = re.sub(r'(?<![a-zA-Z])i(?!\w)', '1', potential_location_from_index_0_cleaned)

        # Validasi apakah teks dari index 0 ini benar-benar terlihat seperti lokasi
        # Cek apakah mengandung "shell" atau kata-kata umum alamat
        is_valid_location_candidate = False
        if "shell" in potential_location_from_index_0_cleaned.lower():
            is_valid_location_candidate = True
        elif re.search(r'(jalan|jln|street|rd|road|no)\s*\d*', potential_location_from_index_0_cleaned.lower()):
            is_valid_location_candidate = True
        
        if is_valid_location_candidate and potential_location_from_index_0_cleaned: # Jika teks tidak kosong dan valid
            details["location"] = potential_location_from_index_0_cleaned
            st.write(f"DEBUG: Lokasi diambil dari index 0: '{details['location']}'") # Debugging
    
    # Prioritas 2 (Fallback jika Lokasi dari index 1 tidak ada/kosong):
    if details["location"] is None:
        location_match = re.search(r'(shell\s+[a-z0-9\s,.-]+(?:jalan|jln|street|rd|road|no)\s*\d+)', all_text_lower, re.IGNORECASE)
        if location_match:
            details["location"] = location_match.group(0).strip()
            st.write(f"DEBUG: Lokasi diambil dari regex 'shell [alamat]': '{details['location']}'") # Debugging
        else:
            # Prioritas 3 (Fallback jika pola di atas tidak ditemukan): Cari kandidat lokasi dan ambil yang pertama
            location_candidates = []
            for bbox, text, conf in ocr_results:
                if conf > 0.7:
                    cleaned_text_lower = text.lower()
                    if 'shell' in cleaned_text_lower:
                        idx = all_text_lower.find('shell')
                        if idx != -1:
                            context = all_text_lower[max(0, idx - 30):min(len(all_text_lower), idx + 30)]
                            potential_loc = re.search(r'shell\s*([a-z0-9\s,.-]+)', context, re.IGNORECASE)
                            if potential_loc:
                                location_candidates.append(potential_loc.group(1).strip())
                    elif re.search(r'(jalan|jln|street|rd|road|no)\s*\d+', cleaned_text_lower):
                        location_candidates.append(text.strip())
            
            if location_candidates:
                details["location"] = location_candidates[0] # Ambil elemen pertama dari kandidat
                st.write(f"DEBUG: Lokasi diambil dari kandidat list (first): '{details['location']}'") # Debugging


    
    # --- Tanggal dan Waktu: Coba cari di baris 16 (waktu) dan 17 (tanggal) ---
    time_line_index = 15 # Baris ke-16 (index 15)
    date_line_index = 16 # Baris ke-17 (index 16)

    extracted_date = None
    extracted_time = None

    # Step 1: Attempt to extract time from specific line
    if len(ocr_results) > time_line_index:
        time_text_raw = ocr_results[time_line_index][1]
        cleaned_time_text = re.sub(r'[oO]', '0', time_text_raw)
        cleaned_time_text = re.sub(r'(?<![a-zA-Z])l(?!\w)', '1', cleaned_time_text)
        cleaned_time_text = re.sub(r'(?<![a-zA-Z])i(?!\w)', '1', cleaned_time_text)
        # Regex for HH:MM:SS or HH:MM. Make sure it's at the beginning or standalone for better accuracy.
        time_match = re.search(r'^\s*(\d{2}:\d{2}(?::\d{2})?)\s*$', cleaned_time_text)
        if time_match:
            extracted_time = time_match.group(1) # Use group(1) to get the captured time
            st.write(f"DEBUG: Waktu dari baris {time_line_index+1}: {time_text_raw} -> Cleaned: {cleaned_time_text} -> Extracted: {extracted_time}")


    # Step 2: Attempt to extract date from specific line
    if len(ocr_results) > date_line_index:
        date_text_raw = ocr_results[date_line_index][1]
        cleaned_date_text = re.sub(r'[oO]', '0', date_text_raw)
        cleaned_date_text = re.sub(r'(?<![a-zA-Z])l(?!\w)', '1', cleaned_date_text)
        cleaned_date_text = re.sub(r'(?<![a-zA-Z])i(?!\w)', '1', cleaned_date_text)
        # Regex for DD/MM/YY or DD/MM/YYYY. Ensure it's the primary content of the line.
        date_match = re.search(r'^\s*(\d{2}[-/]\d{2}[-/]\d{2}(?:\d{2})?)\s*$', cleaned_date_text) # Allow 2 or 4 digit year
        if date_match:
            # Always format to DD/MM/YYYY
            date_part = date_match.group(1)
            # If year is 2 digits, assume 20YY or 19YY based on current year
            parts = re.split(r'[-/]', date_part)
            if len(parts[2]) == 2:
                current_year_last_two_digits = int(datetime.now().strftime('%y'))
                scanned_year_last_two_digits = int(parts[2])
                # Simple heuristic: if the scanned year is greater than current year + 5 years, assume previous century
                # This prevents "25" in 2024 from becoming 1925 (should be 2025)
                if scanned_year_last_two_digits > (current_year_last_two_digits + 5) and (scanned_year_last_two_digits - current_year_last_two_digits > 50): # Add 50 for older dates
                     parts[2] = '19' + parts[2]
                else:
                    parts[2] = '20' + parts[2] # Prepend '20' for 2-digit years
            extracted_date = f"{parts[0]}/{parts[1]}/{parts[2]}"
            st.write(f"DEBUG: Tanggal dari baris {date_line_index+1}: {date_text_raw} -> Cleaned: {cleaned_date_text} -> Extracted: {extracted_date}")

    # Step 3: Combine if both are found from specific lines, OTHERWISE FALLBACK
    # This structure ensures that if ANY specific extraction worked, we try to combine it first.
    # If both extracted_date and extracted_time are None, then it moves to the general fallback.
    if extracted_date and extracted_time:
        details["date_time"] = f"{extracted_date} {extracted_time}"
    elif extracted_date: # If only date was found from specific line
        details["date_time"] = extracted_date
    elif extracted_time: # If only time was found from specific line
        details["date_time"] = extracted_time
    else:
        # Fallback to general search (using cleaned_all_text)
        # This part remains mostly as it was, but adjusted to prioritize DD/MM/YYYY
        date_time_combined_match = re.search(r'(\d{2}[-/]\d{2}[-/]\d{4})\s+(\d{2}:\d{2}(?::\d{2})?)', cleaned_all_text)
        if date_time_combined_match:
            date_part = date_time_combined_match.group(1).replace('-', '/')
            time_part = date_time_combined_match.group(2)
            details["date_time"] = f"{date_part} {time_part}"
        else:
            date_time_combined_match = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2})\s+(\d{2}:\d{2}(?::\d{2})?)', cleaned_all_text)
            if date_time_combined_match: # YYYY-MM-DD HH:MM:SS
                date_part = date_time_combined_match.group(1).replace('-', '/')
                time_part = date_time_combined_match.group(2)
                # Reformat YYYY/MM/DD to DD/MM/YYYY for consistency
                parts = date_part.split('/')
                date_part_formatted = f"{parts[2]}/{parts[1]}/{parts[0]}"
                details["date_time"] = f"{date_part_formatted} {time_part}"
            else: # Try to find date and time separately in general text
                date_match_general = re.search(r'(\d{2}[-/]\d{2}[-/]\d{4})', cleaned_all_text)
                time_match_general = re.search(r'(\d{2}:\d{2}(?::\d{2})?)', cleaned_all_text)
                
                if date_match_general and time_match_general:
                    date_part = date_match_general.group(0).replace('-', '/')
                    time_part = time_match_general.group(0)
                    details["date_time"] = f"{date_part} {time_part}"
                elif date_match_general:
                    details["date_time"] = date_match_general.group(0).replace('-', '/')
                elif time_match_general:
                    details["date_time"] = time_match_general.group(0)



    # Fuel Type
    fuel_types_keywords = {
        "shell v-power nitro+", "v-power nitro+", "nitro+",
        "shell v-power diesel", "v-power diesel",
        "shell v-power", "v-power",
        "shell super", "super",
        "shell ron 92", "ron 92",
        "shell ron 95", "ron 95",
        "diesel", "solar", "pertamax", "pertalite"
    }
    found_fuel_type = None
    for keyword in fuel_types_keywords:
        if keyword in all_text_lower:
            found_fuel_type = keyword.replace("shell ", "").title()
            break
    details["fuel_type"] = found_fuel_type if found_fuel_type else "Unknown Fuel Type"

    # Specific line extraction for Amount
    amount_line_index = 23 # Baris ke-24
    if len(ocr_results) > amount_line_index:
        line_24_text = ocr_results[amount_line_index][1]
        cleaned_line_24_text = re.sub(r'[oO]', '0', line_24_text)
        cleaned_line_24_text = re.sub(r'(?<![a-zA-Z])l(?!\w)', '1', cleaned_line_24_text)
        cleaned_line_24_text = re.sub(r'(?<![a-zA-Z])i(?!\w)', '1', cleaned_line_24_text)
        
        amount_match_line_24 = re.search(r'(\d+(?:[.,]\d+)*)', cleaned_line_24_text)

        if amount_match_line_24:
            num_str = amount_match_line_24.group(1).replace('.', '').replace(',', '.')
            try:
                details["amount"] = float(num_str)
            except ValueError:
                details["amount"] = None
        
    # Fallback for Amount
    if details["amount"] is None:
        amount_match = re.search(r'(total|amount|grand\s*total)\s*[:=]?\s*rp?\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)', cleaned_all_text, re.IGNORECASE)
        if amount_match:
            num_str = amount_match.group(2).replace('.', '').replace(',', '.')
            try:
                details["amount"] = float(num_str)
            except ValueError:
                details["amount"] = None
        else:
            amount_match = re.search(r'rp?\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*$', cleaned_all_text)
            if amount_match:
                num_str = amount_match.group(1).replace('.', '').replace(',', '.')
                try:
                    details["amount"] = float(num_str)
                except ValueError:
                    details["amount"] = None

    # Volume (Liter)
    volume_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(liter|litre|lt)', cleaned_all_text, re.IGNORECASE)
    if volume_match:
        details["volume"] = float(volume_match.group(1).replace(',', '.'))

    # Rate (Harga per Liter): Coba cari di baris 31
    rate_line_index = 30 # Baris ke-31 berarti index 30
    if len(ocr_results) > rate_line_index:
        rate_text = ocr_results[rate_line_index][1]
        cleaned_rate_text = re.sub(r'[oO]', '0', rate_text)
        cleaned_rate_text = re.sub(r'(?<![a-zA-Z])l(?!\w)', '1', cleaned_rate_text)
        cleaned_rate_text = re.sub(r'(?<![a-zA-Z])i(?!\w)', '1', cleaned_rate_text)
        
        rate_match_line_31 = re.search(r'(\d+(?:[.,]\d+)*)', cleaned_rate_text)
        if rate_match_line_31:
            num_str = rate_match_line_31.group(1).replace('.', '').replace(',', '.')
            try:
                details["rate"] = float(num_str)
            except ValueError:
                details["rate"] = None

    # Fallback for Rate if specific line extraction failed
    if details["rate"] is None:
        rate_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:rp)?/?(?:liter|litre|l|unit)', cleaned_all_text, re.IGNORECASE)
        if rate_match:
            details["rate"] = float(rate_match.group(1).replace(',', '.'))
        elif details["amount"] and details["volume"] and details["volume"] > 0:
            details["rate"] = round(details["amount"] / details["volume"], 2)


    return details


# --- New Function to Check for Shell Receipt ---
def is_shell_receipt(ocr_results):
    """
    Checks if any of the detected words contain "Shell" (case-insensitive).
    """
    for bbox, text, conf in ocr_results:
        if "shell" in text.lower() and conf > 0.6:
            return True
    return False

# --- Streamlit App ---
st.title("Kamera & OCR Streamlit Demo")
st.write("Ambil foto dari kamera atau upload gambar, lalu hasil OCR & kata yang terdeteksi akan tampil di bawah.")

# Camera or File Upload
image_data = st.camera_input("Ambil gambar dari kamera")
if not image_data:
    image_data = st.file_uploader("Atau upload file gambar", type=["jpg", "jpeg", "png"])

if image_data:
    # Load Image
    img = Image.open(image_data).convert("RGB")
    st.image(img, caption="Gambar diambil", use_column_width=True)

    # OCR & highlight
    with st.spinner("Memproses OCR..."):
        results_sorted, boxed_img = process_image(img)

    # Display OCR Results
    st.subheader("Hasil Kata yang Terdeteksi (Diurutkan Vertikal):")
    all_detected_words = []
    for idx, (bbox, text, conf) in enumerate(results_sorted):
        st.write(f"{idx+1}. **{text}** (Confidence: {conf:.2f})")
        all_detected_words.append({"text": text, "confidence": round(conf, 2)})

    # Check if it's a Shell receipt and extract details
    is_shell = is_shell_receipt(results_sorted)
    st.subheader("Informasi Struk:")

    json_output = {}

    if is_shell:
        st.success("Ini kemungkinan besar struk dari Shell!")
        shell_details = extract_shell_receipt_details(results_sorted)
        json_output = {
            "is_shell_receipt": True,
            "purchase_details": {
                "location": shell_details["location"],
                "date_time": shell_details["date_time"],
                "name": f"Pembelian bensin {shell_details['fuel_type']}",
                "amount": shell_details["amount"],
                "volume": shell_details["volume"],
                "rate": shell_details["rate"]
            }
        }
    else:
        st.info("Tidak terdeteksi sebagai struk Shell.")
        json_output = {
            "is_shell_receipt": False,
            "detected_words": all_detected_words
        }

    st.subheader("Data OCR (JSON):")
    st.json(json_output)

    st.subheader("Preview Gambar dengan Highlight Teks:")
    st.image(boxed_img, caption="Deteksi Teks", use_column_width=True)

else:
    st.info("Silakan ambil foto dari kamera atau upload gambar.")