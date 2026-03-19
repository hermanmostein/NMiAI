# Task 1: NorgesGruppen Object Detection Competition

## Competition Overview

**NorgesGruppen Data: Object Detection** - Detect grocery products on store shelves in a sandboxed Docker environment.

### Competition Format
- **Submission**: Upload `.zip` file with model code + weights
- **Execution**: Runs in sandboxed Docker container (NVIDIA L4 GPU, 24GB VRAM, no network access)
- **Scoring**: 70% detection accuracy + 30% classification accuracy
- **Entry Point**: Must include `run.py` that processes shelf images and outputs predictions

## Dataset Details

### Training Data (NM_NGD_coco_dataset.zip, ~864 MB)
- **248 shelf images** from Norwegian grocery stores
- **~22,700 COCO-format bounding box annotations**
- **356 product categories** (category_id 0-355)
- **4 store sections**: Egg, Frokost, Knekkebrod, Varmedrikker
- **Special category**: category_id 356 = "unknown_product"

### Product Reference Images (NM_NGD_product_images.zip, ~60 MB)
- **327 individual products** with multi-angle photos
- **Views available**: main, front, back, left, right, top, bottom
- **Organization**: `{product_code}/main.jpg`, `{product_code}/front.jpg`, etc.
- **Includes**: `metadata.json` with product names and annotation counts

### Annotation Format
```json
{
  "images": [
    {"id": 1, "file_name": "img_00001.jpg", "width": 2000, "height": 1500}
  ],
  "categories": [
    {"id": 0, "name": "VESTLANDSLEFSA TØRRE 10STK 360G", "supercategory": "product"},
    {"id": 356, "name": "unknown_product", "supercategory": "product"}
  ],
  "annotations": [
    {
      "id": 1,
      "image_id": 1,
      "category_id": 42,
      "bbox": [141, 49, 169, 152],  // [x, y, width, height] in pixels
      "area": 25688,
      "iscrowd": 0,
      "product_code": "8445291513365",
      "product_name": "NESCAFE VANILLA LATTE 136G NESTLE",
      "corrected": true  // manually verified annotation
    }
  ]
}
```

**Key Fields:**
- `bbox`: [x, y, width, height] in pixels (COCO format)
- `product_code`: Barcode identifier
- `corrected`: Boolean indicating manually verified annotations

## Competition Constraints

### Execution Environment
- **GPU**: NVIDIA L4, 24GB VRAM
- **Network**: No internet access (sandboxed)
- **Entry Point**: `run.py` must handle inference
- **Packaging**: All code + model weights in single `.zip` file

### Scoring System
- **70% Detection Score**: Did you find the products? (localization accuracy)
- **30% Classification Score**: Did you identify the correct product? (classification accuracy)
- **Target**: ~50% mAP is competitive baseline (from competition examples)

### Critical Requirements
1. **Self-contained**: All dependencies must be included or pre-installed in Docker
2. **Reproducible**: Must work in sandboxed environment without network
3. **Efficient**: Must run within GPU memory constraints (24GB VRAM)
4. **Robust**: Handle 356 product categories + unknown_product class

## Recommended Solution

### Approach: Fine-tuned YOLOv8 Object Detection

**Why YOLOv8?**
- ✅ State-of-the-art accuracy (target: >50% mAP, competitive baseline)
- ✅ Fast inference suitable for competition environment
- ✅ Fits in 24GB VRAM with room for batch processing
- ✅ Self-contained model weights can be packaged in .zip
- ✅ No external dependencies during inference

### Architecture Overview

```
Input: Shelf Image (RGB, variable size)
    ↓
YOLOv8 Backbone (CSPDarknet)
    ↓
Feature Pyramid Network (FPN)
    ↓
Detection Head (356 + 1 classes)
    ↓
Output: [Bounding Boxes, Category IDs (0-356), Confidence Scores]
```

### Key Features

1. **356 Product Classes + Unknown**: Handle all categories including unknown_product (356)
2. **Multi-angle Product Learning**: Utilize reference images for data augmentation
3. **Advanced Data Augmentation**: Mosaic, MixUp, color jittering, rotation
4. **Weighted Scoring**: Optimize for 70% detection + 30% classification split
5. **Sandboxed Inference**: No network calls, all processing local

## Submission Structure

### Required Files for .zip Submission
```
submission.zip
├── run.py                         # Entry point (REQUIRED)
├── model_weights/                 # Trained model weights
│   └── best_model.pt
├── src/                           # Source code
│   ├── models/                    # Model architecture
│   ├── inference/                 # Inference pipeline
│   └── utils/                     # Utilities
├── configs/                       # Configuration files
│   └── inference_config.yaml
└── requirements.txt               # Python dependencies (if needed)
```

### run.py Interface
```python
# run.py must accept shelf images and output predictions
# Expected interface:
def predict(image_path: str) -> List[Dict]:
    """
    Args:
        image_path: Path to shelf image
    
    Returns:
        List of predictions:
        [
            {
                'bbox': [x, y, width, height],  # COCO format
                'category_id': int,              # 0-356
                'score': float                   # confidence
            }
        ]
    """
    pass
```

## Development Project Structure

```
Task1/
├── data/                          # Dataset (not in submission)
│   ├── NM_NGD_coco_dataset/      # Training data
│   │   ├── images/
│   │   └── annotations.json
│   └── NM_NGD_product_images/    # Reference images
├── src/                           # Source code (include in submission)
│   ├── data/                      # Dataset & augmentation
│   ├── models/                    # Model architectures
│   ├── training/                  # Training pipeline
│   ├── inference/                 # Inference & prediction
│   └── utils/                     # Utilities & metrics
├── configs/                       # Configuration files
├── notebooks/                     # Jupyter notebooks for EDA
├── checkpoints/                   # Model checkpoints (best → submission)
├── run.py                         # Submission entry point
├── SOLUTION_APPROACH.md          # Detailed technical approach
├── IMPLEMENTATION_PLAN.md        # Step-by-step implementation guide
└── README.md                      # This file
```

## Implementation Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Phase 1: Data Preparation** | 1-2 days | Data analysis, dataset implementation, augmentation pipeline |
| **Phase 2: Model Development** | 3-5 days | Model architecture (356+1 classes), training setup |
| **Phase 3: Training** | 2-3 days | Model training, hyperparameter tuning, validation |
| **Phase 4: Submission Prep** | 1-2 days | Create run.py, package submission.zip, test locally |
| **Phase 5: Optimization** | 1-2 days | Improve score, optimize for 70/30 split, resubmit |

**Total Estimated Time**: 8-14 days

## Expected Performance

### Competition Targets
- **Baseline**: ~50% mAP (from competition examples)
- **Target**: >60% mAP (competitive performance)
- **Stretch Goal**: >70% mAP (top leaderboard)

### Scoring Breakdown
- **Detection (70%)**: Localization accuracy (IoU-based)
- **Classification (30%)**: Correct product identification
- **Strategy**: Prioritize detection accuracy, then refine classification

### Speed Requirements
- **GPU Inference**: Must run on NVIDIA L4 (24GB VRAM)
- **Batch Processing**: Optimize for throughput on 248 test images
- **Memory**: Stay within 24GB VRAM limit

## Technology Stack

### Core Libraries
- **Deep Learning**: PyTorch, torchvision
- **Object Detection**: Ultralytics YOLOv8, Detectron2
- **Computer Vision**: OpenCV, PIL
- **Data Processing**: NumPy, Pandas, Albumentations
- **Evaluation**: pycocotools, scikit-learn

### Optional Tools
- **Feature Extraction**: timm (PyTorch Image Models)
- **Similarity Search**: FAISS
- **Optimization**: ONNX Runtime, TensorRT
- **Visualization**: Matplotlib, Seaborn, Plotly

## Key Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| **Occlusion** | Multi-scale detection, context modeling |
| **Varying lighting** | Color augmentation, normalization |
| **Different angles** | Use all 5 reference views, rotation augmentation |
| **Scale variation** | Feature Pyramid Network, multi-scale training |
| **Class imbalance** | Focal loss, weighted sampling |
| **Similar products** | Fine-grained features, attention mechanisms |
| **Crowded shelves** | Soft-NMS, improved localization loss (GIoU) |

## Getting Started

### Prerequisites
```bash
# Python 3.8+
# CUDA 11.8+ (for GPU acceleration)
# 16GB+ RAM
# 8GB+ GPU memory (recommended)
```

### Installation
```bash
# Clone repository
cd Task1

# Install dependencies
pip install -r requirements.txt

# Verify data structure
python src/utils/verify_data.py
```

### Quick Start
```bash
# 1. Explore data
jupyter notebook notebooks/01_data_exploration.ipynb

# 2. Train model
python src/main.py --mode train --config configs/yolov8_base.yaml

# 3. Run inference
python src/main.py --mode predict --image path/to/shelf_image.jpg

# 4. Evaluate model
python src/main.py --mode evaluate --checkpoint checkpoints/best_model.pt
```

## Evaluation Metrics

### Primary Metrics
1. **Mean Average Precision (mAP)**
   - mAP@0.5: IoU threshold 0.5
   - mAP@0.75: IoU threshold 0.75
   - mAP@[0.5:0.95]: COCO standard (average over IoU 0.5 to 0.95)

2. **Per-Class Metrics**
   - Precision, Recall, F1-score per product
   - Confusion matrix for error analysis

3. **Detection Quality**
   - Average IoU of correct detections
   - False Positive Rate
   - False Negative Rate

### Secondary Metrics
- Inference speed (FPS)
- Model size (MB)
- Memory usage (GB)

## Alternative Approaches Considered

### 1. Template Matching (Not Recommended)
- ❌ Poor with scale/rotation/lighting changes
- ❌ Very slow for large product databases
- ❌ Not suitable for real-world scenarios

### 2. Traditional CV (SIFT/ORB) (Not Recommended)
- ❌ Fails with occlusion
- ❌ Outdated, deep learning is superior
- ❌ Poor accuracy on complex scenes

### 3. Two-Stage Detection + Matching (Alternative)
- ✅ Better generalization to new products
- ✅ Can handle unseen products
- ❌ Slower inference (two-stage)
- ❌ More complex pipeline

**Verdict**: YOLOv8 is the best balance of accuracy, speed, and simplicity.

## Documentation

- **[SOLUTION_APPROACH.md](SOLUTION_APPROACH.md)**: Comprehensive technical approach with algorithm details
- **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)**: Detailed implementation guide with code examples

## Next Steps

1. **Review this plan** and provide feedback
2. **Verify data availability** (annotations.json location)
3. **Set up development environment**
4. **Begin Phase 1**: Data exploration and preparation
5. **Switch to Code mode** for implementation

## Questions?

Before proceeding with implementation, please confirm:
- [ ] Is the annotations.json file available and accessible?
- [ ] Are there any specific performance requirements (speed vs accuracy trade-off)?
- [ ] Should we prioritize certain product categories?
- [ ] Are there any deployment constraints (edge devices, cloud, etc.)?
- [ ] Do you want to explore the alternative two-stage approach?

---

**Status**: Planning Complete ✅  
**Next**: Ready for implementation in Code mode