# Chaos Agent Infrastructure

This CDK project deploys the infrastructure for the Chaos Agent system, including Aurora PostgreSQL database, Bedrock Knowledge Base, and supporting AWS services.

## Architecture

The infrastructure includes:
- **Aurora PostgreSQL Serverless v2** - Database for storing chaos engineering data
- **Bedrock Knowledge Base** - Vector database for FIS documentation and best practices
- **S3 Bucket** - Document storage for additional chaos engineering resources
- **Lambda Functions** - Custom resources for schema initialization and knowledge base sync
- **IAM Roles** - Pre-configured roles for FIS experiments and knowledge base queries
- **VPC** - Isolated network environment with public/private subnets

## Database Schema

The database is automatically initialized with the following tables:
- `system_component` - System components and their configurations
- `hypothesis` - Chaos engineering hypotheses and predictions
- `experiment` - Experiment definitions and parameters
- `learning_insights` - Results and learnings from experiments
- `source_code_analysis` - Code analysis results
- `aws_resource_analysis` - AWS resource dependency analysis

## Prerequisites

- AWS CLI configured with appropriate credentials
- Node.js 18+ and npm
- Docker (for Lambda function bundling)

## Installation

1. Install dependencies:
```bash
npm install
```

2. Bootstrap CDK (if not already done):
```bash
npx cdk bootstrap
```

## Deployment

```bash
# Deploy the stack
npx cdk deploy

# Check what will be deployed first
npx cdk diff

# Deploy with confirmation prompts
npx cdk deploy --require-approval=broadening
```

## Configuration

The stack uses sensible defaults:
- **Database:** 0.5-4 ACU Aurora PostgreSQL Serverless v2
- **Knowledge Base:** 25K max pages, 300 req/min crawler rate
- **Deletion Protection:** Disabled for easier cleanup during development
- **Storage:** Encrypted at rest with lifecycle policies
- **Knowledge Base Refresh:** Updates on every deployment + daily scheduled refresh at 2 AM UTC

## Stack Outputs

After deployment, the stack provides these outputs:

### Database
- `ClusterArn` - Aurora cluster ARN
- `ClusterEndpoint` - Database connection endpoint
- `SecretArn` - Database credentials secret ARN
- `DatabaseName` - Default database name

### Knowledge Base
- `KnowledgeBaseId` - Bedrock knowledge base ID
- `KnowledgeBaseArn` - Knowledge base ARN
- `DocumentsBucketName` - S3 bucket for additional documents
- `DocumentsBucketArn` - S3 bucket ARN

### FIS Integration
- `FISExecutionRoleArn` - Pre-configured FIS execution role
- `FISExecutionRoleName` - Role name for FIS experiments

## Monitoring and Troubleshooting

### Check Deployment Status
```bash
# List all stacks
npx cdk list

# Check stack status
aws cloudformation describe-stacks --stack-name ChaosAgentDatabaseStack
```

### View Lambda Logs
```bash
# Schema initialization logs
aws logs filter-log-events --log-group-name "/aws/lambda/ChaosAgentDatabaseStack-SchemaInitFunction"

# Knowledge base sync logs
aws logs filter-log-events --log-group-name "/aws/lambda/ChaosAgentDatabaseStack-KnowledgeBaseSyncFunction"
```

### Database Connection
```bash
# Get database credentials
aws secretsmanager get-secret-value --secret-id chaos-agent/database-credentials

# Connect using RDS Data API (recommended)
aws rds-data execute-statement \
  --resource-arn "arn:aws:rds:region:account:cluster:cluster-name" \
  --secret-arn "arn:aws:secretsmanager:region:account:secret:secret-name" \
  --database chaosagent \
  --sql "SELECT version();"
```

## Cleanup

```bash
# Destroy the stack
npx cdk destroy
```

## Development

### Project Structure
```
├── bin/
│   └── chaos-agent-infra.ts     # CDK app entry point
├── lib/
│   └── chaos-agent-database-stack.ts  # Main stack definition
├── lambda/
│   ├── schema-init/             # Database schema initialization
│   └── kb-sync/                 # Knowledge base synchronization
├── package.json                 # Dependencies and scripts
└── README.md                    # This file
```

### Modifying Schema

1. Update schema in `lambda/schema-init/index.py`
2. Increment version in `calculateSchemaHash()` method
3. Deploy to trigger schema update

## Security Considerations

- Database is deployed in private subnets
- All data encrypted at rest and in transit
- IAM roles follow least privilege principle
- Secrets managed through AWS Secrets Manager
- VPC security groups restrict network access

## Cost Optimization

- Aurora Serverless v2 scales to zero when not in use
- S3 lifecycle policies manage document retention
- Lambda functions have appropriate timeout settings
- Knowledge base crawler rate limits prevent excessive API calls

## Support

For issues and questions:
1. Review CloudWatch logs for Lambda functions
2. Examine CloudFormation events for deployment issues
3. Verify AWS service quotas and permissions

## Contributing

1. Create a feature branch from `main`
2. Make changes and test in development environment
3. Update documentation as needed
4. Submit pull request with detailed description

---

**Note:** This infrastructure is designed for chaos engineering experiments. Ensure you understand the implications of running fault injection experiments in your AWS environment.
