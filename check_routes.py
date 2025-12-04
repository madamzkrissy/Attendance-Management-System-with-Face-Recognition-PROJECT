#!/usr/bin/env python
"""
Route checker - displays all available routes
"""

from app import app

print("\n" + "="*60)
print("AVAILABLE ROUTES")
print("="*60 + "\n")

routes = []
for rule in app.url_map.iter_rules():
    if rule.endpoint != 'static':
        routes.append({
            'endpoint': rule.endpoint,
            'methods': ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'})),
            'url': str(rule)
        })

# Sort by URL
routes.sort(key=lambda x: x['url'])

for route in routes:
    print(f"{route['url']:<40} [{route['methods']}]")

print("\n" + "="*60)
print(f"Total Routes: {len(routes)}")
print("="*60 + "\n")
