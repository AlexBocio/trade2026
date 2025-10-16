#!/bin/bash
# Cleanup script for Trade2026 directory

echo "🧹 Sanitizing Trade2026 directory..."

cd "C:/ClaudeDesktop_Projects/Trade2026" || exit

# Remove obsolete files
echo "Removing obsolete files..."
rm -f "00_MASTER_INTEGRATION_PLAN.md"  # Too large, replaced by modular approach
rm -f "README_START_HERE.md"           # Redundant with README.md

# Rename clean README
echo "Updating README..."
rm -f "README.md"
mv "README_CLEAN.md" "README.md"

# Verify structure
echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📁 Final structure:"
ls -la

echo ""
echo "📚 Files to keep:"
echo "  - README.md (main guide)"
echo "  - MASTER_PLAN.md (overview)"
echo "  - appendices/ (detailed references)"

echo ""
echo "🎯 Ready for instruction generation!"
