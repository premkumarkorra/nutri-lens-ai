import os, time

docs = [
    r"C:\NUTRISCAN\DOCUMENTATION\ANSAI_TEMPLATE_WITH_LOGOS.docx",
    r"C:\NUTRISCAN\DOCUMENTATION\NUTRI_LENS_AI_MAJOR_PROJECT_REPORT.docx",
    r"C:\NUTRISCAN\DOCUMENTATION\ANSAI_TEMPLATE_WITH_LOGOS.pdf",
    r"C:\NUTRISCAN\DOCUMENTATION\NUTRI_LENS_AI_MAJOR_PROJECT_REPORT.pdf"
]

print("=== FINAL DELIVERABLES VERIFICATION ===")
for d in docs:
    sz = os.path.getsize(d)
    mtime = time.ctime(os.path.getmtime(d))
    print(f"{os.path.basename(d):45s} | Size: {sz:8d} bytes | Modified: {mtime}")
