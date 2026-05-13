import os
import re

BASE_DIR = r'c:\Users\HP\Downloads\JFT_WEBSITE\vics-project'

def propagate_fix():
    print("--- Propagating Products Page Fix ---")
    
    # 1. Read the master (fixed) products.html
    master_path = os.path.join(BASE_DIR, 'products.html')
    with open(master_path, 'r', encoding='utf-8') as f:
        master_content = f.read()
    
    # Extract the script block and CSP
    csp_match = re.search(r'<meta http-equiv="Content-Security-Policy"[\s\S]*?>', master_content)
    script_match = re.search(r'<script>\s+const PRODUCT_DATA = [\s\S]*?</script>', master_content)
    
    if not csp_match or not script_match:
        print("Error: Could not find CSP or Script in master file.")
        return

    csp_text = csp_match.group(0)
    script_text = script_match.group(0)

    # 2. Find all products.html in subfolders
    for root, dirs, files in os.walk(BASE_DIR):
        if root == BASE_DIR: continue # Skip root
        if 'products.html' in files:
            path = os.path.join(root, 'products.html')
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace CSP
            content = re.sub(r'<meta http-equiv="Content-Security-Policy"[\s\S]*?>', csp_text, content)
            
            # Replace Script block
            # Be careful about PRODUCT_DATA if it's localized (but usually it's not)
            content = re.sub(r'<script>\s+const PRODUCT_DATA = [\s\S]*?</script>', script_text, content)
            
            # Ensure pathing is correct (../ prefix)
            # Since we copied from root, we need to add ../ to assets
            if not root.endswith('vics-project'):
                content = content.replace('src="images/', 'src="../images/')
                content = content.replace('href="images/', 'href="../images/')
                content = content.replace('src="assets/', 'src="../assets/')
                content = content.replace('href="assets/', 'href="../assets/')
                content = content.replace('href="index.html"', 'href="../index.html"')
                content = content.replace('href="products.html"', 'href="../products.html"')
                content = content.replace('href="about.html"', 'href="../about.html"')
                content = content.replace('href="contact.html"', 'href="../contact.html"')
                # Fix double ../ if already present
                content = content.replace('../../', '../')
                
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  - Propagated to {os.path.relpath(path, BASE_DIR)}")

if __name__ == "__main__":
    propagate_fix()
