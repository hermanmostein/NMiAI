#!/usr/bin/env python3
"""
Product Image Organization Script
Organizes product reference images by category for easy access during training
"""

import json
import shutil
from pathlib import Path
from collections import defaultdict

def organize_product_images(
    product_dir='data/NM_NGD_product_images',
    output_dir='data/product_images_organized',
    annotations_file='data/train/annotations.json'
):
    """
    Organize product images by category_id
    
    Args:
        product_dir: Directory containing product images
        output_dir: Output directory for organized images
        annotations_file: COCO annotations to map products to categories
    """
    
    print("=" * 70)
    print("PRODUCT IMAGE ORGANIZATION")
    print("=" * 70)
    
    product_path = Path(product_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load annotations to get category mapping
    print(f"\n📂 Loading annotations from {annotations_file}")
    with open(annotations_file) as f:
        coco_data = json.load(f)
    
    # Build category name to ID mapping
    category_map = {cat['name']: cat['id'] for cat in coco_data['categories']}
    print(f"   Categories: {len(category_map)}")
    
    # Load product metadata if available
    metadata_file = product_path / 'metadata.json'
    product_metadata = {}
    if metadata_file.exists():
        with open(metadata_file) as f:
            product_metadata = json.load(f)
        print(f"   Product metadata: {len(product_metadata)} products")
    
    # Scan product directories
    print(f"\n🔍 Scanning product directories...")
    product_folders = [d for d in product_path.iterdir() if d.is_dir()]
    print(f"   Found {len(product_folders)} product folders")
    
    # Organize by category
    organized_count = 0
    unmatched_count = 0
    category_images = defaultdict(list)
    
    for product_folder in product_folders:
        product_code = product_folder.name
        
        # Find matching category
        category_id = None
        
        # Try to match from metadata
        if product_code in product_metadata:
            product_name = product_metadata[product_code].get('name', '')
            if product_name in category_map:
                category_id = category_map[product_name]
        
        # Try to match by product code in category names
        if category_id is None:
            for cat_name, cat_id in category_map.items():
                if product_code in cat_name or cat_name in product_code:
                    category_id = cat_id
                    break
        
        if category_id is not None:
            # Copy images to category folder
            category_folder = output_path / f'category_{category_id}'
            category_folder.mkdir(exist_ok=True)
            
            # Copy all views
            for img_file in product_folder.glob('*.jpg'):
                dest_file = category_folder / f'{product_code}_{img_file.name}'
                shutil.copy2(img_file, dest_file)
                category_images[category_id].append(str(dest_file))
                organized_count += 1
        else:
            unmatched_count += 1
    
    print(f"\n✅ Organization complete:")
    print(f"   Organized images: {organized_count}")
    print(f"   Unmatched products: {unmatched_count}")
    print(f"   Categories with images: {len(category_images)}")
    
    # Save mapping
    mapping = {
        'category_images': {k: v for k, v in category_images.items()},
        'total_images': organized_count,
        'categories_covered': len(category_images),
        'total_categories': len(category_map)
    }
    
    mapping_file = output_path / 'category_mapping.json'
    with open(mapping_file, 'w') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"   Mapping saved to: {mapping_file}")
    
    # Statistics
    images_per_category = [len(imgs) for imgs in category_images.values()]
    if images_per_category:
        print(f"\n📊 Statistics:")
        print(f"   Avg images per category: {sum(images_per_category)/len(images_per_category):.1f}")
        print(f"   Min images: {min(images_per_category)}")
        print(f"   Max images: {max(images_per_category)}")
    
    return mapping

def create_product_dataset_yaml(output_dir='data/product_images_organized'):
    """Create data.yaml for product image classification"""
    
    output_path = Path(output_dir)
    mapping_file = output_path / 'category_mapping.json'
    
    if not mapping_file.exists():
        print("❌ Category mapping not found. Run organize_product_images first.")
        return
    
    with open(mapping_file) as f:
        mapping = json.load(f)
    
    # Load original names
    with open('data.yaml') as f:
        import yaml
        original = yaml.safe_load(f)
    
    # Create classification dataset structure
    yaml_content = f"""# Product Image Classification Dataset
path: {output_path.absolute()}
train: .
val: .  # Will use same for validation (small dataset)

# Number of classes
nc: {mapping['categories_covered']}

# Class names (only categories with product images)
names:
"""
    
    # Add only categories that have product images
    category_images = mapping['category_images']
    for cat_id in sorted(map(int, category_images.keys())):
        if cat_id < len(original['names']):
            yaml_content += f'- "{original["names"][cat_id]}"\n'
    
    yaml_path = output_path / 'data.yaml'
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    
    print(f"\n✅ Created classification dataset config: {yaml_path}")

def main():
    """Main execution"""
    
    # Organize product images
    mapping = organize_product_images()
    
    # Create dataset config
    create_product_dataset_yaml()
    
    print("\n" + "=" * 70)
    print("✅ PRODUCT IMAGE ORGANIZATION COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Review organized images in data/product_images_organized/")
    print("2. Use for Stage 1 pre-training")
    print("3. Use for copy-paste augmentation in Stage 3")

if __name__ == '__main__':
    main()

# Made with Bob
