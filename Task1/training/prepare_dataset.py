#!/usr/bin/env python3
"""
Master Dataset Preparation Script
Runs all preparation steps in sequence
"""

import sys
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent / 'utils'))

from dataset_prep import create_train_val_split, analyze_class_distribution
from organize_products import organize_product_images, create_product_dataset_yaml
from class_weights import compute_class_weights

def main():
    """Run all preparation steps"""
    
    print("\n" + "=" * 70)
    print("COMPREHENSIVE DATASET PREPARATION")
    print("=" * 70)
    print("\nThis will:")
    print("1. Analyze class distribution")
    print("2. Create train/val split (80/20)")
    print("3. Organize product images by category")
    print("4. Compute class weights for imbalance handling")
    print("\n" + "=" * 70)
    
    input("\nPress Enter to continue...")
    
    try:
        # Step 1: Analyze class distribution
        print("\n\n" + "🔍 STEP 1: Analyzing Class Distribution")
        print("=" * 70)
        analyze_class_distribution()
        
        # Step 2: Create train/val split
        print("\n\n" + "📊 STEP 2: Creating Train/Val Split")
        print("=" * 70)
        split_info = create_train_val_split()
        
        # Step 3: Organize product images
        print("\n\n" + "🖼️  STEP 3: Organizing Product Images")
        print("=" * 70)
        mapping = organize_product_images()
        create_product_dataset_yaml()
        
        # Step 4: Compute class weights
        print("\n\n" + "⚖️  STEP 4: Computing Class Weights")
        print("=" * 70)
        weights = compute_class_weights(method='inverse_freq')
        
        # Summary
        print("\n\n" + "=" * 70)
        print("✅ ALL PREPARATION STEPS COMPLETE!")
        print("=" * 70)
        
        print("\n📊 Summary:")
        print(f"   Training images: {split_info['train_size']}")
        print(f"   Validation images: {split_info['val_size']}")
        print(f"   Product images organized: {mapping['total_images']}")
        print(f"   Categories with product images: {mapping['categories_covered']}")
        print(f"   Class weights computed: {len(weights)}")
        
        print("\n📁 Generated Files:")
        print("   - data/train_split/data.yaml (for detection training)")
        print("   - data/train_split/split_info.json")
        print("   - data/product_images_organized/data.yaml (for pre-training)")
        print("   - data/product_images_organized/category_mapping.json")
        print("   - data/class_distribution.json")
        print("   - data/class_weights_inverse_freq.json")
        
        print("\n🚀 Next Steps:")
        print("   1. Review generated files")
        print("   2. Run Stage 1 pre-training:")
        print("      python training/stage1_pretrain.py")
        print("   3. Or run full pipeline:")
        print("      python training/train_full_pipeline.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during preparation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

# Made with Bob
