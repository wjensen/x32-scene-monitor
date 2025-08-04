#!/usr/bin/env python3
"""
Extract OSC specifications from X32-OSC.pdf
"""

import PyPDF2
import sys

def extract_pdf_text(pdf_path):
    """Extract text from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            print(f"PDF has {len(pdf_reader.pages)} pages")
            
            # Extract text from first few pages to understand structure
            text = ""
            for i, page in enumerate(pdf_reader.pages[:10]):  # First 10 pages
                page_text = page.extract_text()
                text += f"\n--- PAGE {i+1} ---\n"
                text += page_text
                text += "\n"
                
            return text
            
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None

if __name__ == "__main__":
    pdf_path = "X32-OSC.pdf"
    
    print("Extracting OSC specifications from X32-OSC.pdf...")
    text = extract_pdf_text(pdf_path)
    
    if text:
        # Save to text file
        output_file = "X32_OSC_Specifications.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"Extracted text saved to {output_file}")
        print(f"Extracted {len(text)} characters")
        
        # Show first 1000 characters as preview
        print("\n--- PREVIEW ---")
        print(text[:1000])
        print("...")
    else:
        print("Failed to extract text from PDF") 