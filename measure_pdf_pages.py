import pypdf
import os
import json

pdf_path = r"C:\NUTRISCAN\DOCUMENTATION\NUTRI_LENS_AI_MAJOR_PROJECT_REPORT.pdf"
reader = pypdf.PdfReader(pdf_path)
total_pages = len(reader.pages)
print(f"Total PDF pages: {total_pages}")

targets = [
    ('c1', 'CHAPTER- I'),
    ('s11', '1.1 INTRODUCTION'),
    ('s12', '1.2 OBJECTIVES OF THE PROJECT'),
    ('s13', '1.3 ORGANIZATION OF THE THESIS'),
    ('c2', 'CHAPTER- II'),
    ('s21', '2.1 LITERATURE SURVEY'),
    ('s22', '2.2 EXISTING WORKS & FOOD LABELING'),
    ('s23', '2.3 LIMITATIONS OF EXISTING WORKS'),
    ('s24', '2.4 ADVANTAGES OF PROPOSED SOLUTION'),
    ('c3', 'CHAPTER- III'),
    ('s31', '3.1 PROBLEM STATEMENT'),
    ('s32', '3.2 SOFTWARE REQUIREMENTS'),
    ('s33', '3.3 HARDWARE REQUIREMENTS'),
    ('c4', 'CHAPTER- IV'),
    ('s41', '4.1 SYSTEM ARCHITECTURE'),
    ('s42', '4.2 USE CASE DIAGRAM'),
    ('s43', '4.3 ACTIVITY DIAGRAM'),
    ('s44', '4.4 SEQUENCE DIAGRAM'),
    ('c5', 'CHAPTER- V'),
    ('s51', '5.1 DATA PREPARATION'),
    ('s52', '5.2 MODEL IMPLEMENTATION'),
    ('s53', '5.3 MODEL EVALUATION METRICS'),
    ('s54', '5.4 EXPERIMENTAL RESULTS'),
    ('s55', '5.5 DEPLOYMENT & USER INTERFACE'),
    ('c6', 'CHAPTER- VI'),
    ('s61', '6.1 KNOWLEDGE BASE VERIFICATION'),
    ('s62', '6.2 TESTING PROCESS'),
    ('s63', '6.3 VALIDATION METRICS'),
    ('c7', 'CHAPTER- VII'),
    ('s71', '7.1 CONCLUSION'),
    ('s72', '7.2 FUTURE SCOPE'),
    ('ref', 'REFERENCES'),
    ('src', 'SOURCE CODE')
]

mapping = {}

# Chapter 1 starts at PDF page 14 (index 13)
for key, target in targets:
    found_page = None
    for p_idx in range(13, len(reader.pages)):
        page = reader.pages[p_idx]
        txt = page.extract_text() or ""
        if target.lower() in txt.lower():
            # Arabic page number is (p_idx + 1) - 13
            arabic_page = (p_idx + 1) - 13
            found_page = str(max(1, arabic_page))
            break
    mapping[key] = found_page or "1"
    print(f"{key:4s} ('{target[:30]}'): PDF Page {int(mapping[key])+13} -> Arabic Page {mapping[key]}")

with open(r"C:\NUTRISCAN\toc_mapping.json", "w") as f:
    json.dump(mapping, f, indent=2)

print("\nSaved accurate TOC mapping to C:\\NUTRISCAN\\toc_mapping.json")
