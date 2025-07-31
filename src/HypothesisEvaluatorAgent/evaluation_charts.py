"""
Hypothesis Evaluation Charts

Tools for retrieving hypothesis evaluation results and displaying them in charts.
"""
from strands import tool
import logging
from typing import Dict, Any, List, Optional
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from pathlib import Path
from matplotlib.figure import Figure

# Import evaluation database tools
from shared.hypothesis_evaluations import get_hypothesis_evaluations
import numpy as np

# Set up logging
logger = logging.getLogger(__name__)

@tool
def display_hypothesis_evaluation_chart(
    hypothesis_ids: Optional[List[int]] = None,
    chart_type: str = "radar",
    output_path: Optional[str] = None,
    min_overall_score: Optional[float] = None,
    max_overall_score: Optional[float] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Retrieve hypothesis evaluation results and display them in a chart.
    
    Args:
        hypothesis_ids: Optional list of specific hypothesis IDs to include
        chart_type: Type of chart to generate ('radar', 'bar', 'heatmap', 'comparison')
        output_path: Optional path to save the chart image
        min_overall_score: Optional minimum overall score filter
        max_overall_score: Optional maximum overall score filter
        limit: Maximum number of evaluations to include
        
    Returns:
        Dict containing chart metadata, base64 encoded image, and success status
    """
    logger.info(f"Generating {chart_type} chart for hypothesis evaluations")
    
    try:
        # 1. Retrieve evaluation data
        evaluation_results = get_hypothesis_evaluations(
            hypothesis_ids=hypothesis_ids,
            min_overall_score=min_overall_score,
            max_overall_score=max_overall_score,
            limit=limit
        )
        
        if not evaluation_results["success"]:
            logger.error(f"Failed to retrieve evaluation data: {evaluation_results.get('error', 'Unknown error')}")
            return {
                "success": False,
                "error": evaluation_results.get("error", "Unknown error"),
                "message": "Failed to retrieve evaluation data"
            }
        
        evaluations = evaluation_results["evaluations"]
        
        if not evaluations:
            logger.warning("No evaluation data found")
            return {
                "success": False,
                "error": "No evaluation data found",
                "message": "No hypothesis evaluations available to chart"
            }
        
        # 2. Generate appropriate chart based on chart_type
        if chart_type.lower() == "radar":
            chart_data = generate_radar_chart(evaluations, output_path)
        elif chart_type.lower() == "bar":
            chart_data = generate_bar_chart(evaluations, output_path)
        elif chart_type.lower() == "heatmap":
            chart_data = generate_heatmap(evaluations, output_path)
        elif chart_type.lower() == "comparison":
            chart_data = generate_comparison_chart(evaluations, output_path)
        else:
            logger.error(f"Unsupported chart type: {chart_type}")
            return {
                "success": False,
                "error": f"Unsupported chart type: {chart_type}",
                "message": "Supported types: radar, bar, heatmap, comparison"
            }
        
        # 3. Return result with chart metadata
        logger.info(f"Successfully generated {chart_type} chart for {len(evaluations)} hypotheses")
        return {
            "success": True,
            "chart_type": chart_type,
            "hypothesis_count": len(evaluations),
            "chart_data": chart_data,
            "message": f"Successfully generated {chart_type} chart for {len(evaluations)} hypotheses"
        }
        
    except ImportError as e:
        logger.error(f"Missing required library: {str(e)}")
        return {
            "success": False,
            "error": f"Missing required library: {str(e)}",
            "message": "Please install matplotlib and numpy: pip install matplotlib numpy"
        }
    except Exception as e:
        logger.error(f"Error generating chart: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to generate {chart_type} chart"
        }

def generate_radar_chart(evaluations: List[Dict[str, Any]], output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate radar charts for hypothesis evaluations.
    
    Args:
        evaluations: List of evaluation dictionaries
        output_path: Optional path to save the chart image
        
    Returns:
        Dict containing chart metadata and base64 encoded image
    """
    # Limit to a reasonable number of hypotheses for radar charts
    max_radar_charts = 6
    if len(evaluations) > max_radar_charts:
        logger.warning(f"Too many hypotheses for radar chart. Limiting to {max_radar_charts}.")
        evaluations = evaluations[:max_radar_charts]
    
    # Set up the figure
    n_hypotheses = len(evaluations)
    n_cols = min(3, n_hypotheses)
    n_rows = (n_hypotheses + n_cols - 1) // n_cols
    
    fig = plt.figure(figsize=(5*n_cols, 4*n_rows))
    plt.subplots_adjust(hspace=0.4, wspace=0.4)
    
    # Categories for the radar chart
    categories = ['Testability', 'Specificity', 'Realism', 'Safety', 'Learning Value']
    N = len(categories)
    
    # Create angle for each category
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Close the loop
    
    for i, evaluation in enumerate(evaluations):
        # Create subplot
        ax = plt.subplot(n_rows, n_cols, i+1, polar=True)
        
        # Get scores
        scores = [
            evaluation['testability_score'],
            evaluation['specificity_score'],
            evaluation['realism_score'],
            evaluation['safety_score'],
            evaluation['learning_value_score']
        ]
        scores += scores[:1]  # Close the loop
        
        # Plot scores
        ax.plot(angles, scores, linewidth=2, linestyle='solid', label=f"Hypothesis {evaluation['hypothesis_id']}")
        ax.fill(angles, scores, alpha=0.25)
        
        # Set category labels
        plt.xticks(angles[:-1], categories, size=10)
        
        # Set y-axis limits
        ax.set_ylim(0, 5)
        
        # Add title
        title = f"Hypothesis {evaluation['hypothesis_id']}"
        if len(evaluation['hypothesis_title']) > 30:
            title += f"\n{evaluation['hypothesis_title'][:30]}..."
        else:
            title += f"\n{evaluation['hypothesis_title']}"
        title += f"\nOverall: {evaluation['overall_score']:.2f}"
        plt.title(title, size=11, y=1.1)
    
    plt.tight_layout()
    
    # Save or return the chart
    return save_or_return_chart(fig, output_path, "radar")

def generate_bar_chart(evaluations: List[Dict[str, Any]], output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate bar chart comparing scores across hypotheses.
    
    Args:
        evaluations: List of evaluation dictionaries
        output_path: Optional path to save the chart image
        
    Returns:
        Dict containing chart metadata and base64 encoded image
    """
    # Limit to a reasonable number of hypotheses for bar charts
    max_bar_hypotheses = 10
    if len(evaluations) > max_bar_hypotheses:
        logger.warning(f"Too many hypotheses for bar chart. Limiting to {max_bar_hypotheses}.")
        evaluations = evaluations[:max_bar_hypotheses]
    
    # Set up the figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Categories and positions
    categories = ['Testability', 'Specificity', 'Realism', 'Safety', 'Learning Value', 'Overall']
    n_categories = len(categories)
    n_hypotheses = len(evaluations)
    
    # Width of each bar group
    group_width = 0.8
    bar_width = group_width / n_hypotheses
    
    # X positions for each category
    x = np.arange(n_categories)
    
    # Plot bars for each hypothesis
    for i, evaluation in enumerate(evaluations):
        # Get scores
        scores = [
            evaluation['testability_score'],
            evaluation['specificity_score'],
            evaluation['realism_score'],
            evaluation['safety_score'],
            evaluation['learning_value_score'],
            evaluation['overall_score']
        ]
        
        # Calculate position
        pos = x - group_width/2 + (i + 0.5) * bar_width
        
        # Plot bars
        bars = ax.bar(pos, scores, bar_width, label=f"H{evaluation['hypothesis_id']}")
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f"{height:.1f}", ha='center', va='bottom', fontsize=8)
    
    # Set labels and title
    ax.set_ylabel('Score (1-5)')
    ax.set_title('Hypothesis Evaluation Scores by Category')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 5.5)  # Set y-axis limit with space for labels
    ax.legend(title="Hypothesis ID", bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    
    # Save or return the chart
    return save_or_return_chart(fig, output_path, "bar")

def generate_heatmap(evaluations: List[Dict[str, Any]], output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate heatmap showing scores for all hypotheses.
    
    Args:
        evaluations: List of evaluation dictionaries
        output_path: Optional path to save the chart image
        
    Returns:
        Dict containing chart metadata and base64 encoded image
    """
    # Limit to a reasonable number of hypotheses for heatmaps
    max_heatmap_hypotheses = 20
    if len(evaluations) > max_heatmap_hypotheses:
        logger.warning(f"Too many hypotheses for heatmap. Limiting to {max_heatmap_hypotheses}.")
        evaluations = evaluations[:max_heatmap_hypotheses]
    
    # Set up the figure
    fig, ax = plt.subplots(figsize=(10, max(6, len(evaluations) * 0.4)))
    
    # Categories
    categories = ['Testability', 'Specificity', 'Realism', 'Safety', 'Learning Value', 'Overall']
    
    # Prepare data for heatmap
    data = []
    y_labels = []
    
    # Sort evaluations by overall score (descending)
    evaluations = sorted(evaluations, key=lambda x: x['overall_score'], reverse=True)
    
    for evaluation in evaluations:
        # Get scores
        scores = [
            evaluation['testability_score'],
            evaluation['specificity_score'],
            evaluation['realism_score'],
            evaluation['safety_score'],
            evaluation['learning_value_score'],
            evaluation['overall_score']
        ]
        data.append(scores)
        
        # Create label with ID and truncated title
        title = evaluation['hypothesis_title']
        if len(title) > 30:
            title = title[:27] + "..."
        y_labels.append(f"H{evaluation['hypothesis_id']}: {title}")
    
    # Create heatmap
    im = ax.imshow(data, cmap='RdYlGn', vmin=1, vmax=5)
    
    # Add colorbar
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("Score", rotation=-90, va="bottom")
    
    # Set labels and title
    ax.set_xticks(np.arange(len(categories)))
    ax.set_yticks(np.arange(len(y_labels)))
    ax.set_xticklabels(categories)
    ax.set_yticklabels(y_labels)
    
    # Rotate x labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Add text annotations with scores
    for i in range(len(y_labels)):
        for j in range(len(categories)):
            text = ax.text(j, i, f"{data[i][j]:.1f}",
                          ha="center", va="center", color="black")
    
    ax.set_title("Hypothesis Evaluation Scores Heatmap")
    fig.tight_layout()
    
    # Save or return the chart
    return save_or_return_chart(fig, output_path, "heatmap")

def generate_comparison_chart(evaluations: List[Dict[str, Any]], output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate comparison chart of overall scores.
    
    Args:
        evaluations: List of evaluation dictionaries
        output_path: Optional path to save the chart image
        
    Returns:
        Dict containing chart metadata and base64 encoded image
    """
    # Limit to a reasonable number of hypotheses for comparison charts
    max_comparison_hypotheses = 20
    if len(evaluations) > max_comparison_hypotheses:
        logger.warning(f"Too many hypotheses for comparison chart. Limiting to {max_comparison_hypotheses}.")
        evaluations = evaluations[:max_comparison_hypotheses]
    
    # Sort evaluations by overall score (descending)
    evaluations = sorted(evaluations, key=lambda x: x['overall_score'], reverse=True)
    
    # Set up the figure
    fig, ax = plt.subplots(figsize=(12, max(6, len(evaluations) * 0.4)))
    
    # Prepare data
    hypothesis_ids = [f"H{e['hypothesis_id']}" for e in evaluations]
    overall_scores = [e['overall_score'] for e in evaluations]
    
    # Create horizontal bar chart
    bars = ax.barh(hypothesis_ids, overall_scores, color='skyblue')
    
    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                f"{width:.2f}", ha='left', va='center')
    
    # Add hypothesis titles as annotations
    for i, evaluation in enumerate(evaluations):
        title = evaluation['hypothesis_title']
        if len(title) > 40:
            title = title[:37] + "..."
        ax.text(0.1, i, title, ha='left', va='center', color='black', fontsize=8)
    
    # Set labels and title
    ax.set_xlabel('Overall Score (1-5)')
    ax.set_title('Hypothesis Comparison by Overall Score')
    ax.set_xlim(0, 5.5)  # Set x-axis limit with space for labels
    
    # Add color bands for score ranges
    ax.axvspan(1, 2, alpha=0.1, color='red')
    ax.axvspan(2, 3, alpha=0.1, color='orange')
    ax.axvspan(3, 4, alpha=0.1, color='yellow')
    ax.axvspan(4, 5, alpha=0.1, color='green')
    
    # Add score range labels
    ax.text(1.5, -0.8, "Poor (1-2)", ha='center', va='center', fontsize=8)
    ax.text(2.5, -0.8, "Fair (2-3)", ha='center', va='center', fontsize=8)
    ax.text(3.5, -0.8, "Good (3-4)", ha='center', va='center', fontsize=8)
    ax.text(4.5, -0.8, "Excellent (4-5)", ha='center', va='center', fontsize=8)
    
    plt.tight_layout()
    
    # Save or return the chart
    return save_or_return_chart(fig, output_path, "comparison")

def generate_statistics_chart(stats: Dict[str, Any], output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a chart showing mean and standard deviation for each quality score.
    
    Args:
        stats: Statistics dictionary from get_evaluation_statistics
        output_path: Optional path to save the chart image
        
    Returns:
        Dict containing chart metadata and base64 encoded image
    """
    # Set up the figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Categories
    categories = ['Testability', 'Specificity', 'Realism', 'Safety', 'Learning Value', 'Overall']
    
    # Get means and standard deviations
    means = [
        stats['average_scores']['testability'],
        stats['average_scores']['specificity'],
        stats['average_scores']['realism'],
        stats['average_scores']['safety'],
        stats['average_scores']['learning_value'],
        stats['average_scores']['overall']
    ]
    
    stds = [
        stats['standard_deviations']['testability'],
        stats['standard_deviations']['specificity'],
        stats['standard_deviations']['realism'],
        stats['standard_deviations']['safety'],
        stats['standard_deviations']['learning_value'],
        stats['standard_deviations']['overall']
    ]
    
    # X positions
    x = np.arange(len(categories))
    
    # Plot bars with error bars
    bars = ax.bar(x, means, yerr=stds, align='center', alpha=0.7, ecolor='black', capsize=10)
    
    # Add value labels on top of bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f"{means[i]:.2f} ± {stds[i]:.2f}", ha='center', va='bottom', fontsize=9)
    
    # Set labels and title
    ax.set_ylabel('Score (1-5)')
    ax.set_title('Hypothesis Evaluation Scores: Mean and Standard Deviation')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 5.5)  # Set y-axis limit with space for labels
    
    # Add count information
    ax.text(0.02, 0.02, f"Based on {stats['count']} hypotheses", 
            transform=ax.transAxes, fontsize=9, va='bottom')
    
    # Add grid lines for better readability
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    
    # Save or return the chart
    return save_or_return_chart(fig, output_path, "statistics")

@tool
def display_evaluation_statistics(
    hypothesis_ids: Optional[List[int]] = None,
    min_overall_score: Optional[float] = None,
    max_overall_score: Optional[float] = None,
    limit: int = 50,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve hypothesis evaluation results and display mean and standard deviation statistics.
    
    Args:
        hypothesis_ids: Optional list of specific hypothesis IDs to include
        min_overall_score: Optional minimum overall score filter
        max_overall_score: Optional maximum overall score filter
        limit: Maximum number of evaluations to include
        output_path: Optional path to save the statistics chart image
        
    Returns:
        Dict containing statistics and optionally a base64 encoded chart image
    """
    logger.info("Generating evaluation statistics")
    
    try:
        # 1. Retrieve evaluation data
        evaluation_results = get_hypothesis_evaluations(
            hypothesis_ids=hypothesis_ids,
            min_overall_score=min_overall_score,
            max_overall_score=max_overall_score,
            limit=limit
        )
        
        if not evaluation_results["success"]:
            logger.error(f"Failed to retrieve evaluation data: {evaluation_results.get('error', 'Unknown error')}")
            return {
                "success": False,
                "error": evaluation_results.get("error", "Unknown error"),
                "message": "Failed to retrieve evaluation data"
            }
        
        evaluations = evaluation_results["evaluations"]
        
        if not evaluations:
            logger.warning("No evaluation data found")
            return {
                "success": False,
                "error": "No evaluation data found",
                "message": "No hypothesis evaluations available for statistics"
            }
        
        # 2. Calculate statistics
        stats = get_evaluation_statistics(evaluations)
        
        # 3. Generate statistics chart if output_path is provided
        chart_data = None
        if output_path:
            chart_data = generate_statistics_chart(stats, output_path)
        
        # 4. Return result with statistics
        logger.info(f"Successfully generated statistics for {len(evaluations)} hypotheses")
        result = {
            "success": True,
            "hypothesis_count": len(evaluations),
            "statistics": stats,
            "message": f"Successfully generated statistics for {len(evaluations)} hypotheses"
        }
        
        if chart_data:
            result["chart_data"] = chart_data
            
        return result
        
    except ImportError as e:
        logger.error(f"Missing required library: {str(e)}")
        return {
            "success": False,
            "error": f"Missing required library: {str(e)}",
            "message": "Please install matplotlib and numpy: pip install matplotlib numpy"
        }
    except Exception as e:
        logger.error(f"Error generating statistics: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate statistics"
        }


def save_or_return_chart(fig: Figure, output_path: Optional[str], chart_type: str) -> Dict[str, Any]:
    """
    Save chart to file if output_path is provided, and return base64 encoded image.
    
    Args:
        fig: Matplotlib figure
        output_path: Optional path to save the chart image
        chart_type: Type of chart
        
    Returns:
        Dict containing chart metadata and base64 encoded image
    """
    # Save to file if output_path is provided
    if output_path:
        try:
            # Create directory if it doesn't exist
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save figure
            fig.savefig(output_path, bbox_inches='tight', dpi=300)
            logger.info(f"Saved {chart_type} chart to {output_path}")
            
            file_path = output_path
        except Exception as e:
            logger.error(f"Error saving chart to {output_path}: {str(e)}")
            file_path = None
    else:
        file_path = None
    
    # Convert figure to base64 encoded image
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    
    # Close the figure to free memory
    plt.close(fig)
    
    return {
        "image_base64": img_str,
        "file_path": file_path,
        "chart_type": chart_type
    }

def get_evaluation_statistics(evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate statistics for hypothesis evaluations.
    
    Args:
        evaluations: List of evaluation dictionaries
        
    Returns:
        Dict containing statistics about the evaluations
    """
    if not evaluations:
        return {
            "count": 0,
            "message": "No evaluations available"
        }
    
    # Calculate average scores
    avg_testability = sum(e['testability_score'] for e in evaluations) / len(evaluations)
    avg_specificity = sum(e['specificity_score'] for e in evaluations) / len(evaluations)
    avg_realism = sum(e['realism_score'] for e in evaluations) / len(evaluations)
    avg_safety = sum(e['safety_score'] for e in evaluations) / len(evaluations)
    avg_learning = sum(e['learning_value_score'] for e in evaluations) / len(evaluations)
    avg_overall = sum(e['overall_score'] for e in evaluations) / len(evaluations)
    
    # Calculate standard deviations
    import numpy as np
    std_testability = np.std([e['testability_score'] for e in evaluations])
    std_specificity = np.std([e['specificity_score'] for e in evaluations])
    std_realism = np.std([e['realism_score'] for e in evaluations])
    std_safety = np.std([e['safety_score'] for e in evaluations])
    std_learning = np.std([e['learning_value_score'] for e in evaluations])
    std_overall = np.std([e['overall_score'] for e in evaluations])
    
    # Calculate score distribution
    score_ranges = {
        "1-2": 0,
        "2-3": 0,
        "3-4": 0,
        "4-5": 0
    }
    
    for e in evaluations:
        score = e['overall_score']
        if score < 2:
            score_ranges["1-2"] += 1
        elif score < 3:
            score_ranges["2-3"] += 1
        elif score < 4:
            score_ranges["3-4"] += 1
        else:
            score_ranges["4-5"] += 1
    
    return {
        "count": len(evaluations),
        "average_scores": {
            "testability": round(avg_testability, 2),
            "specificity": round(avg_specificity, 2),
            "realism": round(avg_realism, 2),
            "safety": round(avg_safety, 2),
            "learning_value": round(avg_learning, 2),
            "overall": round(avg_overall, 2)
        },
        "standard_deviations": {
            "testability": round(std_testability, 2),
            "specificity": round(std_specificity, 2),
            "realism": round(std_realism, 2),
            "safety": round(std_safety, 2),
            "learning_value": round(std_learning, 2),
            "overall": round(std_overall, 2)
        },
        "score_distribution": score_ranges,
        "highest_score": max(e['overall_score'] for e in evaluations),
        "lowest_score": min(e['overall_score'] for e in evaluations)
    }
