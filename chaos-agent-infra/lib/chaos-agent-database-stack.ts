import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as cr from 'aws-cdk-lib/custom-resources';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import { bedrock } from '@cdklabs/generative-ai-cdk-constructs';
import { Construct } from 'constructs';
import * as crypto from 'crypto';

export class ChaosAgentDatabaseStack extends cdk.Stack {
  public readonly knowledgeBase: bedrock.VectorKnowledgeBase;
  public readonly documentsBucket: s3.Bucket;
  public readonly queryRole: iam.Role;
  public readonly fisExecutionRole: iam.Role;
  public readonly logGroups: { [key: string]: logs.LogGroup };
  public readonly observabilityRole: iam.Role;

 private calculateSchemaHash(): string {
    // Prevents unnecessary database schema re-initialization on every deployment
    // Only triggers schema Lambda when table definitions or version actually change
    // This avoids expensive database operations and potential disruption
    const schemaContent = JSON.stringify({
      tables: ['system_component', 'hypothesis', 'experiment', 'learning_insights', 'source_code_analysis', 'aws_resource_analysis'],
      version: '1.3.0',
      changes: [
        'Added ALTER TABLE statements for existing table updates',
        'Added resource_type, resource_id, deployment_status, resource_metadata columns',
        'Added analysis_results, created_at, updated_at columns',
        'Added unique constraint on resource_id for deployment filtering'
      ]
    });
    return crypto.createHash('md5').update(schemaContent).digest('hex');
  }

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Use sensible defaults for all configurations
    const databaseConfig = {
      minCapacity: 0.5,
      maxCapacity: 4,
      deletionProtection: false, // For demo purposes, make cleanup easier
    };
    const knowledgeBaseConfig = {
      enableWebCrawler: true,
      crawlerRateLimit: 300,
      maxPages: 25000,
    };

    // 1. Create VPC with 2 AZs and single NAT Gateway
    const vpc = new ec2.Vpc(this, 'ChaosAgentVPC', {
      maxAzs: 2,
      natGateways: 1,
      subnetConfiguration: [
        {
          name: 'public',
          subnetType: ec2.SubnetType.PUBLIC,
          cidrMask: 24,
        },
        {
          name: 'private',
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
          cidrMask: 24,
        },
      ],
    });

    // 2. Create Security Group for Aurora
    const dbSecurityGroup = new ec2.SecurityGroup(this, 'DatabaseSecurityGroup', {
      vpc,
      description: 'Security group for Aurora Serverless database',
      allowAllOutbound: true,
    });
    
    // Allow connections from within the VPC
    dbSecurityGroup.addIngressRule(
      ec2.Peer.ipv4(vpc.vpcCidrBlock),
      ec2.Port.tcp(5432),
      'Allow PostgreSQL access from within VPC'
    );

    // 3. Create Secrets Manager secret for database credentials
    const databaseCredentialsSecret = new secretsmanager.Secret(this, 'DBCredentialsSecret', {
      secretName: 'chaos-agent/database-credentials',
      generateSecretString: {
        secretStringTemplate: JSON.stringify({ username: 'postgres' }),
        generateStringKey: 'password',
        excludePunctuation: true,
        includeSpace: false,
        passwordLength: 16,
      },
    });

    // 4. Create Aurora PostgreSQL Serverless v2 cluster with Data API enabled
    const cluster = new rds.DatabaseCluster(this, 'ChaosAgentDatabase', {
      engine: rds.DatabaseClusterEngine.auroraPostgres({
        version: rds.AuroraPostgresEngineVersion.VER_15_3
      }),
      // CORRECTED: Explicitly define a serverless writer instance.
      // This satisfies the L2 construct's requirement for a writer,
      // resolving the "writer must be provided" error.
      writer: rds.ClusterInstance.serverlessV2('writer'),
      vpc,
      vpcSubnets: {
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
      },
      securityGroups: [dbSecurityGroup],
      defaultDatabaseName: 'chaosagent',
      credentials: rds.Credentials.fromSecret(databaseCredentialsSecret),
      deletionProtection: databaseConfig.deletionProtection,
      storageEncrypted: true,
      // Use environment-specific scaling configuration
      serverlessV2MinCapacity: databaseConfig.minCapacity,
      serverlessV2MaxCapacity: databaseConfig.maxCapacity,
      enableDataApi: true
    });
    
    // 5. Create Lambda function for database schema initialization
    const schemaInitFunction = new lambda.Function(this, 'SchemaInitFunction', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.handler',
      timeout: cdk.Duration.minutes(5),
      code: lambda.Code.fromAsset('./lambda/schema-init'),
    });

    // Grant the Lambda function permissions to use RDS Data API and Secrets Manager
    schemaInitFunction.addToRolePolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'rds-data:ExecuteStatement',
        'rds-data:BatchExecuteStatement',
        'rds-data:BeginTransaction',
        'rds-data:CommitTransaction',
        'rds-data:RollbackTransaction',
      ],
      resources: [cluster.clusterArn],
    }));

    schemaInitFunction.addToRolePolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'secretsmanager:GetSecretValue',
        'secretsmanager:DescribeSecret',
      ],
      resources: [databaseCredentialsSecret.secretArn],
    }));

    // 6. Create Custom Resource to trigger schema initialization
    const schemaInitProvider = new cr.Provider(this, 'SchemaInitProvider', {
      onEventHandler: schemaInitFunction,
    });

    const schemaInitResource = new cdk.CustomResource(this, 'SchemaInitResource', {
      serviceToken: schemaInitProvider.serviceToken,
      properties: {
        ClusterArn: cluster.clusterArn,
        SecretArn: databaseCredentialsSecret.secretArn,
        DatabaseName: 'chaosagent',
        // Use content-based hash to prevent unnecessary database schema re-initialization
        // Only triggers when table definitions or version change, avoiding expensive DB operations
        SchemaVersion: this.calculateSchemaHash(),
      },
    });

    // Ensure the custom resource runs after the cluster is ready
    schemaInitResource.node.addDependency(cluster);

    // 7. Create S3 bucket for storing additional documents
    this.documentsBucket = new s3.Bucket(this, 'ChaosAgentDocumentsBucket', {
      bucketName: `chaos-agent-documents-${this.account}-${this.region}`,
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.DESTROY, // For demo purposes
      autoDeleteObjects: true, // For demo purposes
      lifecycleRules: [
        {
          id: 'DeleteOldVersions',
          enabled: true,
          noncurrentVersionExpiration: cdk.Duration.days(30),
        },
      ],
    });

    // 8. Create the Vector Knowledge Base with OpenSearch Serverless
    this.knowledgeBase = new bedrock.VectorKnowledgeBase(this, 'ChaosAgentKnowledgeBase', {
      name: 'chaos-agent-knowledge-base',
      description: 'Knowledge base for Chaos Engineering and AWS FIS documentation',
      embeddingsModel: bedrock.BedrockFoundationModel.TITAN_EMBED_TEXT_V2_1024,
      instruction: `Use this knowledge base to answer questions about chaos engineering, 
        AWS Fault Injection Simulator (FIS), system resilience, and infrastructure testing. 
        It contains official AWS documentation for FIS actions, parameters, resource types, 
        and best practices for chaos engineering experiments.`,
      // OpenSearch Serverless will be created automatically
    });

    // 9. Add Web Crawler data source for AWS FIS documentation
    const webCrawlerDataSources: bedrock.WebCrawlerDataSource[] = [];
    const fisCrawlerDataSource = new bedrock.WebCrawlerDataSource(this, 'FISWebCrawler', {
      knowledgeBase: this.knowledgeBase,
      dataSourceName: 'aws-fis-documentation-resources',
      description: 'AWS FIS official documentation crawler',
      sourceUrls: [
        // Core FIS documentation URLs
        'https://docs.aws.amazon.com/fis/latest/userguide/fis-actions-reference.html',
        'https://docs.aws.amazon.com/fis/latest/userguide/actions-ssm-agent.html',
        'https://docs.aws.amazon.com/fis/latest/userguide/ecs-task-actions.html',
        'https://docs.aws.amazon.com/fis/latest/userguide/eks-pod-actions.html',
        'https://docs.aws.amazon.com/fis/latest/userguide/use-lambda-actions.html',
               
        // Experiment management
        'https://docs.aws.amazon.com/fis/latest/userguide/experiments.html',
        'https://docs.aws.amazon.com/fis/latest/userguide/experiment-templates.html',
        'https://docs.aws.amazon.com/fis/latest/userguide/targets.html',
        'https://docs.aws.amazon.com/fis/latest/userguide/stop-conditions.html',
      ],
      chunkingStrategy: bedrock.ChunkingStrategy.fixedSize({
        maxTokens: 500,
        overlapPercentage: 20,
      }),
    });

    webCrawlerDataSources.push(fisCrawlerDataSource);

    // 10. Add S3 data source for additional chaos engineering resources
    const s3DataSource = new bedrock.S3DataSource(this, 'ChaosEngineeringS3DataSource', {
      bucket: this.documentsBucket,
      knowledgeBase: this.knowledgeBase,
      dataSourceName: 'chaos-engineering-s3-resources',
      description: 'Additional chaos engineering documentation and best practices from S3',
      chunkingStrategy: bedrock.ChunkingStrategy.semantic({
        bufferSize: 1,
        breakpointPercentileThreshold: 95,
        maxTokens: 300,
      }),
    });

    // 11. Create Lambda function for knowledge base sync
    const kbSyncFunction = new lambda.Function(this, 'KnowledgeBaseSyncFunction', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.handler',
      timeout: cdk.Duration.minutes(15),
      code: lambda.Code.fromAsset('./lambda/kb-sync'),
      description: 'Custom resource to sync knowledge base data sources',
    });

    // Grant the Lambda function permissions to manage Bedrock knowledge base ingestion
    kbSyncFunction.addToRolePolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'bedrock:StartIngestionJob',
        'bedrock:GetIngestionJob',
        'bedrock:ListIngestionJobs',
        'bedrock:StopIngestionJob',
        'bedrock:ListDataSources',
      ],
      resources: [
        this.knowledgeBase.knowledgeBaseArn,
        `${this.knowledgeBase.knowledgeBaseArn}/*`,
      ],
    }));

    // 12. Create Custom Resource to trigger knowledge base sync
    const kbSyncProvider = new cr.Provider(this, 'KnowledgeBaseSyncProvider', {
      onEventHandler: kbSyncFunction,
    });

    // Collect all data source IDs
    const allDataSourceIds = [
      ...webCrawlerDataSources.map(ds => ds.dataSourceId),
      s3DataSource.dataSourceId,
    ];

    const kbSyncResource = new cdk.CustomResource(this, 'KnowledgeBaseSyncResource', {
      serviceToken: kbSyncProvider.serviceToken,
      properties: {
        KnowledgeBaseId: this.knowledgeBase.knowledgeBaseId,
        DataSourceIds: allDataSourceIds,
        // Use timestamp to ensure refresh on every deployment
        Timestamp: new Date().toISOString(),
      },
    });

    // Ensure the sync runs after all data sources are created
    kbSyncResource.node.addDependency(this.knowledgeBase);
    webCrawlerDataSources.forEach(ds => kbSyncResource.node.addDependency(ds));
    kbSyncResource.node.addDependency(s3DataSource);

    // 12a. Create EventBridge rule for periodic knowledge base refresh
    const kbRefreshRule = new events.Rule(this, 'KnowledgeBaseRefreshRule', {
      description: 'Periodic refresh of knowledge base documentation',
      // Run daily at 2 AM UTC to refresh external documentation
      schedule: events.Schedule.cron({
        minute: '0',
        hour: '2',
        day: '*',
        month: '*',
        year: '*',
      }),
    });

    // Add the knowledge base sync function as a target
    kbRefreshRule.addTarget(new targets.LambdaFunction(kbSyncFunction, {
      event: events.RuleTargetInput.fromObject({
        // Simulate a custom resource event for periodic refresh
        RequestType: 'Update',
        ResourceProperties: {
          KnowledgeBaseId: this.knowledgeBase.knowledgeBaseId,
          DataSourceIds: allDataSourceIds,
          TriggerType: 'Scheduled', // Distinguish from CDK deployment triggers
          ConfigHash: 'scheduled-refresh', // Static hash for scheduled refreshes
        },
      }),
    }));

    // Grant EventBridge permission to invoke the Lambda function
    kbSyncFunction.addPermission('AllowEventBridgeInvoke', {
      principal: new iam.ServicePrincipal('events.amazonaws.com'),
      sourceArn: kbRefreshRule.ruleArn,
    });

    // 13. Create IAM role for applications to query the knowledge base
    this.queryRole = new iam.Role(this, 'KnowledgeBaseQueryRole', {
      roleName: 'ChaosAgentKnowledgeBaseQueryRole',
      assumedBy: new iam.CompositePrincipal(
        new iam.ServicePrincipal('lambda.amazonaws.com'),
        new iam.ServicePrincipal('bedrock.amazonaws.com'),
        // Allow EC2 instances or other compute to assume this role
        new iam.ServicePrincipal('ec2.amazonaws.com'),
      ),
      description: 'Role for querying the Chaos Agent knowledge base',
    });

    // Grant permissions to query the knowledge base
    this.knowledgeBase.grantQuery(this.queryRole);
    this.knowledgeBase.grantRetrieve(this.queryRole);
    this.knowledgeBase.grantRetrieveAndGenerate(this.queryRole);

    // Grant permissions to invoke Bedrock models
    this.queryRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'bedrock:InvokeModel',
        'bedrock:InvokeModelWithResponseStream',
      ],
      resources: [
        `arn:aws:bedrock:${this.region}::foundation-model/*`,
      ],
    }));

    // 14. Create CloudWatch Log Groups for Observability
    this.logGroups = {};
    const logRetentionDays = logs.RetentionDays.ONE_MONTH; // 30 days retention

    // Agent-specific log groups
    const agentNames = [
      'hypothesis-generator',
      'prioritization', 
      'experiment-design',
      'experiments',
      'learning-iteration'
    ];

    agentNames.forEach(agentName => {
      this.logGroups[agentName] = new logs.LogGroup(this, `${agentName}LogGroup`, {
        logGroupName: `/chaos-agent/agents/${agentName}`,
        retention: logRetentionDays,
        removalPolicy: cdk.RemovalPolicy.DESTROY, // For demo purposes
      });
    });

    // System-wide log groups
    this.logGroups['workflow'] = new logs.LogGroup(this, 'WorkflowLogGroup', {
      logGroupName: '/chaos-agent/workflow',
      retention: logRetentionDays,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    this.logGroups['system'] = new logs.LogGroup(this, 'SystemLogGroup', {
      logGroupName: '/chaos-agent/system',
      retention: logRetentionDays,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // 15. Create IAM role for observability (CloudWatch Logs access)
    this.observabilityRole = new iam.Role(this, 'ObservabilityRole', {
      roleName: 'ChaosAgentObservabilityRole',
      assumedBy: new iam.CompositePrincipal(
        new iam.ServicePrincipal('lambda.amazonaws.com'),
        new iam.ServicePrincipal('ec2.amazonaws.com'),
        // Allow local execution environments to assume this role
        new iam.AccountRootPrincipal(),
      ),
      description: 'Role for Chaos Agent observability and CloudWatch Logs access',
    });

    // Grant permissions to write to all Chaos Agent log groups
    Object.values(this.logGroups).forEach(logGroup => {
      logGroup.grantWrite(this.observabilityRole);
    });

    // Grant additional CloudWatch permissions
    this.observabilityRole.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'logs:CreateLogStream',
        'logs:PutLogEvents',
        'logs:DescribeLogGroups',
        'logs:DescribeLogStreams',
        'cloudwatch:PutMetricData',
      ],
      resources: [
        `arn:aws:logs:${this.region}:${this.account}:log-group:/chaos-agent/*`,
        `arn:aws:logs:${this.region}:${this.account}:log-group:/chaos-agent/*:*`,
        `arn:aws:cloudwatch:${this.region}:${this.account}:metric/ChaosAgent/*`,
      ],
    }));

    // 16. Create CloudWatch Dashboard for monitoring
    const dashboard = new cloudwatch.Dashboard(this, 'ChaosAgentDashboard', {
      dashboardName: 'ChaosAgent-Observability',
      widgets: [
        [
          new cloudwatch.TextWidget({
            markdown: '# Chaos Agent Observability Dashboard\n\nMonitoring agent execution, errors, and performance metrics.\n\n## Log Groups\n\n' +
              Object.entries(this.logGroups).map(([name, lg]) => 
                `- **${name}**: [${lg.logGroupName}](https://${this.region}.console.aws.amazon.com/cloudwatch/home?region=${this.region}#logsV2:log-groups/log-group/${encodeURIComponent(lg.logGroupName)})`
              ).join('\n'),
            width: 24,
            height: 8,
          }),
        ],
      ],
    });

    // 17. Create pre-generated FIS execution role with all managed policies
    this.fisExecutionRole = new iam.Role(this, 'FISExecutionRole', {
      roleName: 'ChaosAgentFISExecutionRole',
      assumedBy: new iam.ServicePrincipal('fis.amazonaws.com'),
      description: 'Pre-generated IAM role for AWS FIS experiment execution across all services',
      managedPolicies: [
        // All AWS managed policies for FIS by service
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSFaultInjectionSimulatorEC2Access'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSFaultInjectionSimulatorECSAccess'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSFaultInjectionSimulatorEKSAccess'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSFaultInjectionSimulatorRDSAccess'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSFaultInjectionSimulatorNetworkAccess'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSFaultInjectionSimulatorSSMAccess'),
      ],
    });

    // 18. Output important information
    new cdk.CfnOutput(this, 'SecretArn', {
      value: databaseCredentialsSecret.secretArn,
      description: 'ARN of the database credentials secret',
      exportName: 'ChaosAgentDatabaseSecretArn',
    });
    
    new cdk.CfnOutput(this, 'ClusterArn', {
      value: cluster.clusterArn,
      description: 'ARN of the Aurora Serverless cluster',
      exportName: 'ChaosAgentDatabaseClusterArn',
    });
    
    new cdk.CfnOutput(this, 'ClusterEndpoint', {
      value: cluster.clusterEndpoint.socketAddress,
      description: 'Endpoint of the Aurora Serverless cluster',
      exportName: 'ChaosAgentDatabaseEndpoint',
    });
    
    new cdk.CfnOutput(this, 'DatabaseName', {
      value: 'chaosagent',
      description: 'Name of the default database',
      exportName: 'ChaosAgentDatabaseName',
    });

    // Bedrock Knowledge Base Outputs
    new cdk.CfnOutput(this, 'KnowledgeBaseId', {
      value: this.knowledgeBase.knowledgeBaseId,
      description: 'ID of the Chaos Agent Knowledge Base',
      exportName: 'ChaosAgentKnowledgeBaseId',
    });

    new cdk.CfnOutput(this, 'KnowledgeBaseArn', {
      value: this.knowledgeBase.knowledgeBaseArn,
      description: 'ARN of the Chaos Agent Knowledge Base',
      exportName: 'ChaosAgentKnowledgeBaseArn',
    });

    new cdk.CfnOutput(this, 'DocumentsBucketName', {
      value: this.documentsBucket.bucketName,
      description: 'Name of the documents S3 bucket',
      exportName: 'ChaosAgentDocumentsBucketName',
    });

    new cdk.CfnOutput(this, 'DocumentsBucketArn', {
      value: this.documentsBucket.bucketArn,
      description: 'ARN of the documents S3 bucket',
      exportName: 'ChaosAgentDocumentsBucketArn',
    });

    // FIS execution role outputs
    new cdk.CfnOutput(this, 'FISExecutionRoleArn', {
      value: this.fisExecutionRole.roleArn,
      description: 'ARN of the pre-generated FIS execution role',
      exportName: 'ChaosAgentFISExecutionRoleArn',
    });

    new cdk.CfnOutput(this, 'FISExecutionRoleName', {
      value: this.fisExecutionRole.roleName,
      description: 'Name of the pre-generated FIS execution role',
      exportName: 'ChaosAgentFISExecutionRoleName',
    });

    // Observability outputs
    new cdk.CfnOutput(this, 'ObservabilityRoleArn', {
      value: this.observabilityRole.roleArn,
      description: 'ARN of the observability role for CloudWatch Logs access',
      exportName: 'ChaosAgentObservabilityRoleArn',
    });

    new cdk.CfnOutput(this, 'DashboardUrl', {
      value: `https://${this.region}.console.aws.amazon.com/cloudwatch/home?region=${this.region}#dashboards:name=ChaosAgent-Observability`,
      description: 'URL to the CloudWatch Dashboard',
      exportName: 'ChaosAgentDashboardUrl',
    });

    // Log group outputs
    Object.entries(this.logGroups).forEach(([name, logGroup]) => {
      new cdk.CfnOutput(this, `${name}LogGroupName`, {
        value: logGroup.logGroupName,
        description: `CloudWatch Log Group for ${name}`,
        exportName: `ChaosAgent${name.charAt(0).toUpperCase() + name.slice(1)}LogGroup`,
      });
    });

    // Tags
    cdk.Tags.of(this).add('Project', 'ChaosAgent');
    cdk.Tags.of(this).add('Component', 'Infrastructure');
    cdk.Tags.of(this).add('Environment', 'Development');
  }
}
