import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract cluster ARN and secret ARN from event
        cluster_arn = event['ResourceProperties']['ClusterArn']
        secret_arn = event['ResourceProperties']['SecretArn']
        database_name = event['ResourceProperties']['DatabaseName']
        
        rds_data = boto3.client('rds-data')
        
        def execute_sql(sql_statement):
            """Execute a single SQL statement"""
            logger.info(f"Executing SQL: {sql_statement[:100]}...")
            response = rds_data.execute_statement(
                resourceArn=cluster_arn,
                secretArn=secret_arn,
                database=database_name,
                sql=sql_statement
            )
            logger.info(f"SQL execution response: {response}")
            return response
        
        # Define individual SQL statements for schema creation
        schema_statements = [
            """CREATE TABLE IF NOT EXISTS system_component (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                type VARCHAR(100) NOT NULL,
                description TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )""",
            
            """CREATE TABLE IF NOT EXISTS hypothesis (
                id SERIAL PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                description TEXT,
                persona VARCHAR(255),
                steady_state_description TEXT,
                failure_mode TEXT,
                status VARCHAR(50) DEFAULT 'proposed',
                priority INTEGER DEFAULT 1,
                notes TEXT,
                system_component_id INTEGER REFERENCES system_component(id),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )""",
            
            """CREATE TABLE IF NOT EXISTS experiment (
                id SERIAL PRIMARY KEY,
                hypothesis_id INTEGER REFERENCES hypothesis(id),
                title VARCHAR(500) NOT NULL,
                description TEXT,
                experiment_plan TEXT,
                fis_configuration JSONB,
                fis_role_configuration JSONB,
                fis_experiment_id VARCHAR(255),
                experiment_notes TEXT,
                status VARCHAR(50) DEFAULT 'draft',
                scheduled_for TIMESTAMP WITH TIME ZONE,
                executed_at TIMESTAMP WITH TIME ZONE,
                completed_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )""",
            
            """CREATE TABLE IF NOT EXISTS learning_insights (
                id SERIAL PRIMARY KEY,
                experiment_id INTEGER REFERENCES experiment(id),
                key_learnings TEXT,
                recommendations TEXT,
                refined_hypotheses TEXT,
                risk_assessment TEXT,
                knowledge_gaps TEXT,
                follow_up_experiments TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )""",
            
            """CREATE TABLE IF NOT EXISTS source_code_analysis (
                id SERIAL PRIMARY KEY,
                repository_url VARCHAR(500) NOT NULL,
                analysis_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                framework_stack JSONB,
                aws_services_detected JSONB,
                infrastructure_patterns JSONB,
                deployment_methods JSONB,
                architectural_summary TEXT,
                failure_points_analysis TEXT,
                recommendations TEXT
            )""",
            
            """CREATE TABLE IF NOT EXISTS aws_resource_analysis (
                id SERIAL PRIMARY KEY,
                resource_type VARCHAR(100),
                resource_id VARCHAR(500) UNIQUE,
                aws_account_id VARCHAR(20),
                region VARCHAR(20),
                analysis_results JSONB,
                deployment_status VARCHAR(50) DEFAULT 'unknown',
                resource_metadata JSONB,
                analysis_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                service_inventory JSONB,
                network_topology JSONB,
                security_groups_summary JSONB,
                cross_service_dependencies JSONB,
                architecture_assessment TEXT,
                resilience_gaps TEXT,
                scaling_bottlenecks TEXT,
                security_recommendations TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )""",
            
            """CREATE TABLE IF NOT EXISTS hypothesis_evaluation (
                id SERIAL PRIMARY KEY,
                hypothesis_id INTEGER NOT NULL REFERENCES hypothesis(id),
                testability_score INTEGER NOT NULL CHECK (testability_score BETWEEN 1 AND 5),
                specificity_score INTEGER NOT NULL CHECK (specificity_score BETWEEN 1 AND 5),
                realism_score INTEGER NOT NULL CHECK (realism_score BETWEEN 1 AND 5),
                safety_score INTEGER NOT NULL CHECK (safety_score BETWEEN 1 AND 5),
                learning_value_score INTEGER NOT NULL CHECK (learning_value_score BETWEEN 1 AND 5),
                overall_score NUMERIC(3,2) NOT NULL,
                evaluation_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (hypothesis_id)
            )"""
        ]
        
        # Execute schema creation statements
        logger.info("Creating database schema...")
        for statement in schema_statements:
            execute_sql(statement)
        
        # Add missing columns to existing tables (for schema updates)
        logger.info("Updating existing table schemas...")
        alter_statements = [
            """ALTER TABLE aws_resource_analysis ADD COLUMN IF NOT EXISTS resource_type VARCHAR(100)""",
            """ALTER TABLE aws_resource_analysis ADD COLUMN IF NOT EXISTS resource_id VARCHAR(500)""",
            """ALTER TABLE aws_resource_analysis ADD COLUMN IF NOT EXISTS deployment_status VARCHAR(50) DEFAULT 'unknown'""",
            """ALTER TABLE aws_resource_analysis ADD COLUMN IF NOT EXISTS resource_metadata JSONB""",
            """ALTER TABLE aws_resource_analysis ADD COLUMN IF NOT EXISTS analysis_results JSONB""",
            """ALTER TABLE aws_resource_analysis ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP""",
            """ALTER TABLE aws_resource_analysis ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"""
        ]
        
        for statement in alter_statements:
            try:
                execute_sql(statement)
                logger.info(f"Successfully executed: {statement[:50]}...")
            except Exception as e:
                logger.warning(f"Alter statement failed (may already exist): {statement[:50]}... - {str(e)}")
        
        # Add unique constraint if it doesn't exist
        try:
            execute_sql("""ALTER TABLE aws_resource_analysis ADD CONSTRAINT unique_resource_id UNIQUE (resource_id)""")
            logger.info("Added unique constraint on resource_id")
        except Exception as e:
            logger.warning(f"Unique constraint may already exist: {str(e)}")
        
        # Create indexes (individual statements)
        index_statements = [
            "CREATE INDEX IF NOT EXISTS idx_hypothesis_status ON hypothesis(status)",
            "CREATE INDEX IF NOT EXISTS idx_hypothesis_priority ON hypothesis(priority)",
            "CREATE INDEX IF NOT EXISTS idx_hypothesis_system_component ON hypothesis(system_component_id)",
            "CREATE INDEX IF NOT EXISTS idx_experiment_status ON experiment(status)",
            "CREATE INDEX IF NOT EXISTS idx_experiment_hypothesis ON experiment(hypothesis_id)",
            "CREATE INDEX IF NOT EXISTS idx_experiment_scheduled ON experiment(scheduled_for)",
            "CREATE INDEX IF NOT EXISTS idx_hypothesis_evaluation_hypothesis_id ON hypothesis_evaluation(hypothesis_id)",
            "CREATE INDEX IF NOT EXISTS idx_hypothesis_evaluation_overall_score ON hypothesis_evaluation(overall_score DESC)"
        ]
        
        logger.info("Creating database indexes...")
        for statement in index_statements:
            execute_sql(statement)
        
        # Insert sample data (individual statements)
        sample_data_statements = [
            """INSERT INTO system_component (name, type, description) VALUES
                ('Web API', 'ECS Service', 'Main web API service running on ECS')
                ON CONFLICT DO NOTHING""",
            """INSERT INTO system_component (name, type, description) VALUES
                ('User Database', 'RDS PostgreSQL', 'Primary user data database')
                ON CONFLICT DO NOTHING""",
            """INSERT INTO system_component (name, type, description) VALUES
                ('Cache Layer', 'ElastiCache Redis', 'Redis cache for session and application data')
                ON CONFLICT DO NOTHING""",
            """INSERT INTO system_component (name, type, description) VALUES
                ('File Storage', 'S3 Bucket', 'Object storage for user uploads and static assets')
                ON CONFLICT DO NOTHING""",
            """INSERT INTO system_component (name, type, description) VALUES
                ('Background Jobs', 'Lambda Functions', 'Serverless functions for background processing')
                ON CONFLICT DO NOTHING""",
            """INSERT INTO hypothesis (title, description, persona, steady_state_description, failure_mode, status, priority, system_component_id) VALUES
                ('API maintains performance during ECS task restarts',
                 'The web API should maintain response times under 500ms and >95% success rate when ECS tasks are restarted',
                 'End User',
                 'API response time < 500ms, Success rate > 95%, All endpoints accessible',
                 'ECS tasks are randomly restarted, simulating container failures',
                 'proposed',
                 3,
                 1)
                ON CONFLICT DO NOTHING""",
            """INSERT INTO hypothesis (title, description, persona, steady_state_description, failure_mode, status, priority, system_component_id) VALUES
                ('System resilience during database connection failures',
                 'Application should gracefully handle database connection failures with appropriate fallbacks',
                 'Application Developer',
                 'Database queries complete successfully, Application remains responsive, Error rates < 1%',
                 'Database connections are terminated or network partitions occur',
                 'proposed',
                 2,
                 2)
                ON CONFLICT DO NOTHING""",
            """INSERT INTO hypothesis (title, description, persona, steady_state_description, failure_mode, status, priority, system_component_id) VALUES
                ('Cache failure does not impact core functionality',
                 'Core application features should remain functional when Redis cache is unavailable',
                 'End User',
                 'Core features work normally, Response times may increase but stay < 2s, No data loss',
                 'Redis cache becomes unavailable or returns errors',
                 'prioritized',
                 1,
                 3)
                ON CONFLICT DO NOTHING"""
        ]
        
        logger.info("Inserting sample data...")
        for statement in sample_data_statements:
            execute_sql(statement)
        
        # Create view
        # Add comments to the hypothesis_evaluation table
        comment_statements = [
            """COMMENT ON TABLE hypothesis_evaluation IS 'Stores quality evaluations of chaos engineering hypotheses'""",
            """COMMENT ON COLUMN hypothesis_evaluation.hypothesis_id IS 'Reference to the evaluated hypothesis'""",
            """COMMENT ON COLUMN hypothesis_evaluation.testability_score IS 'Score for how testable the hypothesis is with AWS FIS (1-5)'""",
            """COMMENT ON COLUMN hypothesis_evaluation.specificity_score IS 'Score for how specific the failure conditions and expected behavior are (1-5)'""",
            """COMMENT ON COLUMN hypothesis_evaluation.realism_score IS 'Score for how realistic the failure scenario is in production (1-5)'""",
            """COMMENT ON COLUMN hypothesis_evaluation.safety_score IS 'Score for how well bounded the blast radius is (1-5)'""",
            """COMMENT ON COLUMN hypothesis_evaluation.learning_value_score IS 'Score for how valuable the insights from testing would be (1-5)'""",
            """COMMENT ON COLUMN hypothesis_evaluation.overall_score IS 'Average of all individual scores, rounded to two decimal places'""",
            """COMMENT ON COLUMN hypothesis_evaluation.evaluation_timestamp IS 'When the evaluation was performed'"""
        ]
        
        logger.info("Adding table and column comments...")
        for statement in comment_statements:
            execute_sql(statement)
        
        view_sql = """CREATE OR REPLACE VIEW experiment_with_hypothesis AS
        SELECT 
            e.id,
            e.title,
            e.description,
            e.experiment_plan,
            e.status,
            e.scheduled_for,
            e.executed_at,
            e.completed_at,
            e.created_at,
            h.title as hypothesis_title,
            h.description as hypothesis_description,
            h.status as hypothesis_status,
            sc.name as component_name,
            sc.type as component_type
        FROM experiment e
        LEFT JOIN hypothesis h ON e.hypothesis_id = h.id
        LEFT JOIN system_component sc ON h.system_component_id = sc.id"""
        
        logger.info("Creating database view...")
        execute_sql(view_sql)
        
        logger.info("Database schema initialization completed successfully!")
        return {
            'statusCode': 200,
            'body': json.dumps('Database schema created successfully')
        }
        
    except Exception as e:
        logger.error(f"Error initializing database schema: {str(e)}")
        raise e
