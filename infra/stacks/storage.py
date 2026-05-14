import aws_cdk as cdk
from aws_cdk import (
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_kms as kms,
)
from constructs import Construct


class Team49StorageStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.kms_key = kms.Key(self, "team49-cmk",
            alias="team49-knowledge-graph-key",
            enable_key_rotation=True,
        )

        self.raw_bucket = s3.Bucket(self, "team49-raw-bucket",
            bucket_name=f"team49-raw-{cdk.Aws.ACCOUNT_ID}",
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.kms_key,
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            event_bridge_enabled=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        self.chunks_bucket = s3.Bucket(self, "team49-chunks-bucket",
            bucket_name=f"team49-chunks-{cdk.Aws.ACCOUNT_ID}",
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.kms_key,
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        self.chunks_table = dynamodb.Table(self, "team49-chunks-table",
            table_name="team49-chunks-table",
            partition_key=dynamodb.Attribute(name="chunk_id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )
        self.chunks_table.add_global_secondary_index(
            index_name="spec-release-index",
            partition_key=dynamodb.Attribute(name="spec_release", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="section", type=dynamodb.AttributeType.STRING),
        )

        self.features_table = dynamodb.Table(self, "team49-features-table",
            table_name="team49-features-table",
            partition_key=dynamodb.Attribute(name="feature_id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )
