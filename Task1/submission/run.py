#!/usr/bin/env python3
"""
NorgesGruppen Object Detection Competition - Submission Entry Point
This script implements the required interface for the competition submission.

Usage:
    python run.py --input /data/images --output /output/predictions.json
"""

import argparse
import json
from pathlib import Path
from typing import List, Dict

import torch
import numpy as np
from ultralytics import YOLO


class GroceryDetector:
    """
    Grocery product detector using YOLOv8.
    Handles detection and classification of 357 product categories (0-356).
    """
    
    def __init__(self, model_path: str = "best.pt", conf_threshold: float = 0.25):
        """
        Initialize the detector.
        
        Args:
            model_path: Path to YOLOv8 model weights
            conf_threshold: Confidence threshold for detections
        """
        self.conf_threshold = conf_threshold
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Load model
        model_file = Path(__file__).parent / model_path
        if not model_file.exists():
            print(f"Warning: Model file {model_file} not found. Using baseline YOLOv8n.")
            self.model = YOLO('yolov8n.pt')
        else:
            self.model = YOLO(str(model_file))
        
        self.model.to(self.device)
        print(f"Model loaded on {self.device}")
    
    def predict_image(self, image_path: str) -> List[Dict]:
        """
        Perform object detection on a single shelf image.
        
        Args:
            image_path: Path to input shelf image
        
        Returns:
            List of detection dictionaries in COCO format:
            [
                {
                    'image_id': int,
                    'category_id': int,
                    'bbox': [x, y, width, height],
                    'score': float
                }
            ]
        """
        # Extract image_id from filename (img_00042.jpg -> 42)
        filename = Path(image_path).stem
        image_id = int(filename.split('_')[-1])
        
        # Run inference
        results = self.model.predict(
            source=image_path,
            conf=self.conf_threshold,
            device=self.device,
            verbose=False
        )
        
        detections = []
        
        # Process results
        for result in results:
            boxes = result.boxes
            
            if boxes is None or len(boxes) == 0:
                continue
            
            # Extract predictions
            for i in range(len(boxes)):
                # Get box coordinates in xyxy format
                xyxy = boxes.xyxy[i].cpu().numpy()
                
                # Convert to COCO format [x, y, width, height]
                x1, y1, x2, y2 = xyxy
                x, y = float(x1), float(y1)
                width = float(x2 - x1)
                height = float(y2 - y1)
                
                # Get class and confidence
                cls = int(boxes.cls[i].cpu().numpy())
                conf = float(boxes.conf[i].cpu().numpy())
                
                detection = {
                    'image_id': image_id,
                    'category_id': cls,
                    'bbox': [x, y, width, height],
                    'score': conf
                }
                
                detections.append(detection)
        
        return detections
    
    def predict_directory(self, input_dir: str, output_path: str):
        """
        Process all images in a directory and save predictions.
        
        Args:
            input_dir: Directory containing input images
            output_path: Path to save predictions JSON
        """
        input_path = Path(input_dir)
        
        # Find all JPEG images
        image_files = sorted(list(input_path.glob('*.jpg')) + list(input_path.glob('*.jpeg')))
        
        if not image_files:
            print(f"Warning: No images found in {input_dir}")
            # Create empty predictions file
            with open(output_path, 'w') as f:
                json.dump([], f)
            return
        
        print(f"Processing {len(image_files)} images...")
        
        all_predictions = []
        
        for i, image_file in enumerate(image_files, 1):
            if i % 10 == 0:
                print(f"Processed {i}/{len(image_files)} images")
            
            predictions = self.predict_image(str(image_file))
            all_predictions.extend(predictions)
        
        # Save predictions
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(all_predictions, f, indent=2)
        
        print(f"Saved {len(all_predictions)} predictions to {output_path}")


def main():
    """Main entry point for the competition submission."""
    parser = argparse.ArgumentParser(
        description='NorgesGruppen Object Detection - Inference Script'
    )
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Input directory containing shelf images'
    )
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output path for predictions JSON file'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='best.pt',
        help='Path to model weights (default: best.pt)'
    )
    parser.add_argument(
        '--conf',
        type=float,
        default=0.25,
        help='Confidence threshold (default: 0.25)'
    )
    
    args = parser.parse_args()
    
    # Validate input directory
    input_path = Path(args.input)
    if not input_path.is_dir():
        print(f"Warning: Input directory '{args.input}' does not exist")
        # Create empty predictions file
        output_dir = Path(args.output).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w') as f:
            json.dump([], f)
        print("Created empty predictions file")
        return
    
    # Initialize detector
    try:
        detector = GroceryDetector(
            model_path=args.model,
            conf_threshold=args.conf
        )
    except Exception as e:
        print(f"Error initializing detector: {e}")
        # Create empty predictions file
        output_dir = Path(args.output).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w') as f:
            json.dump([], f)
        return
    
    # Run inference
    try:
        detector.predict_directory(args.input, args.output)
        print("Inference complete!")
    except Exception as e:
        print(f"Error during inference: {e}")
        # Ensure output file exists even if inference fails
        if not Path(args.output).exists():
            output_dir = Path(args.output).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            with open(args.output, 'w') as f:
                json.dump([], f)


if __name__ == '__main__':
    main()

# Made with Bob
