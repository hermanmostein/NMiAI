#!/usr/bin/env python3
"""
Simple YOLOv8 Training Script - Fixed for Competition
Uses existing data.yaml without complex preprocessing
"""

import torch
from ultralytics import YOLO
from pathlib import Path
import shutil

def main():
    print("=" * 70)
    print("YOLOv8 Training for Grocery Detection")
    print("=" * 70)
    
    # Check device
    if torch.backends.mps.is_available():
        device = 'mps'
        print("\n✅ Apple Silicon GPU (MPS) detected")
    elif torch.cuda.is_available():
        device = '0'
        print("\n✅ CUDA GPU detected")
    else:
        device = 'cpu'
        print("\n⚠️  Using CPU")
    
    # Use existing data.yaml
    data_yaml = "data.yaml"
    
    if not Path(data_yaml).exists():
        print(f"❌ Error: {data_yaml} not found!")
        return
    
    print(f"\n📊 Using dataset: {data_yaml}")
    print(f"🎯 Device: {device}")
    
    # Load pretrained YOLOv8 nano model
    print("\n📦 Loading YOLOv8n pretrained model...")
    model = YOLO('yolov8n.pt')
    
    # Training configuration
    print("\n" + "=" * 70)
    print("Training Configuration:")
    print("=" * 70)
    print(f"  Model: YOLOv8n")
    print(f"  Epochs: 100")
    print(f"  Batch Size: 16")
    print(f"  Image Size: 640")
    print(f"  Device: {device}")
    print(f"  Patience: 20 (early stopping)")
    print("=" * 70)
    
    print("\n🚀 Starting training...")
    print("⏱️  Estimated time: 1-2 hours\n")
    
    # Train with simple, robust settings
    try:
        results = model.train(
            data=data_yaml,
            epochs=100,
            batch=16,
            imgsz=640,
            device=device,
            
            # Optimizer settings
            optimizer='AdamW',
            lr0=0.001,
            lrf=0.01,
            momentum=0.937,
            weight_decay=0.0005,
            warmup_epochs=3,
            
            # Loss weights
            box=7.5,
            cls=0.5,
            dfl=1.5,
            
            # Augmentation (moderate)
            hsv_h=0.015,
            hsv_s=0.7,
            hsv_v=0.4,
            degrees=0.0,
            translate=0.1,
            scale=0.5,
            shear=0.0,
            perspective=0.0,
            flipud=0.0,
            fliplr=0.5,
            mosaic=1.0,
            mixup=0.0,
            copy_paste=0.0,
            
            # Training settings
            patience=20,
            save=True,
            save_period=10,
            cache=False,
            workers=8,
            project='runs/detect',
            name='grocery_simple',
            exist_ok=True,
            pretrained=True,
            verbose=True,
            seed=0,
            deterministic=False,
            single_cls=False,
            rect=False,
            cos_lr=True,
            close_mosaic=10,
            amp=True,
            fraction=1.0,
            profile=False,
            freeze=None,
            multi_scale=False,
            overlap_mask=True,
            mask_ratio=4,
            dropout=0.0,
            val=True,
            plots=True
        )
        
        print("\n" + "=" * 70)
        print("✅ TRAINING COMPLETE!")
        print("=" * 70)
        
        # Find best model
        best_model = Path('runs/detect/grocery_simple/weights/best.pt')
        
        if best_model.exists():
            # Copy to submission folder
            submission_model = Path('submission/best.pt')
            shutil.copy(best_model, submission_model)
            print(f"\n✅ Model copied to: {submission_model}")
            print(f"   Size: {submission_model.stat().st_size / 1024 / 1024:.1f} MB")
        else:
            print("\n⚠️  Warning: best.pt not found in expected location")
            print(f"   Check: runs/detect/grocery_simple/weights/")
        
        print("\n📊 Training Results:")
        print(f"   Location: runs/detect/grocery_simple/")
        print(f"   Metrics: runs/detect/grocery_simple/results.csv")
        print(f"   Plots: runs/detect/grocery_simple/results.png")
        
        print("\n🧪 Next Steps:")
        print("   1. Test: python3 submission/run.py --input test_input --output predictions.json")
        print("   2. Create ZIP: bash CREATE_SUBMISSION.sh")
        print("   3. Upload: submission.zip to competition")
        
    except Exception as e:
        print(f"\n❌ Training failed with error:")
        print(f"   {type(e).__name__}: {e}")
        print("\n💡 Try:")
        print("   - Reduce batch size: --batch 8")
        print("   - Check data.yaml is correct")
        print("   - Verify images and labels exist")
        return

if __name__ == '__main__':
    main()

# Made with Bob
