#!/usr/bin/env python3
"""
Hypothesis Evaluation Chart Generator

This script generates charts for hypothesis evaluations from the command line.
"""
import argparse
import os
import sys
import logging
from pathlib import Path
from typing import List, Optional

# Add the parent directory to the path to allow importing from sibling packages
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import the chart generation functionality
from HypothesisEvaluatorAgent.evaluation_charts import display_hypothesis_evaluation_chart, display_evaluation_statistics

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate charts for hypothesis evaluations'
    )
    
    parser.add_argument(
        '--chart-type',
        type=str,
        choices=['radar', 'bar', 'heatmap', 'comparison'],
        default='radar',
        help='Type of chart to generate'
    )
    
    parser.add_argument(
        '--hypothesis-ids',
        type=int,
        nargs='+',
        help='Specific hypothesis IDs to include'
    )
    
    parser.add_argument(
        '--min-score',
        type=float,
        help='Minimum overall score filter'
    )
    
    parser.add_argument(
        '--max-score',
        type=float,
        help='Maximum overall score filter'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=20,
        help='Maximum number of hypotheses to include'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='charts',
        help='Directory to save chart images'
    )
    
    parser.add_argument(
        '--all-types',
        action='store_true',
        help='Generate all chart types'
    )
    
    parser.add_argument(
        '--statistics',
        action='store_true',
        help='Generate statistics chart with mean and standard deviation'
    )
    
    return parser.parse_args()

def generate_chart(
    chart_type: str,
    hypothesis_ids: Optional[List[int]] = None,
    min_overall_score: Optional[float] = None,
    max_overall_score: Optional[float] = None,
    limit: int = 20,
    output_dir: str = 'charts'
) -> bool:
    """
    Generate a chart for hypothesis evaluations.
    
    Args:
        chart_type: Type of chart to generate
        hypothesis_ids: Optional list of specific hypothesis IDs to include
        min_overall_score: Optional minimum overall score filter
        max_overall_score: Optional maximum overall score filter
        limit: Maximum number of hypotheses to include
        output_dir: Directory to save chart images
        
    Returns:
        True if chart generation was successful, False otherwise
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output path
    output_path = os.path.join(output_dir, f"hypothesis_{chart_type}_chart.png")
    
    # Generate chart
    logger.info(f"Generating {chart_type} chart...")
    result = display_hypothesis_evaluation_chart(
        chart_type=chart_type,
        hypothesis_ids=hypothesis_ids,
        min_overall_score=min_overall_score,
        max_overall_score=max_overall_score,
        limit=limit,
        output_path=output_path
    )
    
    # Check result
    if result["success"]:
        logger.info(f"Successfully generated {chart_type} chart with {result['hypothesis_count']} hypotheses")
        logger.info(f"Chart saved to: {output_path}")
        return True
    else:
        logger.error(f"Failed to generate {chart_type} chart: {result['message']}")
        return False

def generate_statistics(
    hypothesis_ids: Optional[List[int]] = None,
    min_overall_score: Optional[float] = None,
    max_overall_score: Optional[float] = None,
    limit: int = 50,
    output_dir: str = 'charts'
) -> bool:
    """
    Generate statistics for hypothesis evaluations.
    
    Args:
        hypothesis_ids: Optional list of specific hypothesis IDs to include
        min_overall_score: Optional minimum overall score filter
        max_overall_score: Optional maximum overall score filter
        limit: Maximum number of hypotheses to include
        output_dir: Directory to save chart images
        
    Returns:
        True if statistics generation was successful, False otherwise
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output path
    output_path = os.path.join(output_dir, "hypothesis_statistics.png")
    
    # Generate statistics
    logger.info("Generating statistics chart...")
    result = display_evaluation_statistics(
        hypothesis_ids=hypothesis_ids,
        min_overall_score=min_overall_score,
        max_overall_score=max_overall_score,
        limit=limit,
        output_path=output_path
    )
    
    # Check result
    if result["success"]:
        logger.info(f"Successfully generated statistics for {result['hypothesis_count']} hypotheses")
        
        # Print statistics
        stats = result["statistics"]
        logger.info(f"Mean scores:")
        for criterion, score in stats["average_scores"].items():
            logger.info(f"  {criterion}: {score}")
        
        logger.info(f"Standard deviations:")
        for criterion, std in stats["standard_deviations"].items():
            logger.info(f"  {criterion}: {std}")
        
        if "chart_data" in result and result["chart_data"]["file_path"]:
            logger.info(f"Statistics chart saved to: {result['chart_data']['file_path']}")
        
        return True
    else:
        logger.error(f"Failed to generate statistics: {result['message']}")
        return False

def main():
    """Main function."""
    args = parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    if args.statistics:
        # Generate statistics
        success = generate_statistics(
            hypothesis_ids=args.hypothesis_ids,
            min_overall_score=args.min_score,
            max_overall_score=args.max_score,
            limit=args.limit,
            output_dir=args.output_dir
        )
        
        if args.all_types:
            # Also generate all chart types
            chart_types = ['radar', 'bar', 'heatmap', 'comparison']
            success_count = 0
            
            for chart_type in chart_types:
                chart_success = generate_chart(
                    chart_type=chart_type,
                    hypothesis_ids=args.hypothesis_ids,
                    min_overall_score=args.min_score,
                    max_overall_score=args.max_score,
                    limit=args.limit,
                    output_dir=args.output_dir
                )
                
                if chart_success:
                    success_count += 1
            
            logger.info(f"Generated {success_count} out of {len(chart_types)} chart types")
            return 0 if success and success_count == len(chart_types) else 1
        
        return 0 if success else 1
    
    elif args.all_types:
        # Generate all chart types
        chart_types = ['radar', 'bar', 'heatmap', 'comparison']
        success_count = 0
        
        for chart_type in chart_types:
            success = generate_chart(
                chart_type=chart_type,
                hypothesis_ids=args.hypothesis_ids,
                min_overall_score=args.min_score,
                max_overall_score=args.max_score,
                limit=args.limit,
                output_dir=args.output_dir
            )
            
            if success:
                success_count += 1
        
        logger.info(f"Generated {success_count} out of {len(chart_types)} chart types")
        return 0 if success_count == len(chart_types) else 1
    else:
        # Generate single chart type
        success = generate_chart(
            chart_type=args.chart_type,
            hypothesis_ids=args.hypothesis_ids,
            min_overall_score=args.min_score,
            max_overall_score=args.max_score,
            limit=args.limit,
            output_dir=args.output_dir
        )
        
        return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
