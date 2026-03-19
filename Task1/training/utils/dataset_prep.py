#!/usr/bin/env python3
"""
Dataset Preparation Script
Creates stratified train/val split ensuring all classes are represented
"""

import json
import shutil
from pathlib import Path
from collections import Counter, defaultdict
import random
import numpy as np

def create_train_val_split(
    images_dir='data/train/images',
    labels_dir='data/train/labels',
    annotations_file='data/train/annotations.json',
    output_dir='data/train_split',
    val_ratio=0.2,
    seed=42
):
    """
    Create stratified train/val split
    
    Args:
        images_dir: Directory containing training images
        labels_dir: Directory containing YOLO format labels
        annotations_file: COCO format annotations
        output_dir: Output directory for split
        val_ratio: Validation set ratio (default 0.2 = 20%)
        seed: Random seed for reproducibility
    """
    random.seed(seed)
    np.random.seed(seed)
    
    print("=" * 70)
    print("DATASET PREPARATION - Train/Val Split")
    print("=" * 70)
    
    # Load annotations
    print(f"\n📂 Loading annotations from {annotations_file}")
    with open(annotations_file) as f:
        coco_data = json.load(f)
    
    # Build image info
    image_info = {img['id']: img for img in coco_data['images']}
    print(f"   Total images: {len(image_info)}")
    
    # Group annotations by image
    annotations_by_image = defaultdict(list)
    for ann in coco_data['annotations']:
        annotations_by_image[ann['image_id']].append(ann)
    
    # Count classes per image
    class_counts = Counter()
    image_classes = {}
    for img_id, anns in annotations_by_image.items():
        classes = set(ann['category_id'] for ann in anns)
        image_classes[img_id] = classes
        class_counts.update(classes)
    
    print(f"   Total annotations: {len(coco_data['annotations'])}")
    print(f"   Total classes: {len(class_counts)}")
    print(f"   Classes with <10 samples: {sum(1 for c in class_counts.values() if c < 10)}")
    
    # Stratified split - ensure rare classes in both sets
    rare_classes = {cls for cls, count in class_counts.items() if count < 10}
    print(f"\n🎯 Rare classes (<10 samples): {len(rare_classes)}")
    
    # Find images containing rare classes
    images_with_rare = []
    images_without_rare = []
    
    for img_id, classes in image_classes.items():
        if classes & rare_classes:
            images_with_rare.append(img_id)
        else:
            images_without_rare.append(img_id)
    
    print(f"   Images with rare classes: {len(images_with_rare)}")
    print(f"   Images without rare classes: {len(images_without_rare)}")
    
    # Split rare class images (ensure both sets get some)
    random.shuffle(images_with_rare)
    val_size_rare = max(1, int(len(images_with_rare) * val_ratio))
    val_images_rare = set(images_with_rare[:val_size_rare])
    train_images_rare = set(images_with_rare[val_size_rare:])
    
    # Split remaining images
    random.shuffle(images_without_rare)
    val_size_normal = int(len(images_without_rare) * val_ratio)
    val_images_normal = set(images_without_rare[:val_size_normal])
    train_images_normal = set(images_without_rare[val_size_normal:])
    
    # Combine
    train_images = train_images_rare | train_images_normal
    val_images = val_images_rare | val_images_normal
    
    print(f"\n📊 Split Statistics:")
    print(f"   Training images: {len(train_images)} ({len(train_images)/len(image_info)*100:.1f}%)")
    print(f"   Validation images: {len(val_images)} ({len(val_images)/len(image_info)*100:.1f}%)")
    
    # Verify all classes represented
    train_classes = set()
    val_classes = set()
    for img_id in train_images:
        train_classes.update(image_classes.get(img_id, set()))
    for img_id in val_images:
        val_classes.update(image_classes.get(img_id, set()))
    
    print(f"\n✅ Class Coverage:")
    print(f"   Train classes: {len(train_classes)}")
    print(f"   Val classes: {len(val_classes)}")
    print(f"   Classes only in train: {len(train_classes - val_classes)}")
    print(f"   Classes only in val: {len(val_classes - train_classes)}")
    
    # Copy files
    print(f"\n📁 Copying files to {output_dir}")
    
    images_path = Path(images_dir)
    labels_path = Path(labels_dir)
    output_path = Path(output_dir)
    
    # Create directories
    train_img_dir = output_path / 'train' / 'images'
    train_lbl_dir = output_path / 'train' / 'labels'
    val_img_dir = output_path / 'val' / 'images'
    val_lbl_dir = output_path / 'val' / 'labels'
    
    for d in [train_img_dir, train_lbl_dir, val_img_dir, val_lbl_dir]:
        d.mkdir(parents=True, exist_ok=True)
    
    # Copy training files
    print("   Copying training set...")
    for img_id in train_images:
        img_info = image_info[img_id]
        img_file = images_path / img_info['file_name']
        lbl_file = labels_path / (Path(img_info['file_name']).stem + '.txt')
        
        if img_file.exists():
            shutil.copy2(img_file, train_img_dir / img_info['file_name'])
        if lbl_file.exists():
            shutil.copy2(lbl_file, train_lbl_dir / lbl_file.name)
    
    # Copy validation files
    print("   Copying validation set...")
    for img_id in val_images:
        img_info = image_info[img_id]
        img_file = images_path / img_info['file_name']
        lbl_file = labels_path / (Path(img_info['file_name']).stem + '.txt')
        
        if img_file.exists():
            shutil.copy2(img_file, val_img_dir / img_info['file_name'])
        if lbl_file.exists():
            shutil.copy2(lbl_file, val_lbl_dir / lbl_file.name)
    
    # Create split info file
    split_info = {
        'train_images': sorted(list(train_images)),
        'val_images': sorted(list(val_images)),
        'train_size': len(train_images),
        'val_size': len(val_images),
        'train_classes': sorted(list(train_classes)),
        'val_classes': sorted(list(val_classes)),
        'seed': seed,
        'val_ratio': val_ratio
    }
    
    with open(output_path / 'split_info.json', 'w') as f:
        json.dump(split_info, f, indent=2)
    
    print(f"\n✅ Split complete!")
    print(f"   Train: {train_img_dir}")
    print(f"   Val: {val_img_dir}")
    print(f"   Split info: {output_path / 'split_info.json'}")
    
    # Create updated data.yaml
    create_split_yaml(output_path)
    
    return split_info

def create_split_yaml(output_dir):
    """Create data.yaml for the split dataset"""
    
    yaml_content = f"""# Dataset configuration for train/val split
path: {Path(output_dir).absolute()}
train: train
val: val

# Classes (same as original)
nc: 356
names:
"""
    
    # Load original names
    with open('data.yaml') as f:
        import yaml
        original = yaml.safe_load(f)
        for name in original['names']:
            yaml_content += f'- "{name}"\n'
    
    yaml_path = Path(output_dir) / 'data.yaml'
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    
    print(f"   Created: {yaml_path}")

def analyze_class_distribution(annotations_file='data/train/annotations.json'):
    """Analyze and report class distribution"""
    
    print("\n" + "=" * 70)
    print("CLASS DISTRIBUTION ANALYSIS")
    print("=" * 70)
    
    with open(annotations_file) as f:
        coco_data = json.load(f)
    
    # Count annotations per class
    class_counts = Counter(ann['category_id'] for ann in coco_data['annotations'])
    
    # Statistics
    counts = list(class_counts.values())
    print(f"\n📊 Statistics:")
    print(f"   Total classes: {len(class_counts)}")
    print(f"   Total annotations: {sum(counts)}")
    print(f"   Mean per class: {np.mean(counts):.1f}")
    print(f"   Median per class: {np.median(counts):.1f}")
    print(f"   Std dev: {np.std(counts):.1f}")
    print(f"   Min: {min(counts)}")
    print(f"   Max: {max(counts)}")
    
    # Distribution bins
    bins = [0, 5, 10, 20, 50, 100, 500]
    print(f"\n📈 Distribution:")
    for i in range(len(bins)-1):
        count = sum(1 for c in counts if bins[i] < c <= bins[i+1])
        print(f"   {bins[i]+1}-{bins[i+1]} samples: {count} classes")
    count = sum(1 for c in counts if c > bins[-1])
    print(f"   >{bins[-1]} samples: {count} classes")
    
    # Most/least common
    most_common = class_counts.most_common(10)
    least_common = class_counts.most_common()[-10:]
    
    print(f"\n🔝 Top 10 classes:")
    for cls, count in most_common:
        print(f"   Class {cls}: {count} samples")
    
    print(f"\n🔻 Bottom 10 classes:")
    for cls, count in least_common:
        print(f"   Class {cls}: {count} samples")
    
    # Save detailed report
    report = {
        'total_classes': len(class_counts),
        'total_annotations': sum(counts),
        'statistics': {
            'mean': float(np.mean(counts)),
            'median': float(np.median(counts)),
            'std': float(np.std(counts)),
            'min': int(min(counts)),
            'max': int(max(counts))
        },
        'distribution': {
            f'{bins[i]+1}-{bins[i+1]}': sum(1 for c in counts if bins[i] < c <= bins[i+1])
            for i in range(len(bins)-1)
        },
        'class_counts': dict(class_counts)
    }
    
    with open('data/class_distribution.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Detailed report saved to: data/class_distribution.json")
    
    return report

def main():
    """Main execution"""
    
    # Analyze class distribution
    analyze_class_distribution()
    
    # Create train/val split
    split_info = create_train_val_split()
    
    print("\n" + "=" * 70)
    print("✅ DATASET PREPARATION COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Review split_info.json")
    print("2. Use data/train_split/data.yaml for training")
    print("3. Proceed with training pipeline")

if __name__ == '__main__':
    main()

# Made with Bob
