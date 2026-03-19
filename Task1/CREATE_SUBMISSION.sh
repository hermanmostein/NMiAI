#!/bin/bash
# Create competition submission ZIP file
# This script ensures proper structure and validates the submission

set -e

echo "=== NorgesGruppen Competition Submission Creator ==="
echo ""

# Check if model exists
if [ ! -f "submission/best.pt" ]; then
    echo "ERROR: Model file 'submission/best.pt' not found!"
    echo "Please copy your trained model:"
    echo "  cp runs/detect/grocery_detection_optimized/weights/best.pt submission/best.pt"
    exit 1
fi

# Check if run.py exists
if [ ! -f "submission/run.py" ]; then
    echo "ERROR: run.py not found in submission folder!"
    exit 1
fi

echo "✓ Model file found ($(du -h submission/best.pt | cut -f1))"
echo "✓ run.py found"
echo ""

# Create submission ZIP
cd submission
echo "Creating submission.zip..."
zip -r ../submission.zip . -x ".*" "__MACOSX/*" "*.pyc" "*__pycache__*"
cd ..

echo ""
echo "=== Submission ZIP Created ==="
echo ""

# Verify ZIP structure
echo "ZIP contents:"
unzip -l submission.zip | head -20
echo ""

# Check ZIP size
ZIP_SIZE=$(du -h submission.zip | cut -f1)
echo "ZIP size: $ZIP_SIZE"
echo ""

# Validate structure
echo "=== Validation ==="
if unzip -l submission.zip | grep -q "^.*run.py$"; then
    echo "✓ run.py is at root level"
else
    echo "✗ ERROR: run.py not at root level!"
    exit 1
fi

if unzip -l submission.zip | grep -q "^.*best.pt$"; then
    echo "✓ best.pt found"
else
    echo "✗ WARNING: best.pt not found in ZIP"
fi

# Count files
FILE_COUNT=$(unzip -l submission.zip | grep -c "^.*\.[a-z]" || true)
echo "✓ Total files: $FILE_COUNT (limit: 1000)"

# Check for disallowed files
if unzip -l submission.zip | grep -qE "\.(md|txt|yaml|yml)$"; then
    echo "✗ WARNING: Found disallowed file types (.md, .txt, .yaml)"
    unzip -l submission.zip | grep -E "\.(md|txt|yaml|yml)$"
else
    echo "✓ No disallowed file types"
fi

echo ""
echo "=== Submission Ready ==="
echo "File: submission.zip"
echo "Size: $ZIP_SIZE"
echo ""
echo "Next steps:"
echo "1. Test locally: python submission/run.py --input test_input --output predictions.json"
echo "2. Upload submission.zip to competition platform"
echo ""

# Made with Bob
