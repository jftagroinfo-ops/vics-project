import os

BASE_DIR = r'c:\Users\HP\Downloads\JFT_WEBSITE\vics-project'
SUBDIRS = ['ar', 'fr', 'vi', 'ms', 'id', 'th', 'si', 'ru', 'es', 'pt']

def fix_errors():
    print("--- Fixing Audit Errors ---")
    
    # 1. Fix INFRASTRUCTURE typo
    print("Fixing double folder typos...")
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                new_content = content.replace('images/INFRASTRUCTURE/INFRASTRUCTURE/', 'images/INFRASTRUCTURE/')
                new_content = new_content.replace('images/INFRASTRUCTURE/INFRASTRUCTURE', 'images/INFRASTRUCTURE')
                
                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"  - Fixed typo in {file}")

    # 2. Fix Header/Footer paths in subdirectories
    print("Fixing Component paths in subdirectories...")
    for sub in SUBDIRS:
        sub_path = os.path.join(BASE_DIR, sub)
        if not os.path.exists(sub_path): continue
        
        for file in os.listdir(sub_path):
            if file.endswith('.html'):
                path = os.path.join(sub_path, file)
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Fix fetch calls
                new_content = content.replace("loadComp('header-placeholder','header.html')", "loadComp('header-placeholder','../header.html')")
                new_content = new_content.replace("loadComp('footer-placeholder','footer.html')", "loadComp('footer-placeholder','../footer.html')")
                
                # Fix canonical tags (they should point to the absolute root)
                # But for now, just making sure they aren't broken relative ones
                
                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"  - Fixed paths in {sub}/{file}")

    print("--- Fixes Complete ---")

if __name__ == "__main__":
    fix_errors()
