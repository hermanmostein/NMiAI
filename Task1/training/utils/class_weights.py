#!/usr/bin/env python3
"""
Class Weights Computation
Computes class weights for handling imbalanced dataset
"""

import json
import numpy as np
from collections import Counter
from pathlib import Path

def compute_class_weights(
    annotations_file='data/train/annotations.json',
    method='inverse_freq',
    smooth=1.0
):
    """
    Compute class weights for imbalanced dataset
    
    Args:
        annotations_file: COCO format annotations
        method: 'inverse_freq', 'effective_samples', or 'focal'
        smooth: Smoothing factor to prevent extreme weights
    
    Returns:
        dict: class_id -> weight
    """
    
    print("=" * 70)
    print("CLASS WEIGHTS COMPUTATION")
    print("=" * 70)
    
    # Load annotations
    with open(annotations_file) as f:
        coco_data = json.load(f)
    
    # Count samples per class
    class_counts = Counter(ann['category_id'] for ann in coco_data['annotations'])
    total_samples = sum(class_counts.values())
    num_classes = len(coco_data['categories'])
    
    print(f"\n📊 Dataset Statistics:")
    print(f"   Total classes: {num_classes}")
    print(f"   Total samples: {total_samples}")
    print(f"   Avg samples per class: {total_samples / num_classes:.1f}")
    
    # Compute weights based on method
    weights = {}
    
    if method == 'inverse_freq':
        # Weight = total_samples / (num_classes * class_count)
        for cls_id in range(num_classes):
            count = class_counts.get(cls_id, 0)
            if count > 0:
                weights[cls_id] = total_samples / (num_classes * count)
            else:
                weights[cls_id] = 1.0
    
    elif method == 'effective_samples':
        # Effective number of samples: (1 - beta^n) / (1 - beta)
        beta = 0.9999
        for cls_id in range(num_classes):
            count = class_counts.get(cls_id, 0)
            if count > 0:
                effective_num = (1.0 - np.power(beta, count)) / (1.0 - beta)
                weights[cls_id] = 1.0 / effective_num
            else:
                weights[cls_id] = 1.0
    
    elif method == 'focal':
        # Focal loss style: weight = 1 / sqrt(count)
        for cls_id in range(num_classes):
            count = class_counts.get(cls_id, 0)
            if count > 0:
                weights[cls_id] = 1.0 / np.sqrt(count)
            else:
                weights[cls_id] = 1.0
    
    # Apply smoothing
    if smooth > 0:
        max_weight = max(weights.values())
        for cls_id in weights:
            weights[cls_id] = (weights[cls_id] + smooth) / (max_weight + smooth)
    
    # Normalize weights
    weight_sum = sum(weights.values())
    for cls_id in weights:
        weights[cls_id] = weights[cls_id] * num_classes / weight_sum
    
    # Statistics
    weight_values = list(weights.values())
    print(f"\n⚖️  Weight Statistics ({method}):")
    print(f"   Mean: {np.mean(weight_values):.3f}")
    print(f"   Std: {np.std(weight_values):.3f}")
    print(f"   Min: {np.min(weight_values):.3f}")
    print(f"   Max: {np.max(weight_values):.3f}")
    
    # Show examples
    sorted_by_count = sorted(class_counts.items(), key=lambda x: x[1])
    print(f"\n📋 Example Weights:")
    print(f"   Rarest classes:")
    for cls_id, count in sorted_by_count[:5]:
        print(f"      Class {cls_id} ({count} samples): weight = {weights[cls_id]:.3f}")
    print(f"   Most common classes:")
    for cls_id, count in sorted_by_count[-5:]:
        print(f"      Class {cls_id} ({count} samples): weight = {weights[cls_id]:.3f}")
    
    # Save weights
    output_file = Path('data') / f'class_weights_{method}.json'
    with open(output_file, 'w') as f:
        json.dump({
            'method': method,
            'smooth': smooth,
            'weights': weights,
            'class_counts': dict(class_counts),
            'statistics': {
                'mean': float(np.mean(weight_values)),
                'std': float(np.std(weight_values)),
                'min': float(np.min(weight_values)),
                'max': float(np.max(weight_values))
            }
        }, f, indent=2)
    
    print(f"\n💾 Weights saved to: {output_file}")
    
    return weights

def compare_methods(annotations_file='data/train/annotations.json'):
    """Compare different weighting methods"""
    
    print("\n" + "=" * 70)
    print("COMPARING WEIGHTING METHODS")
    print("=" * 70)
    
    methods = ['inverse_freq', 'effective_samples', 'focal']
    
    for method in methods:
        print(f"\n{'='*70}")
        weights = compute_class_weights(annotations_file, method=method)
    
    print("\n" + "=" * 70)
    print("✅ COMPARISON COMPLETE")
    print("=" * 70)
    print("\nRecommendation:")
    print("- Use 'inverse_freq' for balanced weighting")
    print("- Use 'effective_samples' for extreme imbalance")
    print("- Use 'focal' for moderate imbalance")

def main():
    """Main execution"""
    
    # Compute weights with different methods
    compare_methods()
    
    print("\nNext steps:")
    print("1. Review generated weight files in data/")
    print("2. Choose appropriate method for your training")
    print("3. Load weights in training script")

if __name__ == '__main__':
    main()

# Made with Bob
