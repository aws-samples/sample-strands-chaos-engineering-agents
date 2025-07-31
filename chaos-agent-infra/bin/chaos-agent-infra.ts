#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { ChaosAgentDatabaseStack } from '../lib/chaos-agent-database-stack';

const app = new cdk.App();

new ChaosAgentDatabaseStack(app, 'ChaosAgentDatabaseStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
  description: 'Chaos Agent Database Stack with Aurora PostgreSQL and Bedrock Knowledge Base',
});
