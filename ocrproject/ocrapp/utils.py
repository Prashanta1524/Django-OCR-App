import cv2
import numpy as np
import base64
from google.generativeai import GenerativeModel, configure
import fitz  # PyMuPDF
import os
from django.conf import settings

# Configure Gemini API
API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyDgravfB3y3PsGnoOR3D5gEjsj5b0D1vgs')  # Fallback to default key if not set
configure(api_key=API_KEY)
model = GenerativeModel("gemini-2.0-flash")

# Add a dictionary for English translations
LABEL_TRANSLATIONS = {
    "नाम थर": "Full Name",
    "जन्म मिति": "Date of Birth",
    "बाबुको नाम थर": "Father's Name",
    "आमाको नाम थर": "Mother's Name",
    "नागरिकता नम्बर": "Citizenship Number",
    "अन्य विवरण": "Other Details"
}

# Add page-specific field definitions
PAGE_FIELDS = {
    1: {
        "नाम थर": "Full Name",
        "ठेगाना": "Address",
        "मिति": "Date"
    },
    2: {
        "नाम थर": "Full Name",
        "लिङ्ग": "Gender",
        "पेशा": "Occupation",
        "नागरिकता नम्बर": "Citizenship Number",
        "जिल्ला": "District",
        "नगरपालिका वा गा.वि.स.": "Municipality or VDC",
        "जन्म मिति": "Date of Birth",
        "बुवाको नाम": "Father's Name",
        "तालिम लिएको स्थान": "Place where training is taken",
        "तालिम मिति": "Training Date"
    },
    3: {
        "नाम थर": "Full Name",
        "ठेगाना": "Address"
    },
    4: {
        "नाम थर": "Full Name",
        "जन्म मिति": "Date of Birth",
        "ठेगाना": "Address",
        "बुवाको नाम": "Father's Name",
        "लिङ्ग": "Gender",
        "पेशा": "Occupation",
        "मोबाइल नम्बर": "Mobile Number",
        "इमेल": "Email",
        "प्यान नम्बर": "PAN Number",
        "बैंकको नाम": "Bank Name",
        "बैंक खाता नम्बर": "Bank Account Number",
        "साइन मिति": "Signed Date"
    }
}

# Define the bounding box configuration for each page
BOUNDING_BOX_CONFIG = {
    1: {
        "नाम थर": {"x": 0.5, "y": 0.67, "width": 0.8, "height": 0.025},
        "ठेगाना": {"x": 0.5, "y": 0.70, "width": 0.8, "height": 0.025},
        "मिति": {"x": 0.5, "y": 0.73, "width": 0.8, "height": 0.025}
    },
    2: {
        "नाम थर": {"x": 0.05, "y": 0.34, "width": 0.8, "height": 0.025},
        "लिङ्ग": {"x": 0.05, "y": 0.40, "width": 0.8, "height": 0.025},
        "पेशा": {"x": 0.05, "y": 0.42, "width": 0.8, "height": 0.025},
        "नागरिकता नम्बर": {"x": 0.05, "y": 0.44, "width": 0.8, "height": 0.025},
        "जिल्ला": {"x": 0.05, "y": 0.47, "width": 0.8, "height": 0.025},
        "नगरपालिका वा गा.वि.स.": {"x": 0.05, "y": 0.52, "width": 0.8, "height": 0.025},
        "जन्म मिति": {"x": 0.05, "y": 0.573, "width": 0.8, "height": 0.025},
        "बुवाको नाम": {"x": 0.05, "y": 0.60, "width": 0.8, "height": 0.025},
        "तालिम लिएको स्थान": {"x": 0.06, "y": 0.71, "width": 0.8, "height": 0.025},
        "तालिम मिति": {"x": 0.06, "y": 0.67, "width": 0.8, "height": 0.025}
    },
    3: {
        "नाम थर": {"x": 0.08, "y": 0.55, "width": 0.8, "height": 0.025},
        "ठेगाना": {"x": 0.08, "y": 0.575, "width": 0.8, "height": 0.025}
    },
    4: {
        "नाम थर": {"x": 0.1, "y": 0.18, "width": 0.8, "height": 0.030},
        "जन्म मिति": {"x": 0.1, "y": 0.22, "width": 0.8, "height": 0.025},
        "ठेगाना": {"x": 0.1, "y": 0.25, "width": 0.8, "height": 0.025},
        "बुवाको नाम": {"x": 0.1, "y": 0.388, "width": 0.4, "height": 0.025},
        "लिङ्ग": {"x": 0.5, "y": 0.388, "width": 0.8, "height": 0.025},
        "पेशा": {"x": 0.1, "y": 0.418, "width": 0.8, "height": 0.025},
        "मोबाइल नम्बर": {"x": 0.38, "y": 0.442, "width": 0.24, "height": 0.025},
        "इमेल": {"x": 0.6, "y": 0.442, "width": 0.6, "height": 0.025},
        "प्यान नम्बर": {"x": 0.1, "y": 0.60, "width": 0.4, "height": 0.025},
        "बैंकको नाम": {"x": 0.1, "y": 0.63, "width": 0.5, "height": 0.025},
        "बैंक खाता नम्बर": {"x": 0.1, "y": 0.67, "width": 0.4, "height": 0.025},
        "साइन मिति": {"x": 0.5, "y": 0.69, "width": 0.8, "height": 0.025}
    }
}

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast_enhanced = clahe.apply(blur)
    sharpening_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    sharpened = cv2.filter2D(contrast_enhanced, -1, sharpening_kernel)
    binary = cv2.adaptiveThreshold(sharpened, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY_INV, 11, 2)
    return binary

def encode_image(image):
    _, buffer = cv2.imencode(".jpg", image)
    return base64.b64encode(buffer).decode("utf-8")

def get_prompt_for_page(page_num):
    fields = PAGE_FIELDS.get(page_num, PAGE_FIELDS[1])
    fields_text = "\n".join([f"- {field}" for field in fields.keys()])
    
    prompt = f"""
    कृपया यो छविबाट निम्नलिखित जानकारी निकाल्नुहोस् र प्रत्येक फाँटको पाठलाई स्पष्ट रूपमा छुट्याउनुहोस्।
    प्रत्येक फाँटको नाम र त्यसको मानलाई अलग-अलग लाइनमा लेख्नुहोस्।
    कुनै पनि फाँट खाली भएमा 'नभेटियो' लेख्नुहोस्।

    निम्न फाँटहरूको जानकारी चाहिन्छ:
    {fields_text}

    कृपया प्रत्येक फाँटको जानकारी यस्तो ढाँचामा दिनुहोस्:
    नाम थर: [पाइएको नाम]
    ठेगाना: [पाइएको ठेगाना]
    ...

    सुनिश्चित गर्नुहोस् कि तपाईंले नेपाली भाषामा जानकारी पहिचान गर्नुहन्छ।
    """
    return prompt

def extract_text_from_image(image, page_num=1):
    base64_image = encode_image(image)
    prompt = get_prompt_for_page(page_num)
    
    image_part = {
        "inline_data": {
            "mime_type": "image/jpeg",
            "data": base64_image
        }
    }
    response = model.generate_content([{"text": prompt}, image_part])
    return response.text

def label_text(extracted_text, page_num=1):
    lines = [line.strip() for line in extracted_text.split("\n") if line.strip()]
    fields = PAGE_FIELDS.get(page_num, PAGE_FIELDS[1])
    
    labeled_content = {field: "नभेटियो" for field in fields.keys()}
    
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if key in labeled_content:
                labeled_content[key] = value
    
    return labeled_content

def estimate_bounding_boxes(image, labeled_content, page_num):
    height, width = image.shape[:2]
    boxes = []
    
    page_config = BOUNDING_BOX_CONFIG.get(page_num, {})
    
    for label, content in labeled_content.items():
        if content != "नभेटियो" and label in page_config:
            config = page_config[label]
            x = int(width * config["x"])
            y = int(height * config["y"])
            box_width = int(width * config["width"])
            box_height = int(height * config["height"])
            
            boxes.append({
                'coords': (x, y, box_width, box_height),
                'label': label,
                'content': content
            })
    
    return boxes

def annotate_image_with_boxes(image, labeled_content, page_num):
    result = image.copy()
    height, width = image.shape[:2]
    
    font_scale = max(0.7, min(width / 1000, 1.2))
    thickness = max(2, min(width // 500, 3))
    
    boxes = estimate_bounding_boxes(image, labeled_content, page_num)
    
    box_color = (0, 0, 255)  # Red in BGR
    text_color = (255, 255, 255)  # White in BGR
    bg_color = (0, 0, 0)  # Black background for text
    
    for box in boxes:
        x, y, w, h = box['coords']
        label = box['label']
        content = box['content']
        
        cv2.rectangle(result, (x, y), (x + w, y + h), box_color, thickness)
        
        label_text = LABEL_TRANSLATIONS.get(label, label)
        
        (label_width, label_height), _ = cv2.getTextSize(
            label_text, cv2.FONT_HERSHEY_COMPLEX, font_scale, thickness
        )
        
        cv2.rectangle(
            result,
            (x, y - label_height - 10),
            (x + label_width + 10, y),
            bg_color,
            -1
        )
        
        cv2.putText(
            result,
            label_text,
            (x + 5, y - 5),
            cv2.FONT_HERSHEY_COMPLEX,
            font_scale,
            text_color,
            thickness
        )
        
        try:
            content_text = content if any(ord(c) < 128 for c in content) else "[Nepali Text]"
            (content_width, content_height), _ = cv2.getTextSize(
                content_text, cv2.FONT_HERSHEY_COMPLEX, font_scale, thickness
            )
            
            cv2.rectangle(
                result,
                (x, y + h),
                (x + content_width + 10, y + h + content_height + 10),
                bg_color,
                -1
            )
            
            cv2.putText(
                result,
                content_text,
                (x + 5, y + h + content_height),
                cv2.FONT_HERSHEY_COMPLEX,
                font_scale,
                text_color,
                thickness
            )
        except:
            placeholder = "[Content]"
            cv2.putText(
                result,
                placeholder,
                (x + 5, y + h + 20),
                cv2.FONT_HERSHEY_COMPLEX,
                font_scale,
                text_color,
                thickness
            )
    
    return result 