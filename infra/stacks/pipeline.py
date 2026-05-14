import aws_cdk as cdk
from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_events as events,
    aws_events_targets as targets,
    Duration,
)
from constructs import Construct
from infra.stacks.storage import Team49StorageStack
from infra.stacks.graph import Team49GraphStack
from infra.stacks.knowledge import Team49KnowledgeStack


class Team49PipelineStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, storage: Team49StorageStack,
                 graph: Team49GraphStack, knowledge: Team49KnowledgeStack, **kwargs):
        super().__init__(scope, id, **kwargs)

        shared_layer = _lambda.LayerVersion(self, "team49-shared-layer",
            code=_lambda.Code.from_asset("lambdas/shared"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
            description="Shared utilities for ingestion lambdas",
        )

        common_env = {
            "RAW_BUCKET": storage.raw_bucket.bucket_name,
            "CHUNKS_BUCKET": storage.chunks_bucket.bucket_name,
            "CHUNKS_TABLE": storage.chunks_table.table_name,
            "FEATURES_TABLE": storage.features_table.table_name,
            "NEPTUNE_ENDPOINT": graph.cluster.attr_endpoint,
            "KB_ID": knowledge.knowledge_base.attr_knowledge_base_id,
            "DATA_SOURCE_ID": knowledge.data_source.attr_data_source_id,
        }

        def make_lambda(name: str, path: str, timeout: int = 300, memory: int = 512,
                        vpc=None, sg=None, extra_env=None) -> _lambda.Function:
            env = {**common_env, **(extra_env or {})}
            fn = _lambda.Function(self, name,
                function_name=name,
                runtime=_lambda.Runtime.PYTHON_3_12,
                handler="handler.lambda_handler",
                code=_lambda.Code.from_asset(path),
                timeout=Duration.seconds(timeout),
                memory_size=memory,
                layers=[shared_layer],
                environment=env,
                vpc=vpc,
                security_groups=[sg] if sg else None,
            )
            return fn

        # Ingestion Lambdas
        textract_fn = make_lambda("team49-image-textract", "lambdas/ingestion/image_textract")
        storage.raw_bucket.grant_read(textract_fn)
        storage.raw_bucket.grant_put(textract_fn)
        textract_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["textract:AnalyzeDocument", "textract:DetectDocumentText"],
            resources=["*"],
        ))

        metadata_fn = make_lambda("team49-metadata-extractor", "lambdas/ingestion/metadata_extractor")
        storage.raw_bucket.grant_read(metadata_fn)
        storage.features_table.grant_write_data(metadata_fn)
        metadata_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["bedrock:InvokeModel"],
            resources=[f"arn:aws:bedrock:{cdk.Aws.REGION}::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"],
        ))

        chunker_fn = make_lambda("team49-semantic-chunker", "lambdas/ingestion/semantic_chunker")
        storage.raw_bucket.grant_read(chunker_fn)
        storage.chunks_bucket.grant_put(chunker_fn)
        storage.chunks_table.grant_write_data(chunker_fn)

        relationship_fn = make_lambda("team49-relationship-extractor", "lambdas/ingestion/relationship_extractor")
        storage.chunks_bucket.grant_read(relationship_fn)
        relationship_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["bedrock:InvokeModel"],
            resources=[f"arn:aws:bedrock:{cdk.Aws.REGION}::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"],
        ))

        neptune_fn = make_lambda("team49-neptune-writer", "lambdas/ingestion/neptune_writer",
                                 vpc=graph.vpc, sg=graph.lambda_sg)

        metadata_writer_fn = make_lambda("team49-metadata-writer", "lambdas/ingestion/metadata_writer")
        storage.chunks_table.grant_write_data(metadata_writer_fn)

        kb_sync_fn = make_lambda("team49-kb-sync", "lambdas/ingestion/kb_sync", timeout=600)
        kb_sync_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["bedrock:StartIngestionJob", "bedrock:GetIngestionJob"],
            resources=[f"arn:aws:bedrock:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:knowledge-base/*"],
        ))

        # Step Functions workflow
        textract_task = tasks.LambdaInvoke(self, "ExtractText",
            lambda_function=textract_fn,
            output_path="$.Payload",
        )
        metadata_task = tasks.LambdaInvoke(self, "ExtractMetadata",
            lambda_function=metadata_fn,
            output_path="$.Payload",
        )
        chunker_task = tasks.LambdaInvoke(self, "SemanticChunk",
            lambda_function=chunker_fn,
            output_path="$.Payload",
        )
        relationship_task = tasks.LambdaInvoke(self, "ExtractRelationships",
            lambda_function=relationship_fn,
            output_path="$.Payload",
        )
        neptune_task = tasks.LambdaInvoke(self, "WriteToNeptune",
            lambda_function=neptune_fn,
            output_path="$.Payload",
        )
        metadata_writer_task = tasks.LambdaInvoke(self, "WriteMetadata",
            lambda_function=metadata_writer_fn,
            output_path="$.Payload",
        )
        kb_sync_task = tasks.LambdaInvoke(self, "SyncKnowledgeBase",
            lambda_function=kb_sync_fn,
            output_path="$.Payload",
        )

        chain = (
            textract_task
            .next(metadata_task)
            .next(chunker_task)
            .next(relationship_task)
            .next(neptune_task)
            .next(metadata_writer_task)
            .next(kb_sync_task)
        )

        self.state_machine = sfn.StateMachine(self, "team49-ingestion-pipeline",
            state_machine_name="team49-ingestion-pipeline",
            definition_body=sfn.DefinitionBody.from_chainable(chain),
            timeout=Duration.minutes(30),
        )

        # EventBridge rule for S3 uploads
        rule = events.Rule(self, "team49-s3-upload-rule",
            rule_name="team49-s3-upload-trigger",
            event_pattern=events.EventPattern(
                source=["aws.s3"],
                detail_type=["Object Created"],
                detail={
                    "bucket": {"name": [storage.raw_bucket.bucket_name]},
                    "object": {"key": [{"prefix": "3gpp/"}, {"prefix": "whitepapers/"}]},
                },
            ),
        )
        rule.add_target(targets.SfnStateMachine(self.state_machine))
