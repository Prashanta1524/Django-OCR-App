from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import cv2
import numpy as np
import fitz
import os
import tempfile
from .models import Page1, Page2, Page3, Page4
from .utils import (
    preprocess_image, extract_text_from_image, label_text,
    annotate_image_with_boxes, PAGE_FIELDS
)
import base64

def home(request):
    return render(request, 'ocrapp/home.html')

def view_data(request):
    # Fetch data from all tables
    page1_data = Page1.objects.all()
    page2_data = Page2.objects.all()
    page3_data = Page3.objects.all()
    page4_data = Page4.objects.all()
    
    context = {
        'page1_data': page1_data,
        'page2_data': page2_data,
        'page3_data': page3_data,
        'page4_data': page4_data,
    }
    return render(request, 'ocrapp/view_data.html', context)

@csrf_exempt
def process_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_file = request.FILES['image']
        page_num = int(request.POST.get('page_num', 1))
        
        # Save the uploaded file temporarily
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_path = temp_file.name
        with open(temp_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        
        try:
            if uploaded_file.name.lower().endswith('.pdf'):
                # Use 'with' to ensure the document is properly closed
                with fitz.open(temp_path) as doc:
                    results = []
                    for page_num in range(doc.page_count):
                        actual_page = page_num + 1
                        page = doc[page_num]
                        pix = page.get_pixmap()
                        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
                        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                        
                        # Process the image
                        preprocessed_image = preprocess_image(img)
                        extracted_text = extract_text_from_image(preprocessed_image, actual_page)
                        labeled_content = label_text(extracted_text, actual_page)
                        annotated_image = annotate_image_with_boxes(img.copy(), labeled_content, actual_page)
                        
                        # Save the annotated image
                        _, buffer = cv2.imencode('.jpg', annotated_image)
                        annotated_image_base64 = base64.b64encode(buffer).decode('utf-8')
                        
                        # Save to database
                        save_to_database(actual_page, labeled_content)
                        
                        results.append({
                            'page': actual_page,
                            'content': labeled_content,
                            'annotated_image': annotated_image_base64
                        })
                
                return JsonResponse({'success': True, 'results': results})
            
            else:
                # Handle single image
                img = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), 1)
                
                # Process the image
                preprocessed_image = preprocess_image(img)
                extracted_text = extract_text_from_image(preprocessed_image, page_num)
                labeled_content = label_text(extracted_text, page_num)
                annotated_image = annotate_image_with_boxes(img.copy(), labeled_content, page_num)
                
                # Save the annotated image
                _, buffer = cv2.imencode('.jpg', annotated_image)
                annotated_image_base64 = base64.b64encode(buffer).decode('utf-8')
                
                # Save to database
                save_to_database(page_num, labeled_content)
                
                return JsonResponse({
                    'success': True,
                    'content': labeled_content,
                    'annotated_image': annotated_image_base64
                })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)  # Ensure the file is deleted
                except Exception as cleanup_error:
                    print(f"Error during cleanup: {cleanup_error}")
    
    return JsonResponse({'success': False, 'error': 'No file uploaded'})

def save_to_database(page_num, labeled_content):
    if page_num == 1:
        Page1.objects.create(
            full_name=labeled_content.get("नाम थर", "नभेटियो"),
            address=labeled_content.get("ठेगाना", "नभेटियो"),
            date=labeled_content.get("मिति", "नभेटियो")
        )
    elif page_num == 2:
        Page2.objects.create(
            full_name=labeled_content.get("नाम थर", "नभेटियो"),
            gender=labeled_content.get("लिङ्ग", "नभेटियो"),
            occupation=labeled_content.get("पेशा", "नभेटियो"),
            citizenship_number=labeled_content.get("नागरिकता नम्बर", "नभेटियो"),
            district=labeled_content.get("जिल्ला", "नभेटियो"),
            municipality_or_vdc=labeled_content.get("नगरपालिका वा गा.वि.स.", "नभेटियो"),
            date_of_birth=labeled_content.get("जन्म मिति", "नभेटियो"),
            fathers_name=labeled_content.get("बुवाको नाम", "नभेटियो"),
            training_place=labeled_content.get("तालिम लिएको स्थान", "नभेटियो"),
            training_date=labeled_content.get("तालिम मिति", "नभेटियो")
        )
    elif page_num == 3:
        Page3.objects.create(
            full_name=labeled_content.get("नाम थर", "नभेटियो"),
            address=labeled_content.get("ठेगाना", "नभेटियो")
        )
    elif page_num == 4:
        Page4.objects.create(
            full_name=labeled_content.get("नाम थर", "नभेटियो"),
            date_of_birth=labeled_content.get("जन्म मिति", "नभेटियो"),
            address=labeled_content.get("ठेगाना", "नभेटियो"),
            fathers_name=labeled_content.get("बुवाको नाम", "नभेटियो"),
            gender=labeled_content.get("लिङ्ग", "नभेटियो"),
            occupation=labeled_content.get("पेशा", "नभेटियो"),
            mobile_number=labeled_content.get("मोबाइल नम्बर", "नभेटियो"),
            email=labeled_content.get("इमेल", "नभेटियो"),
            pan_number=labeled_content.get("प्यान नम्बर", "नभेटियो"),
            bank_name=labeled_content.get("बैंकको नाम", "नभेटियो"),
            bank_account_number=labeled_content.get("बैंक खाता नम्बर", "नभेटियो"),
            signed_date=labeled_content.get("साइन मिति", "नभेटियो")
        )