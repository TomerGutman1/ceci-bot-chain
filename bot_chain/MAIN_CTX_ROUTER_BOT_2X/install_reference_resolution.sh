#!/bin/bash

# Reference Resolution Installation Script for CECI Bot Chain
# Run this script from the MAIN_CTX_ROUTER_BOT_2X directory

set -e  # Exit on any error

echo "🚀 Installing Reference Resolution for CECI Bot Chain"
echo "=============================================="

# Step 1: Verify we're in the right directory
if [[ ! -f "main.py" ]]; then
    echo "❌ Error: main.py not found. Please run this script from MAIN_CTX_ROUTER_BOT_2X directory"
    exit 1
fi

echo "✅ Found main.py - we're in the right directory"

# Step 2: Check if files already exist
echo "📋 Checking for required files..."

REQUIRED_FILES=("reference_config.py" "reference_resolver.py" "simple_test.py")
MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [[ ! -f "$file" ]]; then
        MISSING_FILES+=("$file")
    fi
done

if [[ ${#MISSING_FILES[@]} -gt 0 ]]; then
    echo "❌ Missing required files: ${MISSING_FILES[*]}"
    echo "Please ensure all reference resolution files are in this directory"
    exit 1
fi

echo "✅ All required files present"

# Step 3: Check for reference resolution integration in main.py
echo "🔍 Checking main.py integration..."

if ! grep -q "from reference_resolver import ReferenceResolver" main.py; then
    echo "❌ Error: main.py does not contain reference resolution integration"
    echo "Please use the updated main.py file from the integration package"
    exit 1
fi

echo "✅ main.py contains reference resolution integration"

# Step 4: Test basic functionality
echo "🧪 Testing basic functionality..."

python3 -c "
try:
    from reference_config import reference_config
    print('✅ reference_config import successful')
except Exception as e:
    print(f'❌ reference_config import failed: {e}')
    exit(1)
"

# Run simple tests
echo "🔬 Running simple tests..."
if python3 simple_test.py | grep -q "All simple tests completed"; then
    echo "✅ Simple tests passed"
else
    echo "❌ Simple tests failed"
    exit 1
fi

# Step 5: Check environment variables
echo "⚙️ Checking environment configuration..."

ENV_VARS=("REDIS_URL")
MISSING_ENV=()

for var in "${ENV_VARS[@]}"; do
    if [[ -z "${!var}" ]]; then
        MISSING_ENV+=("$var")
    fi
done

if [[ ${#MISSING_ENV[@]} -gt 0 ]]; then
    echo "⚠️  Warning: Missing environment variables: ${MISSING_ENV[*]}"
    echo "Please set these variables before starting the service:"
    echo "export REDIS_URL=redis://redis:6379"
    echo "export REF_RESOLUTION_ENABLED=true"
fi

# Step 6: Test Redis connectivity (if REDIS_URL is set)
if [[ -n "$REDIS_URL" ]]; then
    echo "🔗 Testing Redis connectivity..."
    if command -v redis-cli >/dev/null 2>&1; then
        if redis-cli -u "$REDIS_URL" ping >/dev/null 2>&1; then
            echo "✅ Redis connection successful"
        else
            echo "⚠️  Warning: Cannot connect to Redis at $REDIS_URL"
            echo "Make sure Redis is running before starting the service"
        fi
    else
        echo "⚠️  Warning: redis-cli not found, cannot test Redis connectivity"
    fi
fi

# Step 7: Create environment file template
echo "📝 Creating environment template..."

cat > .env.reference_resolution << 'EOF'
# Reference Resolution Environment Variables
# Copy these to your main .env file or docker-compose.yml

# Core Settings
REF_RESOLUTION_ENABLED=true
REF_HISTORY_TURNS=20
REF_FUZZY_THRESHOLD=0.6
REF_CLARIFY_ON_FAIL=true
REF_RECENCY_TURNS=3

# Performance
REF_PERF_TARGET_MS=100

# Redis (update with your Redis URL)
REDIS_URL=redis://redis:6379
EOF

echo "✅ Environment template created: .env.reference_resolution"

# Step 8: Final validation
echo "🎯 Final validation..."

python3 -c "
# Test pattern matching
from reference_config import reference_config
patterns = reference_config.get_compiled_patterns()
print(f'✅ {len(patterns)} pattern groups loaded')

# Test Hebrew text
test_text = 'החלטה 2989 של ממשלה 37'
found = 0
for entity_type, entity_patterns in patterns.items():
    for pattern in entity_patterns:
        if pattern.search(test_text):
            found += 1
            break
print(f'✅ Pattern matching: {found}/3 entity types detected')
"

echo ""
echo "🎉 INSTALLATION COMPLETE!"
echo "========================"
echo ""
echo "Next steps:"
echo "1. Copy environment variables from .env.reference_resolution to your main config"
echo "2. Start the Context Router Bot service: python3 main.py"
echo "3. Test the health endpoint: curl http://localhost:8013/health"
echo "4. Look for 'reference_resolver_status': {'status': 'ok'} in the response"
echo ""
echo "For detailed integration instructions, see:"
echo "REFERENCE_RESOLUTION_INTEGRATION_GUIDE.md"
echo ""
echo "🚀 Reference Resolution is ready for production use!"