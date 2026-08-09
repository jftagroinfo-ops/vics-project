@echo off
py -3 scripts\apply_site_audit_fixes.py || exit /b 1
py -3 scripts\add_image_dimensions.py || exit /b 1
py -3 scripts\apply_site_audit_fixes.py || exit /b 1
py -3 scripts\validate_blog_navigation.py || exit /b 1
py -3 -u scripts\audit_website.py
