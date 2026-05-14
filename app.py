#!/usr/bin/env python3
import aws_cdk as cdk
from infra.stacks.storage import Team49StorageStack
from infra.stacks.knowledge import Team49KnowledgeStack
from infra.stacks.graph import Team49GraphStack
from infra.stacks.pipeline import Team49PipelineStack
from infra.stacks.agent import Team49AgentStack
from infra.stacks.api import Team49ApiStack
from infra.stacks.observability import Team49ObservabilityStack

app = cdk.App()

storage = Team49StorageStack(app, "Team49StorageStack")
knowledge = Team49KnowledgeStack(app, "Team49KnowledgeStack", storage=storage)
graph = Team49GraphStack(app, "Team49GraphStack")
pipeline = Team49PipelineStack(app, "Team49PipelineStack", storage=storage, graph=graph, knowledge=knowledge)
agent = Team49AgentStack(app, "Team49AgentStack", storage=storage, graph=graph, knowledge=knowledge)
api = Team49ApiStack(app, "Team49ApiStack", agent=agent)
observability = Team49ObservabilityStack(app, "Team49ObservabilityStack", pipeline=pipeline, api=api)

app.synth()
