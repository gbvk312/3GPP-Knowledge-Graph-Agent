import aws_cdk as cdk
from aws_cdk import (
    aws_cloudwatch as cw,
)
from constructs import Construct
from infra.stacks.pipeline import Team49PipelineStack
from infra.stacks.api import Team49ApiStack


class Team49ObservabilityStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, pipeline: Team49PipelineStack,
                 api: Team49ApiStack, **kwargs):
        super().__init__(scope, id, **kwargs)

        sfn_failures = cw.Alarm(self, "team49-sfn-failures",
            alarm_name="team49-pipeline-failures",
            metric=pipeline.state_machine.metric_failed(),
            threshold=1,
            evaluation_periods=1,
            comparison_operator=cw.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
        )

        api_5xx = cw.Alarm(self, "team49-api-5xx",
            alarm_name="team49-api-5xx-errors",
            metric=cw.Metric(
                namespace="AWS/ApiGateway",
                metric_name="5xx",
                dimensions_map={"ApiId": api.http_api.http_api_id},
                statistic="Sum",
                period=cdk.Duration.minutes(5),
            ),
            threshold=5,
            evaluation_periods=1,
            comparison_operator=cw.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
        )

        cw.Dashboard(self, "team49-dashboard",
            dashboard_name="team49-knowledge-graph-dashboard",
            widgets=[
                [
                    cw.GraphWidget(
                        title="Pipeline Executions",
                        left=[
                            pipeline.state_machine.metric_started(),
                            pipeline.state_machine.metric_succeeded(),
                            pipeline.state_machine.metric_failed(),
                        ],
                    ),
                    cw.GraphWidget(
                        title="API Errors",
                        left=[cw.Metric(
                            namespace="AWS/ApiGateway",
                            metric_name="5xx",
                            dimensions_map={"ApiId": api.http_api.http_api_id},
                            statistic="Sum",
                            period=cdk.Duration.minutes(1),
                        )],
                    ),
                ],
            ],
        )
