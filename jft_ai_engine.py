import os
import re
import argparse
import json
from datetime import datetime

# Paths
# Portable Paths
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(TOOLS_DIR, '..'))
TEMPLATE_FILE = os.path.join(BASE_DIR, 'blog-basmati-export-guide.html')
BLOG_LIST_FILE = os.path.join(BASE_DIR, 'blog.html')
SITEMAP_SCRIPT = os.path.join(TOOLS_DIR, 'generate_sitemap.py')
TRANS_SCRIPT = os.path.join(TOOLS_DIR, 'generate_hreflang.py')

def generate_slug(title):
    slug = title.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s-]+', '-', slug)
    return f"blog-{slug}"

def update_blog_list(slug, title, cat, lede, date):
    with open(BLOG_LIST_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Add new card to the top of the grid
    card_html = f"""
        <a href="{slug}.html" class="article-card" data-cat="{cat.lower().replace(' ', '-')}">
          <div class="card-img"><div class="card-img-placeholder">📢</div></div>
          <div class="card-body">
            <span class="article-cat">{cat}</span>
            <h3 class="card-title">{title}</h3>
            <p class="card-excerpt">{lede[:150]}...</p>
            <div class="card-meta">
              <span><i class="fa-solid fa-calendar"></i> {date} · 6 min</span>
              <span class="card-read">Read <i class="fa-solid fa-arrow-right"></i></span>
            </div>
          </div>
        </a>"""
    
    marker = '<div class="articles-grid" id="articlesGrid">'
    content = content.replace(marker, marker + card_html)
    
    # 2. Update filter counts (crude but effective)
    def increment_count(match):
        val = int(match.group(1)) + 1
        return f'class="filter-count">{val}</span>'
    
    # Update "All Articles"
    content = re.sub(r'All Articles <span class="filter-count">(\d+)</span>', 
                     lambda m: f'All Articles <span class="filter-count">{int(m.group(1))+1}</span>', content)
    
    # Update specific category
    cat_match = cat.lower().replace(' ', '-')
    if 'buyer-guide' in cat_match: label = "Buyer Guides"
    elif 'market' in cat_match: label = "Market Intelligence"
    else: label = "Compliance & Docs"
    
    content = re.sub(f'{label} <span class="filter-count">(\d+)</span>', 
                     lambda m: f'{label} <span class="filter-count">{int(m.group(1))+1}</span>', content)

    with open(BLOG_LIST_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated blog.html grid and counts.")

def main():
    parser = argparse.ArgumentParser(description="JFT AI Content Engine")
    parser.add_argument("--title", required=True, help="Blog title")
    parser.add_argument("--cat", default="Market Intelligence", help="Category: Buyer's Guide, Market Intelligence, Compliance")
    parser.add_argument("--lede", required=True, help="Short summary/lede")
    parser.add_argument("--content", required=True, help="Main HTML content for the body")
    
    args = parser.parse_args()
    
    date_str = datetime.now().strftime("%b %d, %Y")
    slug = generate_slug(args.title)
    
    # Create the new HTML file
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()
    
    new_page = template
    new_page = new_page.replace("1121 vs 1509 Basmati Rice: Which Variety Should You Import? | JFT Agro Insights", f"{args.title} | JFT Agro Insights")
    new_page = new_page.replace("A complete buyer's guide comparing 1121 Sella, 1121 Steam, 1509 Sella Basmati rice varieties — grain length, cooking quality, FOB price, and best markets for each.", args.lede)
    new_page = new_page.replace("blog-basmati-export-guide.html", f"{slug}.html")
    new_page = new_page.replace("April 1, 2026", date_str)
    new_page = new_page.replace("Buyer's Guide", args.cat)
    new_page = new_page.replace("1121 vs 1509 Basmati Rice: Which Variety Should You Import?</h2>", f"{args.title}</h2>")
    
    # Replace body content
    start_marker = '<div class="article-body">'
    end_marker = '<!-- CTA -->'
    s_idx = new_page.find(start_marker) + len(start_marker)
    e_idx = new_page.find(end_marker)
    if s_idx != -1 and e_idx != -1:
        new_page = new_page[:s_idx] + "\n" + args.content + "\n" + new_page[e_idx:]
    
    output_path = os.path.join(BASE_DIR, f"{slug}.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_page)
    print(f"Created {slug}.html")
    
    # Update Blog List
    update_blog_list(slug, args.title, args.cat, args.lede, date_str)
    
    # Update Sitemap & Translations
    print("Refreshing sitemap and translations...")
    os.system(f"python {SITEMAP_SCRIPT}")
    os.system(f"python {TRANS_SCRIPT}")
    
    print("\n[SUCCESS] New blog post is live in all languages!")

if __name__ == "__main__":
    main()
