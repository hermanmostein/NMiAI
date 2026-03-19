#!/bin/bash
# Optimized Training Pipeline - One-Click Execution

set -e  # Exit on error

echo "========================================================================"
echo "OPTIMIZED GROCERY DETECTION TRAINING PIPELINE"
echo "========================================================================"
echo ""
echo "This script will:"
echo "  1. Prepare dataset (train/val split, organize product images)"
echo "  2. Run optimized training (1-2 hours)"
echo "  3. Copy model to submission folder"
echo "  4. Create submission ZIP"
echo ""
echo "========================================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "data.yaml" ]; then
    echo "❌ Error: Please run this script from the Task1 directory"
    exit 1
fi

# Step 1: Prepare dataset
echo "📊 STEP 1: Preparing Dataset"
echo "========================================================================"
if [ ! -d "data/train_split" ]; then
    echo "Running dataset preparation..."
    python3 training/prepare_dataset.py
    if [ $? -ne 0 ]; then
        echo "❌ Dataset preparation failed"
        exit 1
    fi
else
    echo "✅ Dataset already prepared (data/train_split exists)"
    echo "   To re-prepare, delete data/train_split and run again"
fi

echo ""
echo "========================================================================"
echo "📊 STEP 2: Running Optimized Training"
echo "========================================================================"
echo ""
echo "Configuration:"
echo "  Model: YOLOv8n (nano)"
echo "  Epochs: 100 (with early stopping)"
echo "  Batch Size: 16"
echo "  Device: Auto-detect (MPS/CUDA/CPU)"
echo "  Estimated Time: 1-2 hours on Apple Silicon"
echo ""
echo "Training will start in 5 seconds... (Ctrl+C to cancel)"
sleep 5

# Run training
python3 training/train_optimized.py \
    --data data/train_split/data.yaml \
    --model n \
    --epochs 100 \
    --batch 16 \
    --device auto \
    --name grocery_optimized_$(date +%Y%m%d_%H%M%S)

if [ $? -ne 0 ]; then
    echo "❌ Training failed"
    exit 1
fi

echo ""
echo "========================================================================"
echo "📦 STEP 3: Creating Submission ZIP"
echo "========================================================================"

# Check if model exists in submission folder
if [ ! -f "submission/best.pt" ]; then
    echo "❌ Model not found in submission folder"
    exit 1
fi

# Create submission ZIP
cd submission
rm -f ../submission.zip
zip -r ../submission.zip . -x "*.pyc" "*__pycache__*" "*.md" "*.txt" "SUBMISSION_GUIDE.md"
cd ..

echo ""
echo "========================================================================"
echo "✅ TRAINING PIPELINE COMPLETE!"
echo "========================================================================"
echo ""
echo "📊 Results:"
echo "   Model: submission/best.pt"
echo "   Submission: submission.zip"
echo "   Size: $(du -h submission.zip | cut -f1)"
echo ""
echo "🧪 Test the model:"
echo "   python3 submission/run.py --input test_input --output predictions.json"
echo ""
echo "📤 Upload to competition:"
echo "   Upload submission.zip to the competition platform"
echo ""
echo "========================================================================"

# Made with Bob
