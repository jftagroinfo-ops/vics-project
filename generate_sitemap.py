import os
from datetime import datetime

base_url = 'https://jftagro.com/'
# Portable pathing
directory = os.path.abspath(os.path.dirname(__file__))

xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

today = datetime.now().strftime('%Y-%m-%d')
url_count = 0

# Walk through the directory recursively
for root, dirs, files in os.walk(directory):
    # Exclude hidden directories like .git
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    
    for file in files:
        EXCLUDE = {'header.html','footer.html','inner-page-hero-snippet.html',
                 'seo-universal-head-snippet.html','product-page-template.html',
                 'cookie-consent-snippet.html','thank-you.html','404.html'}
        if file.endswith('.html') and file not in EXCLUDE:
            # Get relative path
            rel_path = os.path.relpath(os.path.join(root, file), directory)
            # Use forward slashes for URLs
            rel_path_url = rel_path.replace(os.sep, '/')
            
            # Map index.html to directory root for cleaner URLs
            if rel_path_url == 'index.html':
                url = base_url
            elif rel_path_url.endswith('/index.html'):
                url = base_url + rel_path_url.replace('index.html', '')
            else:
                url = base_url + rel_path_url
                
            xml_content += '  <url>\n'
            xml_content += f'    <loc>{url}</loc>\n'
            xml_content += f'    <lastmod>{today}</lastmod>\n'
            
            # Priority logic
            if 'index.html' in rel_path_url:
                priority = '1.0'
            elif 'products.html' in rel_path_url:
                priority = '0.9'
            elif '-exporter.html' in rel_path_url or '-supplier.html' in rel_path_url:
                priority = '0.8'
            elif 'blog' in rel_path_url:
                priority = '0.7'
            else:
                priority = '0.5'
                
            xml_content += f'    <priority>{priority}</priority>\n'
            xml_content += '  </url>\n'
            url_count += 1

xml_content += '</urlset>'

with open(os.path.join(directory, 'sitemap.xml'), 'w', encoding='utf-8') as f:
    f.write(xml_content)

print(f'Generated sitemap.xml with {url_count} URLs across all languages.')
