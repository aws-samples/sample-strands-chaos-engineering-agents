#!/usr/bin/env python3
"""
Test script for hypothesis evaluation charts.

This script tests the chart generation functionality by creating a sample chart.
"""
import os
import sys
import logging
from pathlib import Path

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

def test_chart_generation():
    """Test chart generation with sample data."""
    # Create output directory if it doesn't exist
    output_dir = "test_charts"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate a test chart
    logger.info("Generating test chart...")
    result = display_hypothesis_evaluation_chart(
        chart_type="radar",
        output_path=os.path.join(output_dir, "test_radar_chart.png")
    )
    
    # Check result
    if result["success"]:
        logger.info(f"Successfully generated test chart with {result['hypothesis_count']} hypotheses")
        logger.info(f"Chart saved to: {result['chart_data']['file_path']}")
        return True
    else:
        logger.error(f"Failed to generate test chart: {result['message']}")
        return False

def test_statistics_generation():
    """Test statistics generation with sample data."""
    # Create output directory if it doesn't exist
    output_dir = "test_charts"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate statistics
    logger.info("Generating statistics...")
    result = display_evaluation_statistics(
        output_path=os.path.join(output_dir, "test_statistics_chart.png")
    )
    
    # Check result
    if result["success"]:
        logger.info(f"Successfully generated statistics for {result['hypothesis_count']} hypotheses")
        
        # Print some statistics
        stats = result["statistics"]
        logger.info("Mean scores:")
        for criterion, score in stats["average_scores"].items():
            logger.info(f"  {criterion}: {score}")
        
        logger.info("Standard deviations:")
        for criterion, std in stats["standard_deviations"].items():
            logger.info(f"  {criterion}: {std}")
        
        if "chart_data" in result and result["chart_data"]["file_path"]:
            logger.info(f"Statistics chart saved to: {result['chart_data']['file_path']}")
        
        return True
    else:
        logger.error(f"Failed to generate statistics: {result['message']}")
        return False

if __name__ == "__main__":
    # Test chart generation
    chart_success = test_chart_generation()
    
    # Test statistics generation
    stats_success = test_statistics_generation()
    
    # Exit with success if both tests pass
    sys.exit(0 if chart_success and stats_success else 1)
