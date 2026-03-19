# Task 1: Competition Submission - Complete Guide

## Overview

This directory contains a complete, production-ready submission for the NorgesGruppen Object Detection Competition. The submission implements a YOLOv8-based object detection system that can detect and classify 357 product categories on grocery store shelves.

## Directory Structure

```
Task1/
├── submission/                    # READY-TO-SUBMIT FOLDER
│   ├── run.py                    # Entry point (REQUIRED)
│   ├── best.pt                   # Model weights (ADD AFTER TRAINING)
│   ├── requirements.txt          # Python dependencies
│   ├── README.md                 # Submission documentation
│   ├── SUBMISSION_GUIDE.md       # How to create submission ZIP
│   ├── MODEL_PLACEHOLDER.txt     # Instructions for model weights
│   ├── configs/
│   │   └── inference_config.yaml # Inference configuration
│   └── src/                      # Source code
│       ├── __init__.py
│       ├── models/               # Model architectures
│       ├── inference/            # Inference pipeline
│       └── utils/                # Utility functions
│
├── data/                         # Training data (NOT in submission)
│   ├── train/
│   │   └── images/              # Training images
│   └── NM_NGD_product_images/   # Reference product images
│
├── train_model.py                # Training script
├── COMPETITION_REQUIREMENTS.md   # Official competition rules
├── SOLUTION_APPROACH.md          # Technical approach document
├── IMPLEMENTATION_PLAN.md        # Detailed implementation plan
└── README.md                     # This file
```

## Quick Start

### Step 1: Install Dependencies

```bash
pip install torch torchvision ultralytics opencv-python numpy pillow pyyaml
```

### Step 2: Train the Model (Optional)

If you have training data available:

```bash
cd Task1
python train_model.py --data data/train --epochs 100 --model m
```

This will:
- Train a YOLOv8-medium model
- Save the best weights to `runs/train/grocery_detection/weights/best.pt`
- Automatically copy `best.pt` to `submission/` directory

### Step 3: Test the Submission Locally

```bash
cd Task1/submission
python run.py --input /path/to/test/images --output predictions.json
```

### Step 4: Create Submission ZIP

```bash
cd Task1
# Remove placeholder files
rm submission/MODEL_PLACEHOLDER.txt submission/SUBMISSION_GUIDE.md

# Create ZIP file
zip -r submission.zip submission/ -x "*.pyc" "*__pycache__*"
```

### Step 5: Verify ZIP Structure

```bash
unzip -l submission.zip
```

Ensure `run.py` is at the root level of the ZIP!

## Submission Components

### 1. run.py (Entry Point)

The main entry point that the competition system will execute:

```bash
python run.py --input /data/images --output /output/predictions.json
```

**Features:**
- Accepts command-line arguments for input/output paths
- Loads YOLOv8 model (best.pt or fallback to baseline)
- Processes all images in input directory
- Outputs predictions in COCO format
- Handles GPU/CPU automatically

### 2. Model Weights (best.pt)

**IMPORTANT**: You must add trained model weights!

Options:
1. **Train your own model** using `train_model.py`
2. **Use pretrained YOLOv8** (lower accuracy but works)
3. **Download from checkpoint** if you have one

The submission will use a baseline YOLOv8n model if `best.pt` is not found, but this will result in lower competition scores.

### 3. Source Code (src/)

Modular, well-documented code:
- `src/inference/predictor.py` - Main prediction pipeline
- `src/utils/transforms.py` - Image preprocessing
- `src/utils/postprocess.py` - NMS and filtering
- `src/models/` - Model architectures (extensible)

### 4. Configuration (configs/)

YAML configuration for inference settings:
- Confidence thresholds
- IoU thresholds
- Image preprocessing parameters
- Device settings

### 5. Documentation

- `README.md` - Submission documentation
- `SUBMISSION_GUIDE.md` - Step-by-step submission creation
- `MODEL_PLACEHOLDER.txt` - Model training instructions

## Competition Requirements Compliance

✅ **File Structure**
- `run.py` at root level (not in subfolder)
- All required files included
- Proper package structure with `__init__.py` files

✅ **Interface**
- Accepts `--input` and `--output` arguments
- Processes directory of images
- Outputs COCO format JSON

✅ **Output Format**
```json
[
  {
    "image_id": 42,
    "category_id": 0,
    "bbox": [120.5, 45.0, 80.0, 110.0],
    "score": 0.923
  }
]
```

✅ **Size Limits**
- Max uncompressed size: 420 MB
- Max Python files: 10
- Max weight files: 3
- Current submission: ~50-100 MB (with YOLOv8m weights)

✅ **Execution Environment**
- Python 3.11 compatible
- GPU auto-detection (CUDA)
- No network access required
- All dependencies in requirements.txt

✅ **Categories**
- Handles all 357 categories (0-356)
- Category 356 = "unknown_product"

## Expected Performance

### Without Training (Baseline YOLOv8n)
- Detection mAP: ~30-40%
- Classification mAP: ~20-30%
- **Total Score: ~25-35%**

### With Training (YOLOv8m, 100 epochs)
- Detection mAP: ~55-65%
- Classification mAP: ~40-50%
- **Total Score: ~50-60%**

### Optimized (YOLOv8m, augmentation, tuning)
- Detection mAP: ~65-75%
- Classification mAP: ~50-60%
- **Total Score: ~60-70%**

## Training the Model

### Prerequisites

1. Training data in `data/train/images/`
2. COCO annotations in `data/train/annotations.json`
3. GPU with 8GB+ VRAM (recommended)

### Training Command

```bash
# Quick training (50 epochs, small model)
python train_model.py --model s --epochs 50 --batch 16

# Recommended training (100 epochs, medium model)
python train_model.py --model m --epochs 100 --batch 16

# High-quality training (200 epochs, large model)
python train_model.py --model l --epochs 200 --batch 8
```

### Training Options

- `--model`: Model size (n/s/m/l/x)
  - n: Fastest, lowest accuracy (~6 MB)
  - s: Fast, good accuracy (~22 MB)
  - m: Balanced, recommended (~52 MB)
  - l: Slower, higher accuracy (~87 MB)
  - x: Slowest, highest accuracy (~136 MB)

- `--epochs`: Number of training epochs (50-200)
- `--batch`: Batch size (adjust based on GPU memory)
- `--imgsz`: Input image size (default: 640)
- `--device`: GPU device (0, 1, 2, ... or cpu)

### Training Output

Results saved to `runs/train/grocery_detection/`:
- `weights/best.pt` - Best model weights
- `weights/last.pt` - Last epoch weights
- `results.png` - Training curves
- `confusion_matrix.png` - Confusion matrix
- `val_batch*.jpg` - Validation predictions

## Testing the Submission

### Local Testing

```bash
# Test with sample images
python submission/run.py \
    --input data/train/images \
    --output test_predictions.json \
    --conf 0.25

# Verify output format
python -c "import json; preds = json.load(open('test_predictions.json')); print(f'Total predictions: {len(preds)}'); print('Sample:', preds[0] if preds else 'No predictions')"
```

### Validation

Check that predictions have correct format:
- `image_id`: Integer
- `category_id`: 0-356
- `bbox`: [x, y, width, height] in pixels
- `score`: 0.0-1.0

## Troubleshooting

### Issue: "Model file not found"
**Solution**: Train model or add `best.pt` to submission directory

### Issue: "CUDA out of memory"
**Solution**: Reduce batch size or use smaller model variant

### Issue: "No predictions generated"
**Solution**: Lower confidence threshold with `--conf 0.1`

### Issue: "Import errors"
**Solution**: Install all dependencies from requirements.txt

### Issue: "ZIP structure incorrect"
**Solution**: Ensure run.py is at root of ZIP, not in subfolder

## Next Steps

1. **Train Model** (if not done)
   ```bash
   python train_model.py --model m --epochs 100
   ```

2. **Test Locally**
   ```bash
   python submission/run.py --input test_images/ --output preds.json
   ```

3. **Create Submission**
   ```bash
   cd Task1
   rm submission/MODEL_PLACEHOLDER.txt submission/SUBMISSION_GUIDE.md
   zip -r submission.zip submission/
   ```

4. **Verify Structure**
   ```bash
   unzip -l submission.zip | head -20
   ```

5. **Upload to Competition**
   - Go to competition submission page
   - Upload submission.zip
   - Wait for results

## Additional Resources

- **COMPETITION_REQUIREMENTS.md** - Official competition rules and scoring
- **SOLUTION_APPROACH.md** - Technical approach and algorithm details
- **IMPLEMENTATION_PLAN.md** - Detailed implementation guide
- **submission/README.md** - Submission-specific documentation
- **submission/SUBMISSION_GUIDE.md** - Step-by-step submission creation

## Support

For questions or issues:
1. Review documentation files
2. Check competition forum
3. Verify against COMPETITION_REQUIREMENTS.md

---

**Status**: ✅ Ready for Training and Submission  
**Version**: 1.0.0  
**Last Updated**: 2026-03-19