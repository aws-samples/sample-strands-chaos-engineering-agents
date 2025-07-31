#!/usr/bin/env python3
"""
Command-line interface for running the Chaos Agent workflow.
This script provides a simple CLI for executing the chaos engineering workflow.
"""

import argparse
import logging
import sys
from workflow_orchestrator import run_chaos_workflow
from shared.config import set_region_override, get_aws_region
from shared.resource_tags import parse_tags_string

def main():
    """Parse command line arguments and run the chaos engineering workflow."""
    parser = argparse.ArgumentParser(
        description="Run the Chaos Agent workflow for testing AWS workload resilience."
    )
    
    parser.add_argument(
        "--workload", "-w",
        type=str,
        default="https://github.com/aws-containers/retail-store-sample-app.git",
        help="Repository URL for the workload to analyze (default: AWS Retail Store Sample App)"
    )
    
    parser.add_argument(
        "--region", "-r",
        type=str,
        default="us-east-1",
        help="AWS region where resources are deployed (default: us-east-1)"
    )
    
    parser.add_argument(
        "--experiments", "-e",
        type=int,
        default=3,
        help="Number of top priority experiments to execute (default: 3)"
    )
    
    parser.add_argument(
        "--tags", "-t",
        type=str,
        help="Workload tags for resource filtering (format: 'Environment=prod,Application=web-app')"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set region override if provided via CLI
    if args.region != "us-east-1":  # Only override if not default
        set_region_override(args.region)
    
    # Get the actual region that will be used (may come from stack/env)
    actual_region = get_aws_region()
    
    # Configure basic logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler()]
    )
    
    logger = logging.getLogger("chaos_cli")
    logger.info(f"Starting Chaos Agent workflow for {args.workload}")
    logger.info(f"AWS Region: {actual_region}")
    logger.info(f"Executing top {args.experiments} experiments")
    
    # Validate tags if provided
    if args.tags:
        try:
            # Just validate the format, don't convert to list
            parse_tags_string(args.tags)
            logger.info(f"Using workload tags: {args.tags}")
        except ValueError as e:
            logger.error(f"Invalid tags format: {e}")
            return 1
    else:
        logger.info("No workload tags specified - will consider all resources")
    
    try:
        # Run the workflow with the provided arguments
        result = run_chaos_workflow(
            workload_repo=args.workload,
            region=actual_region,
            tags=args.tags,
            top_experiments=args.experiments,
            verbose=args.verbose
        )
        
        logger.info("Workflow completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Error running workflow: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
