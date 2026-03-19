# NorgesGruppen Object Detection Competition - Official Requirements

## Submission Format

### Zip Structure Requirements
```
submission.zip
├── run.py          # REQUIRED at root (not in subfolder!)
├── model.onnx      # Optional: model weights
├── model.pt        # Optional: PyTorch weights
└── utils.py        # Optional: helper code
```

### File Limits
| Limit | Value |
|-------|-------|
| Max zip size (uncompressed) | 420 MB |
| Max files | 1000 |
| Max Python files | 10 |
| Max weight files (.pt, .pth, .onnx, .safetensors, .npy) | 3 |
| Max weight size total | 420 MB |
| Allowed file types | .py, .json, .yaml, .yml, .cfg, .pt, .pth, .onnx, .safetensors, .npy |

### run.py Contract
**Execution Command:**
```bash
python run.py --input /data/images --output /output/predictions.json
```

**Input:**
- `/data/images/` contains JPEG shelf images
- Filename format: `img_XXXXX.jpg` (e.g., `img_00042.jpg`)

**Output:**
Write JSON array to `--output` path:
```json
[
  {
    "image_id": 42,                          // int: from filename (img_00042.jpg → 42)
    "category_id": 0,                        // int: 0-356 (see categories in annotations.json)
    "bbox": [120.5, 45.0, 80.0, 110.0],     // [x, y, w, h] in COCO format
    "score": 0.923                           // float: confidence (0-1)
  }
]
```

### Execution Environment
| Resource | Limit |
|----------|-------|
| Python | 3.11 |
| CPU | 4 vCPU |
| Memory | 8 GB |
| GPU | NVIDIA L4 (24 GB VRAM) |
| CUDA | 12.4 |
| Network | None (fully offline) |
| Timeout | 300 seconds (5 minutes) |

**GPU Auto-Detection:**
- `torch.cuda.is_available()` returns `True`
- GPU is always available, no opt-in needed
- For ONNX: use `["CUDAExecutionProvider", "CPUExecutionProvider"]`

## Dataset Specifications

### Training Data: NM_NGD_coco_dataset.zip (~864 MB)
- **248 shelf images** from Norwegian grocery stores
- **~22,700 bounding box annotations** in COCO format
- **356 product categories** (category_id: 0-355)
- **1 special category**: category_id 356 = "unknown_product"
- **4 store sections**: Egg, Frokost, Knekkebrod, Varmedrikker

### Product Reference Images: NM_NGD_product_images.zip (~60 MB)
- **327 individual products** with multi-angle photography
- **Available views**: main, front, back, left, right, top, bottom
- **File structure**: `{product_code}/main.jpg`, `{product_code}/front.jpg`, etc.
- **Metadata**: `metadata.json` with product names and annotation statistics

### COCO Annotation Format
```json
{
  "images": [
    {
      "id": 1,
      "file_name": "img_00001.jpg",
      "width": 2000,
      "height": 1500
    }
  ],
  "categories": [
    {
      "id": 0,
      "name": "VESTLANDSLEFSA TØRRE 10STK 360G",
      "supercategory": "product"
    },
    {
      "id": 356,
      "name": "unknown_product",
      "supercategory": "product"
    }
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

**Important Fields:**
- `bbox`: [x, y, width, height] in pixels (COCO format, top-left corner)
- `product_code`: Barcode identifier linking to reference images
- `corrected`: Boolean flag for manually verified annotations
- `category_id`: 0-355 for known products, 356 for unknown

## Scoring System

### Weighted Scoring Formula
```
Final Score = (0.70 × Detection mAP) + (0.30 × Classification mAP)
```

### Detection mAP (70% weight)
- **Question**: Did you find the products?
- **Criteria**: Bounding box IoU ≥ 0.5 (category_id ignored)
- **Measurement**: mean Average Precision on localization only
- **Note**: Detection-only submissions (all category_id: 0) score up to 70%

### Classification mAP (30% weight)
- **Question**: Did you identify the right product?
- **Criteria**: IoU ≥ 0.5 AND correct category_id
- **Measurement**: mean Average Precision on correct classification
- **Note**: Product identification adds the remaining 30%

### Performance Benchmarks
- **~50% mAP**: Baseline performance (competitive threshold)
- **>60% mAP**: Strong performance
- **>70% mAP**: Top leaderboard performance

## Submission Requirements

### Required File: run.py
Must implement inference interface that:
1. Accepts shelf image path as input
2. Loads model and performs detection
3. Returns predictions in specified format

```python
# run.py - Required Interface

def predict(image_path: str) -> List[Dict]:
    """
    Perform object detection on a shelf image.
    
    Args:
        image_path: Path to input shelf image (JPG/PNG)
    
    Returns:
        List of detection dictionaries:
        [
            {
                'bbox': [x, y, width, height],  # COCO format (pixels)
                'category_id': int,              # 0-356
                'score': float                   # confidence (0.0-1.0)
            },
            ...
        ]
    
    Notes:
        - bbox must be [x, y, width, height] in pixels (COCO format)
        - category_id must be in range 0-356 (356 = unknown_product)
        - score should reflect detection confidence
        - No network access available during execution
    """
    # Load model (cached/pre-loaded recommended)
    # Preprocess image
    # Run inference
    # Post-process predictions
    # Return formatted results
    pass
```

### Submission Package Structure
```
submission.zip
├── run.py                         # Entry point (REQUIRED)
├── model_weights/                 # Trained model files
│   ├── best_model.pt             # Main model weights
│   └── config.yaml               # Model configuration
├── src/                           # Source code modules
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── detector.py           # Model architecture
│   ├── inference/
│   │   ├── __init__.py
│   │   ├── predictor.py          # Inference pipeline
│   │   └── postprocess.py        # NMS, filtering
│   └── utils/
│       ├── __init__.py
│       └── transforms.py         # Image preprocessing
├── configs/
│   └── inference_config.yaml     # Inference settings
├── requirements.txt               # Python dependencies (optional)
└── README.md                      # Instructions (optional)
```

### Package Size Recommendations
- **Target**: <200MB (model weights + code)
- **Maximum**: <500MB (practical limit)
- **Optimization**: Use model quantization, pruning if needed

## Technical Constraints

### GPU Memory (24GB VRAM)
- Must fit model + batch processing within 24GB
- Recommended: Test with batch_size=1 first, then optimize
- YOLOv8-medium/large should fit comfortably
- Leave headroom for image preprocessing

### No Network Access
- Cannot download pre-trained weights during inference
- Cannot call external APIs
- All dependencies must be pre-installed or included
- Model weights must be in submission package

### Docker Environment
- Pre-installed: PyTorch, TensorFlow, common CV libraries
- Python 3.8+
- CUDA 11.8+
- If using custom dependencies, include in requirements.txt

### Inference Speed
- Not explicitly scored, but must complete in reasonable time
- 248 test images should process in <10 minutes
- Optimize for throughput, not real-time FPS

## Strategy Recommendations

### 1. Prioritize Detection (70% of score)
- Focus on finding all products first
- Use aggressive data augmentation
- Optimize IoU thresholds for detection
- Lower confidence threshold to catch more products

### 2. Then Optimize Classification (30% of score)
- Fine-tune on product-specific features
- Use reference images for hard negative mining
- Handle "unknown_product" (category 356) carefully
- Consider ensemble for classification refinement

### 3. Handle Class Imbalance
- Some products appear frequently, others rarely
- Use weighted loss or focal loss
- Oversample rare products in training
- Consider per-class confidence thresholds

### 4. Leverage Reference Images
- Use for data augmentation (paste products on shelves)
- Create synthetic training data
- Build product embedding database for validation
- Use for hard negative mining

### 5. Optimize for Sandboxed Environment
- Pre-load model in run.py (avoid repeated loading)
- Batch process if possible
- Use efficient image preprocessing
- Test locally in Docker if possible

## Common Pitfalls to Avoid

❌ **Network Dependencies**: Don't rely on downloading anything during inference  
❌ **Large Model Sizes**: Keep submission <500MB  
❌ **Memory Leaks**: Test with multiple images to ensure stable memory usage  
❌ **Wrong Output Format**: Must return COCO format [x, y, w, h], not [x1, y1, x2, y2]  
❌ **Missing Unknown Class**: Must handle category_id 356  
❌ **Overfitting**: 248 images is small - use heavy augmentation  
❌ **Ignoring Detection/Classification Split**: Optimize for 70/30 weighting  

## Validation Strategy

### Local Testing
1. Split 248 images: 200 train, 48 validation
2. Train model on training split
3. Evaluate on validation split
4. Measure both detection mAP and classification accuracy
5. Calculate weighted score: 0.7×mAP + 0.3×classification_acc

### Pre-Submission Checklist
- [ ] Model achieves >50% mAP on validation set
- [ ] Classification accuracy >80% on detected boxes
- [ ] run.py works with sample images
- [ ] Submission package <500MB
- [ ] No network calls in inference code
- [ ] Handles all 357 categories (0-356)
- [ ] Output format is correct COCO format
- [ ] Tested in Docker environment (if possible)

### Iterative Improvement
1. Submit baseline model
2. Check leaderboard score
3. Analyze: Is detection or classification the bottleneck?
4. Improve weak area
5. Resubmit
6. Repeat until satisfied

## Success Metrics

### Minimum Viable Submission
- ✅ Runs without errors in sandboxed environment
- ✅ Produces valid predictions for all test images
- ✅ Achieves >40% mAP (basic functionality)

### Competitive Submission
- ✅ Achieves >50% mAP (beats baseline)
- ✅ Classification accuracy >75%
- ✅ Handles all product categories
- ✅ Robust to various lighting/angles

### Top Leaderboard Submission
- ✅ Achieves >70% mAP
- ✅ Classification accuracy >85%
- ✅ Handles edge cases (occlusion, unknown products)
- ✅ Optimized for 70/30 scoring split

## Next Steps

1. **Download Data**: Get training data and reference images from submit page
2. **Setup Environment**: Configure local GPU environment
3. **Baseline Model**: Train YOLOv8 on 357 classes
4. **Create run.py**: Implement inference interface
5. **Local Validation**: Test on validation split
6. **Package Submission**: Create submission.zip
7. **Submit**: Upload and check leaderboard
8. **Iterate**: Improve based on score feedback

---

**Key Takeaway**: This is a **detection-heavy** competition (70% weight). Prioritize finding all products with good localization, then refine classification accuracy. The 248-image training set is small, so heavy data augmentation and leveraging reference images is critical.