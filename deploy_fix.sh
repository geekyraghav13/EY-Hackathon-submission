#!/bin/bash

echo "🔧 Fixing Render Deployment Issue..."
echo ""

# Navigate to project directory
cd "$(dirname "$0")"

echo "✅ Files already updated:"
echo "   - runtime.txt → python-3.11.0"
echo "   - requirements.txt → pandas 2.2.0, numpy 1.26.4"
echo ""

echo "📝 Committing changes..."
git add runtime.txt requirements.txt RENDER_DEPLOYMENT_FIX.md deploy_fix.sh

git commit -m "Fix: Update Python to 3.11 and pandas to 2.2.0 for Render compatibility"

echo ""
echo "🚀 Pushing to GitHub..."
git push

echo ""
echo "=========================================="
echo "✅ Fix Deployed!"
echo "=========================================="
echo ""
echo "Render will automatically redeploy in 3-5 minutes."
echo ""
echo "Check deployment status:"
echo "https://dashboard.render.com"
echo ""
echo "Your app will be available at:"
echo "https://provider-validation-system-XXXX.onrender.com"
echo ""
echo "=========================================="
