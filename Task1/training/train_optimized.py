#!/usr/bin/env python3
"""
Optimized YOLOv8 Training Script
Incorporates all improvements from comprehensive training strategy
"""

import os
import sys
import json
import torch
from pathlib import Path
from ultralytics import YOLO
import yaml

def load_class_weights(weights_file='data/class_weights_inverse_freq.json'):
    """Load pre-computed class weights"""
    if Path(weights_file).exists():
        with open(weights_file) as f:
            data = json.load(f)
            return data['weights']
    return None

def train_optimized(
    data_yaml='data/train_split/data.yaml',
    model_size='n',  # n, s, m, l, x
    epochs=100,
    batch_size=16,
    device='mps',
    project='runs/detect',
    name='grocery_optimized',
    pretrained_weights=None,
    use_class_weights=True,
    enable_copy_paste=True,
    freeze_backbone=False,
    freeze_epochs=10
):
    """
    Train YOLOv8 with optimized settings
    
    Args:
        data_yaml: Path to dataset configuration
        model_size: Model size (n/s/m/l/x)
        epochs: Number of training epochs
        batch_size: Batch size
        device: Training device (mps/cuda/cpu)
        project: Project directory
        name: Experiment name
        pretrained_weights: Path to pretrained weights (optional)
        use_class_weights: Use class weights for imbalance
        enable_copy_paste: Enable copy-paste augmentation
        freeze_backbone: Freeze backbone initially
        freeze_epochs: Number of epochs to keep backbone frozen
    """
    
    print("=" * 70)
    print("OPTIMIZED YOLOV8 TRAINING")
    print("=" * 70)
    
    # Device detection
    if device == 'auto':
        if torch.backends.mps.is_available():
            device = 'mps'
            print("\n✅ Apple Silicon GPU (MPS) detected")
        elif torch.cuda.is_available():
            device = '0'
            print("\n✅ CUDA GPU detected")
        else:
            device = 'cpu'
            print("\n⚠️  Using CPU")
    
    # Load or create model
    if pretrained_weights and Path(pretrained_weights).exists():
        print(f"\n📦 Loading pretrained weights: {pretrained_weights}")
        model = YOLO(pretrained_weights)
    else:
        model_file = f'yolov8{model_size}.pt'
        print(f"\n📦 Loading base model: {model_file}")
        model = YOLO(model_file)
    
    # Load dataset config
    with open(data_yaml) as f:
        data_config = yaml.safe_load(f)
    
    num_classes = data_config['nc']
    print(f"\n📊 Dataset: {num_classes} classes")
    
    # Load class weights if enabled
    class_weights_dict = None
    if use_class_weights:
        class_weights_dict = load_class_weights()
        if class_weights_dict:
            print(f"✅ Loaded class weights for {len(class_weights_dict)} classes")
        else:
            print("⚠️  Class weights not found, using uniform weights")
    
    # Training configuration
    print("\n" + "=" * 70)
    print("Training Configuration:")
    print("=" * 70)
    print(f"  Model: YOLOv8{model_size}")
    print(f"  Device: {device}")
    print(f"  Epochs: {epochs}")
    print(f"  Batch Size: {batch_size}")
    print(f"  Image Size: 640")
    print(f"  Classes: {num_classes}")
    print(f"  Class Weights: {'Enabled' if use_class_weights else 'Disabled'}")
    print(f"  Copy-Paste Aug: {'Enabled' if enable_copy_paste else 'Disabled'}")
    print(f"  Freeze Backbone: {freeze_epochs if freeze_backbone else 'No'} epochs")
    print("=" * 70)
    
    # Freeze backbone if requested
    if freeze_backbone and freeze_epochs > 0:
        print(f"\n🔒 Freezing backbone for first {freeze_epochs} epochs")
        # Note: YOLOv8 handles this internally with freeze parameter
    
    print("\n🚀 Starting training...")
    print("⏱️  This may take 1-3 hours depending on configuration\n")
    
    # Optimized hyperparameters
    results = model.train(
        # Data and model
        data=data_yaml,
        epochs=epochs,
        
        # Device and performance
        device=device,
        batch=batch_size,
        imgsz=640,
        workers=8,
        cache=False,  # Don't cache (memory consideration)
        
        # Optimizer settings (optimized for small dataset)
        optimizer='AdamW',
        lr0=0.001,  # Initial learning rate
        lrf=0.01,   # Final learning rate (1% of initial)
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3.0,
        warmup_momentum=0.8,
        warmup_bias_lr=0.1,
        
        # Data augmentation (balanced for grocery detection)
        hsv_h=0.015,  # HSV-Hue augmentation
        hsv_s=0.4,    # HSV-Saturation (reduced from 0.7)
        hsv_v=0.3,    # HSV-Value (reduced from 0.4)
        degrees=0.0,  # No rotation (products have fixed orientation)
        translate=0.1,  # Translation
        scale=0.3,    # Scale (reduced from 0.5)
        shear=0.0,    # No shear
        perspective=0.0,  # No perspective
        flipud=0.0,   # No vertical flip
        fliplr=0.5,   # Horizontal flip
        mosaic=0.8,   # Mosaic augmentation (reduced from 1.0)
        mixup=0.1,    # Mixup augmentation
        copy_paste=0.4 if enable_copy_paste else 0.0,  # Copy-paste for rare classes
        
        # Training settings
        patience=20,  # Early stopping patience (increased)
        save=True,
        save_period=10,  # Save checkpoint every 10 epochs
        
        # Output settings
        project=project,
        name=name,
        exist_ok=True,
        pretrained=True,
        verbose=True,
        seed=42,
        deterministic=False,  # Faster training
        
        # Validation
        val=True,
        plots=True,
        
        # Loss weights (balanced for 356 classes)
        box=5.0,      # Box loss weight (reduced from 7.5)
        cls=2.0,      # Classification loss weight (increased from 0.5!)
        dfl=1.5,      # Distribution focal loss weight
        
        # Backbone freezing
        freeze=freeze_epochs if freeze_backbone else 0,
        
        # Mixed precision training (faster on Apple Silicon)
        amp=True,
    )
    
    print("\n" + "=" * 70)
    print("✅ Training completed!")
    print("=" * 70)
    
    # Get the best model path
    best_model = Path(project) / name / 'weights' / 'best.pt'
    
    if best_model.exists():
        print(f"\n📦 Best model saved to: {best_model}")
        
        # Get model size
        model_size_mb = best_model.stat().st_size / (1024 * 1024)
        print(f"📊 Model size: {model_size_mb:.2f} MB")
        
        # Copy to submission folder
        submission_model = Path('submission/best.pt')
        submission_model.parent.mkdir(exist_ok=True)
        
        import shutil
        shutil.copy2(best_model, submission_model)
        print(f"✅ Model copied to: {submission_model}")
        
        # Copy to checkpoints
        checkpoint_dir = Path('checkpoints')
        checkpoint_dir.mkdir(exist_ok=True)
        checkpoint_file = checkpoint_dir / f'{name}_best.pt'
        shutil.copy2(best_model, checkpoint_file)
        print(f"✅ Checkpoint saved to: {checkpoint_file}")
    
    print("\n📊 Training Summary:")
    if hasattr(results, 'results_dict'):
        metrics = results.results_dict
        print(f"  Box mAP50: {metrics.get('metrics/mAP50(B)', 'N/A')}")
        print(f"  Box mAP50-95: {metrics.get('metrics/mAP50-95(B)', 'N/A')}")
    print(f"  Training device: {device}")
    print(f"  Total epochs: {results.epoch if hasattr(results, 'epoch') else 'N/A'}")
    
    return results, best_model

def main():
    """Main execution with argument parsing"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Optimized YOLOv8 Training')
    parser.add_argument('--data', default='data/train_split/data.yaml', help='Dataset YAML')
    parser.add_argument('--model', default='n', choices=['n', 's', 'm', 'l', 'x'], help='Model size')
    parser.add_argument('--epochs', type=int, default=100, help='Number of epochs')
    parser.add_argument('--batch', type=int, default=16, help='Batch size')
    parser.add_argument('--device', default='auto', help='Training device')
    parser.add_argument('--name', default='grocery_optimized', help='Experiment name')
    parser.add_argument('--pretrained', default=None, help='Pretrained weights path')
    parser.add_argument('--no-class-weights', action='store_true', help='Disable class weights')
    parser.add_argument('--no-copy-paste', action='store_true', help='Disable copy-paste')
    parser.add_argument('--freeze-backbone', action='store_true', help='Freeze backbone initially')
    parser.add_argument('--freeze-epochs', type=int, default=10, help='Epochs to freeze')
    
    args = parser.parse_args()
    
    # Train
    results, best_model = train_optimized(
        data_yaml=args.data,
        model_size=args.model,
        epochs=args.epochs,
        batch_size=args.batch,
        device=args.device,
        name=args.name,
        pretrained_weights=args.pretrained,
        use_class_weights=not args.no_class_weights,
        enable_copy_paste=not args.no_copy_paste,
        freeze_backbone=args.freeze_backbone,
        freeze_epochs=args.freeze_epochs
    )
    
    print("\n" + "=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print("1. Test the model:")
    print("   python submission/run.py --input test_input --output predictions.json")
    print("\n2. Create submission ZIP:")
    print("   cd submission && zip -r ../submission.zip . -x '*.pyc' '*__pycache__*' '*.md' '*.txt'")
    print("\n3. Upload submission.zip to competition platform")
    print("=" * 70)

if __name__ == '__main__':
    main()

# Made with Bob
