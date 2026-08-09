py -3 scripts\apply_site_audit_fixes.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
py -3 scripts\add_image_dimensions.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
py -3 scripts\apply_site_audit_fixes.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
py -3 scripts\validate_blog_navigation.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
py -3 -u scripts\audit_website.py
exit $LASTEXITCODE
