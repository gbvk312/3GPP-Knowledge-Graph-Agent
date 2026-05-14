import aws_cdk as cdk
from aws_cdk import (
    aws_apigatewayv2 as apigw,
    aws_apigatewayv2_integrations as integrations,
)
from constructs import Construct
from infra.stacks.agent import Team49AgentStack


class Team49ApiStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, agent: Team49AgentStack, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.http_api = apigw.HttpApi(self, "team49-http-api",
            api_name="team49-3gpp-api",
            cors_preflight=apigw.CorsPreflightOptions(
                allow_origins=["*"],
                allow_methods=[apigw.CorsHttpMethod.POST, apigw.CorsHttpMethod.GET],
                allow_headers=["Content-Type"],
            ),
        )

        self.http_api.add_routes(
            path="/ask",
            methods=[apigw.HttpMethod.POST],
            integration=integrations.HttpLambdaIntegration(
                "team49-agent-integration",
                handler=agent.invoker_fn,
            ),
        )

        self.api_url = self.http_api.url

        cdk.CfnOutput(self, "ApiUrl", value=self.http_api.url or "")
