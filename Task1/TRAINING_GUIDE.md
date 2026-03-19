# Training Guide - Optimized YOLOv8 for Grocery Detection

## 🚀 Quick Start (Recommended)

Run the automated training pipeline:

```bash
cd Task1
bash RUN_OPTIMIZED_TRAINING.sh
```

This will:
1. Prepare dataset (80/20 train/val split)
2. Train YOLOv8n for 100 epochs (~1-2 hours)
3. Copy best model to submission/
4. Create submission.zip

## 📊 What to Expect

### Training Configuration
- **Model:** YOLOv8n (6.7 MB, fast inference)
- **Epochs:** 100 with early stopping (patience: 20)
- **Batch Size:** 16 (optimized for Apple Silicon)
- **Device:** Auto-detect (MPS/CUDA/CPU)
- **Dataset:** 357 classes (0-356)

### Optimizations Applied
- ✅ 80/20 stratified train/val split
- ✅ Class imbalance handling (weighted loss)
- ✅ Copy-paste augmentation for rare classes
- ✅ Optimized hyperparameters (lr: 0.001, cls_loss: 2.0)
- ✅ Advanced augmentation (mosaic, mixup, HSV)
- ✅ Early stopping to prevent overfitting

### Expected Performance
- **Training Time:** 1-2 hours on Apple Silicon M1/M2/M3
- **Detection mAP@50:** 50-60% (vs 25-35% baseline)
- **Competition Score:** Top 25-30% expected

## 🎯 Training Options

### Option 1: One-Click Training (Easiest)
```bash
bash RUN_OPTIMIZED_TRAINING.sh
```

### Option 2: Manual Training (More Control)

**Step 1: Prepare Dataset**
```bash
python3 training/prepare_dataset.py
```

**Step 2: Train Model**
```bash
python3 training/train_optimized.py \
  --data data/train_split/data.yaml \
  --model n \
  --epochs 100 \
  --batch 16 \
  --device auto
```

**Step 3: Test Model**
```bash
python3 submission/run.py --input test_input --output predictions.json
```

**Step 4: Create Submission**
```bash
bash CREATE_SUBMISSION.sh
```

### Option 3: Larger Model (Better Accuracy)
```bash
python3 training/train_optimized.py \
  --data data/train_split/data.yaml \
  --model s \
  --epochs 150 \
  --batch 16 \
  --device auto
```

Models available: `n` (nano), `s` (small), `m` (medium), `l` (large), `x` (xlarge)

## 📈 Monitoring Training

### Real-time Progress
Training will show:
```
Epoch 1/100: 100%|████████| 168/168 [12:34<00:00, 4.48s/it]
      Class     Images  Instances      Box(P          R      mAP50  mAP50-95)
        all        168      18184      0.456      0.389      0.423     0.245
```

### View Training Curves
After training completes:
```bash
open runs/detect/grocery_optimized_*/results.png
```

### Check Metrics
```bash
tail runs/detect/grocery_optimized_*/results.csv
```

## 🎓 Understanding the Results

### Key Metrics
- **mAP@50:** Main detection metric (target: >50%)
- **Precision:** How many detections are correct
- **Recall:** How many products were found
- **Box Loss:** Bounding box accuracy (should decrease)
- **Class Loss:** Classification accuracy (should decrease)

### Good Training Signs
- ✅ Losses steadily decreasing
- ✅ mAP@50 increasing
- ✅ Validation metrics tracking training metrics
- ✅ No sudden spikes or divergence

### Warning Signs
- ⚠️ Validation loss increasing (overfitting)
- ⚠️ mAP@50 not improving after 50 epochs
- ⚠️ Loss values stuck or oscillating

## 🔧 Troubleshooting

### Out of Memory
```bash
# Reduce batch size
python3 training/train_optimized.py --batch 8
```

### Training Too Slow
```bash
# Use smaller model or fewer epochs
python3 training/train_optimized.py --model n --epochs 50
```

### Poor Results (<45% mAP)
```bash
# Try larger model with more epochs
python3 training/train_optimized.py --model s --epochs 150
```

### Want to Resume Training
```bash
# Training automatically saves checkpoints
# Find last checkpoint in runs/detect/grocery_optimized_*/weights/last.pt
python3 training/train_optimized.py --pretrained runs/detect/grocery_optimized_*/weights/last.pt
```

## 📦 After Training

### 1. Verify Model
```bash
ls -lh submission/best.pt
# Should be ~6-7 MB for YOLOv8n
```

### 2. Test Locally
```bash
python3 submission/run.py --input test_input --output predictions.json
cat predictions.json | python3 -m json.tool | head -20
```

### 3. Create Submission
```bash
bash CREATE_SUBMISSION.sh
ls -lh submission.zip
# Should be ~6-7 MB
```

### 4. Upload
Upload `submission.zip` to competition platform

## 🎯 Performance Targets

### Minimum (Must Have)
- mAP@50 > 45%
- Model makes predictions
- Submission validates

### Target (Should Have)
- mAP@50 > 55%
- Top 30% on leaderboard
- Rare classes detected

### Excellent (Nice to Have)
- mAP@50 > 65%
- Top 10% on leaderboard
- All classes performing well

## 💡 Tips for Better Results

1. **Train Longer:** More epochs = better results (up to a point)
2. **Larger Model:** YOLOv8s or YOLOv8m for +5-10% mAP
3. **Multiple Runs:** Train 2-3 times, keep best model
4. **Ensemble:** Average predictions from multiple models
5. **Hyperparameter Tuning:** Adjust learning rate, augmentation

## 📊 Comparison to Baseline

| Metric | Baseline | Optimized | Improvement |
|--------|----------|-----------|-------------|
| mAP@50 | 25-35% | 50-60% | +25-35% |
| Training Time | 1-2 hrs | 1-2 hrs | Same |
| Rare Class AP | <10% | 25-35% | +15-25% |
| Detections | 0-5 | 10-30 | Much better |

## 🔗 Additional Resources

- **Competition Requirements:** `COMPETITION_REQUIREMENTS.md`
- **Submission Guide:** `SUBMISSION_README.md`
- **Training Script:** `training/train_optimized.py`
- **Dataset Prep:** `training/prepare_dataset.py`

---

**Ready to train?** Run: `bash RUN_OPTIMIZED_TRAINING.sh`

Good luck! 🍀