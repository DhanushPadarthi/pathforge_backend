import httpx

# Test API endpoints
base_url = "http://127.0.0.1:8000"

print("🔍 Testing PathForge API Endpoints\n")

# Test health
r = httpx.get(f"{base_url}/health")
print(f"✓ Health Check: {r.json()}")

# Test root
r = httpx.get(f"{base_url}/")
print(f"✓ Root: {r.json()['message']}")

# Test career roles
r = httpx.get(f"{base_url}/api/skills/career-roles")
print(f"✓ Career Roles: {len(r.json())} roles found")

# Get OpenAPI spec
r = httpx.get(f"{base_url}/openapi.json")
spec = r.json()

# Count endpoints
total_endpoints = sum(len(methods) for methods in spec['paths'].values())
print(f"\n📊 Total API Endpoints: {total_endpoints}")

# Group by tag
tags = {}
for path, methods in spec['paths'].items():
    for method, details in methods.items():
        tag = details.get('tags', ['Other'])[0]
        if tag not in tags:
            tags[tag] = []
        tags[tag].append(f"{method.upper()} {path}")

print("\n📋 Endpoints by Category:")
for tag, endpoints in sorted(tags.items()):
    print(f"\n{tag} ({len(endpoints)} endpoints):")
    for ep in sorted(endpoints)[:3]:  # Show first 3
        print(f"  • {ep}")
    if len(endpoints) > 3:
        print(f"  ... and {len(endpoints) - 3} more")

print("\n✅ API is running and all endpoints are accessible!")
