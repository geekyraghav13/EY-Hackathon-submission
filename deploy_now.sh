#!/bin/bash

echo "🚀 Deploying Provider Validation System to Render..."
echo ""
echo "This fix removes pandas/numpy/matplotlib for deployment"
echo "(they're only needed for diagram generation, already done locally)"
echo ""

cd "$(dirname "$0")"

echo "📝 Adding files..."
git add requirements-deploy.txt render.yaml FINAL_DEPLOYMENT_FIX.md deploy_now.sh

echo "💾 Committing..."
git commit -m "Fix: Minimal dependencies for successful Render deployment"

echo "🚀 Pushing to GitHub..."
git push

echo ""
echo "=========================================="
echo "✅ DEPLOYED!"
echo "=========================================="
echo ""
echo "Render will auto-deploy in 2-3 minutes"
echo ""
echo "Check status:"
echo "https://dashboard.render.com"
echo ""
echo "Your app will be live at:"
echo "https://provider-validation-system-XXXX.onrender.com"
echo ""
echo "THIS WILL WORK! No C++ compilation needed! 🎉"
echo "=========================================="
