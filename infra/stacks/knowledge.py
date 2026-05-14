import aws_cdk as cdk
from aws_cdk import (
    aws_opensearchserverless as oss,
    aws_iam as iam,
    aws_bedrock as bedrock,
)
from constructs import Construct
from infra.stacks.storage import Team49StorageStack


class Team49KnowledgeStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, storage: Team49StorageStack, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.collection_name = "team49-kb-collection"

        encryption_policy = oss.CfnSecurityPolicy(self, "team49-encryption-policy",
            name="team49-encryption-policy",
            type="encryption",
            policy=cdk.Fn.sub(
                '{"Rules":[{"ResourceType":"collection","Resource":["collection/${name}"]}],"AWSOwnedKey":true}',
                {"name": self.collection_name}
            ),
        )

        network_policy = oss.CfnSecurityPolicy(self, "team49-network-policy",
            name="team49-network-policy",
            type="network",
            policy=cdk.Fn.sub(
                '[{"Rules":[{"ResourceType":"collection","Resource":["collection/${name}"]},{"ResourceType":"dashboard","Resource":["collection/${name}"]}],"AllowFromPublic":true}]',
                {"name": self.collection_name}
            ),
        )

        self.collection = oss.CfnCollection(self, "team49-kb-collection",
            name=self.collection_name,
            type="VECTORSEARCH",
        )
        self.collection.add_dependency(encryption_policy)
        self.collection.add_dependency(network_policy)

        self.kb_role = iam.Role(self, "team49-kb-role",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
            inline_policies={
                "s3-access": iam.PolicyDocument(statements=[
                    iam.PolicyStatement(
                        actions=["s3:GetObject", "s3:ListBucket"],
                        resources=[
                            storage.chunks_bucket.bucket_arn,
                            f"{storage.chunks_bucket.bucket_arn}/*",
                        ],
                    ),
                ]),
                "oss-access": iam.PolicyDocument(statements=[
                    iam.PolicyStatement(
                        actions=["aoss:APIAccessAll"],
                        resources=[self.collection.attr_arn],
                    ),
                ]),
            },
        )

        data_access_policy = oss.CfnAccessPolicy(self, "team49-data-access-policy",
            name="team49-data-access-policy",
            type="data",
            policy=cdk.Fn.sub(
                '[{"Rules":[{"ResourceType":"index","Resource":["index/${name}/*"],"Permission":["aoss:CreateIndex","aoss:UpdateIndex","aoss:DescribeIndex","aoss:ReadDocument","aoss:WriteDocument"]},{"ResourceType":"collection","Resource":["collection/${name}"],"Permission":["aoss:CreateCollectionItems","aoss:DescribeCollectionItems","aoss:UpdateCollectionItems"]}],"Principal":["${role}"]}]',
                {"name": self.collection_name, "role": self.kb_role.role_arn}
            ),
        )

        self.knowledge_base = bedrock.CfnKnowledgeBase(self, "team49-knowledge-base",
            name="team49-3gpp-knowledge-base",
            role_arn=self.kb_role.role_arn,
            knowledge_base_configuration=bedrock.CfnKnowledgeBase.KnowledgeBaseConfigurationProperty(
                type="VECTOR",
                vector_knowledge_base_configuration=bedrock.CfnKnowledgeBase.VectorKnowledgeBaseConfigurationProperty(
                    embedding_model_arn=f"arn:aws:bedrock:{cdk.Aws.REGION}::foundation-model/amazon.titan-embed-text-v2:0",
                ),
            ),
            storage_configuration=bedrock.CfnKnowledgeBase.StorageConfigurationProperty(
                type="OPENSEARCH_SERVERLESS",
                opensearch_serverless_configuration=bedrock.CfnKnowledgeBase.OpenSearchServerlessConfigurationProperty(
                    collection_arn=self.collection.attr_arn,
                    vector_index_name="team49-kb-index",
                    field_mapping=bedrock.CfnKnowledgeBase.OpenSearchServerlessFieldMappingProperty(
                        vector_field="embedding",
                        text_field="text",
                        metadata_field="metadata",
                    ),
                ),
            ),
        )

        self.data_source = bedrock.CfnDataSource(self, "team49-data-source",
            knowledge_base_id=self.knowledge_base.attr_knowledge_base_id,
            name="team49-chunks-source",
            data_source_configuration=bedrock.CfnDataSource.DataSourceConfigurationProperty(
                type="S3",
                s3_configuration=bedrock.CfnDataSource.S3DataSourceConfigurationProperty(
                    bucket_arn=storage.chunks_bucket.bucket_arn,
                ),
            ),
            vector_ingestion_configuration=bedrock.CfnDataSource.VectorIngestionConfigurationProperty(
                chunking_configuration=bedrock.CfnDataSource.ChunkingConfigurationProperty(
                    chunking_strategy="NONE",
                ),
            ),
        )

        cdk.CfnOutput(self, "KnowledgeBaseId", value=self.knowledge_base.attr_knowledge_base_id)
        cdk.CfnOutput(self, "DataSourceId", value=self.data_source.attr_data_source_id)
