import aws_cdk as cdk
from aws_cdk import (
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_bedrock as bedrock,
    Duration,
)
from constructs import Construct
from infra.stacks.storage import Team49StorageStack
from infra.stacks.graph import Team49GraphStack
from infra.stacks.knowledge import Team49KnowledgeStack

AGENT_INSTRUCTION = """You are a 3GPP standards expert assistant. When answering:
1. ALWAYS call vector_search first to retrieve relevant specification chunks.
2. Call graph_search to expand the relationship neighborhood for visual rendering.
3. Call metadata_query for exact structured attribute lookups (spec, release, section).
4. Call whitepaper_lookup for vendor deployment context and explanations.
Return a JSON response with keys: summary (string), nodes (array), edges (array), citations (array of {spec, release, section, text})."""


class Team49AgentStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, storage: Team49StorageStack,
                 graph: Team49GraphStack, knowledge: Team49KnowledgeStack, **kwargs):
        super().__init__(scope, id, **kwargs)

        common_env = {
            "NEPTUNE_ENDPOINT": graph.cluster.attr_endpoint,
            "CHUNKS_TABLE": storage.chunks_table.table_name,
            "FEATURES_TABLE": storage.features_table.table_name,
            "KB_ID": knowledge.knowledge_base.attr_knowledge_base_id,
        }

        def make_tool_lambda(name: str, path: str, vpc=None, sg=None) -> _lambda.Function:
            fn = _lambda.Function(self, name,
                function_name=name,
                runtime=_lambda.Runtime.PYTHON_3_12,
                handler="handler.lambda_handler",
                code=_lambda.Code.from_asset(path),
                timeout=Duration.seconds(30),
                memory_size=256,
                environment=common_env,
                vpc=vpc,
                security_groups=[sg] if sg else None,
            )
            return fn

        vector_search_fn = make_tool_lambda("team49-vector-search", "lambdas/agent_tools/vector_search")
        vector_search_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["bedrock:Retrieve"],
            resources=[f"arn:aws:bedrock:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:knowledge-base/*"],
        ))

        graph_search_fn = make_tool_lambda("team49-graph-search", "lambdas/agent_tools/graph_search",
                                           vpc=graph.vpc, sg=graph.lambda_sg)

        metadata_query_fn = make_tool_lambda("team49-metadata-query", "lambdas/agent_tools/metadata_query")
        storage.chunks_table.grant_read_data(metadata_query_fn)
        storage.features_table.grant_read_data(metadata_query_fn)

        whitepaper_lookup_fn = make_tool_lambda("team49-whitepaper-lookup", "lambdas/agent_tools/whitepaper_lookup")
        whitepaper_lookup_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["bedrock:Retrieve"],
            resources=[f"arn:aws:bedrock:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:knowledge-base/*"],
        ))

        # Agent role
        agent_role = iam.Role(self, "team49-agent-role",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
            inline_policies={
                "bedrock-model": iam.PolicyDocument(statements=[
                    iam.PolicyStatement(
                        actions=["bedrock:InvokeModel"],
                        resources=[f"arn:aws:bedrock:{cdk.Aws.REGION}::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"],
                    ),
                ]),
                "lambda-invoke": iam.PolicyDocument(statements=[
                    iam.PolicyStatement(
                        actions=["lambda:InvokeFunction"],
                        resources=[
                            vector_search_fn.function_arn,
                            graph_search_fn.function_arn,
                            metadata_query_fn.function_arn,
                            whitepaper_lookup_fn.function_arn,
                        ],
                    ),
                ]),
            },
        )

        self.agent = bedrock.CfnAgent(self, "team49-agent",
            agent_name="team49-3gpp-agent",
            agent_resource_role_arn=agent_role.role_arn,
            foundation_model="anthropic.claude-3-5-sonnet-20241022-v2:0",
            instruction=AGENT_INSTRUCTION,
            action_groups=[
                bedrock.CfnAgent.AgentActionGroupProperty(
                    action_group_name="vector_search",
                    action_group_executor=bedrock.CfnAgent.ActionGroupExecutorProperty(
                        lambda_=vector_search_fn.function_arn,
                    ),
                    api_schema=bedrock.CfnAgent.APISchemaProperty(
                        payload=open("schemas/vector_search.yaml").read(),
                    ),
                ),
                bedrock.CfnAgent.AgentActionGroupProperty(
                    action_group_name="graph_search",
                    action_group_executor=bedrock.CfnAgent.ActionGroupExecutorProperty(
                        lambda_=graph_search_fn.function_arn,
                    ),
                    api_schema=bedrock.CfnAgent.APISchemaProperty(
                        payload=open("schemas/graph_search.yaml").read(),
                    ),
                ),
                bedrock.CfnAgent.AgentActionGroupProperty(
                    action_group_name="metadata_query",
                    action_group_executor=bedrock.CfnAgent.ActionGroupExecutorProperty(
                        lambda_=metadata_query_fn.function_arn,
                    ),
                    api_schema=bedrock.CfnAgent.APISchemaProperty(
                        payload=open("schemas/metadata_query.yaml").read(),
                    ),
                ),
                bedrock.CfnAgent.AgentActionGroupProperty(
                    action_group_name="whitepaper_lookup",
                    action_group_executor=bedrock.CfnAgent.ActionGroupExecutorProperty(
                        lambda_=whitepaper_lookup_fn.function_arn,
                    ),
                    api_schema=bedrock.CfnAgent.APISchemaProperty(
                        payload=open("schemas/whitepaper_lookup.yaml").read(),
                    ),
                ),
            ],
        )

        # Agent invoker Lambda (for API Gateway)
        self.invoker_fn = _lambda.Function(self, "team49-agent-invoker",
            function_name="team49-agent-invoker",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambdas/agent_tools/agent_invoker"),
            timeout=Duration.seconds(60),
            memory_size=256,
            environment={
                "AGENT_ID": self.agent.attr_agent_id,
                "AGENT_ALIAS_ID": "TSTALIASID",
            },
        )
        self.invoker_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["bedrock:InvokeAgent"],
            resources=[f"arn:aws:bedrock:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:agent-alias/*"],
        ))

        cdk.CfnOutput(self, "AgentId", value=self.agent.attr_agent_id)
