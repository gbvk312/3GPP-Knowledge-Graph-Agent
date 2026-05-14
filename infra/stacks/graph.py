import aws_cdk as cdk
from aws_cdk import (
    aws_ec2 as ec2,
    aws_neptune as neptune,
)
from constructs import Construct


class Team49GraphStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.vpc = ec2.Vpc(self, "team49-vpc",
            max_azs=2,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="team49-private",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24,
                ),
            ],
        )

        self.neptune_sg = ec2.SecurityGroup(self, "team49-neptune-sg",
            vpc=self.vpc,
            description="Neptune Serverless security group",
            allow_all_outbound=False,
        )
        self.neptune_sg.add_ingress_rule(
            ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
            ec2.Port.tcp(8182),
            "Allow Neptune access from VPC",
        )

        self.lambda_sg = ec2.SecurityGroup(self, "team49-lambda-sg",
            vpc=self.vpc,
            description="Lambda security group for Neptune access",
            allow_all_outbound=True,
        )

        self.vpc.add_interface_endpoint("team49-neptune-endpoint",
            service=ec2.InterfaceVpcEndpointAwsService("neptune-db"),
            security_groups=[self.neptune_sg],
        )

        subnet_group = neptune.CfnDBSubnetGroup(self, "team49-neptune-subnet-group",
            db_subnet_group_description="Neptune subnet group",
            subnet_ids=[s.subnet_id for s in self.vpc.isolated_subnets],
            db_subnet_group_name="team49-neptune-subnet-group",
        )

        self.cluster = neptune.CfnDBCluster(self, "team49-neptune-cluster",
            db_cluster_identifier="team49-neptune-cluster",
            engine_version="1.3.1.0",
            serverless_scaling_configuration=neptune.CfnDBCluster.ServerlessScalingConfigurationProperty(
                min_capacity=1.0,
                max_capacity=8.0,
            ),
            db_subnet_group_name=subnet_group.db_subnet_group_name,
            vpc_security_group_ids=[self.neptune_sg.security_group_id],
            storage_encrypted=True,
        )
        self.cluster.add_dependency(subnet_group)

        self.neptune_endpoint = self.cluster.attr_endpoint

        cdk.CfnOutput(self, "NeptuneEndpoint", value=self.cluster.attr_endpoint)
        cdk.CfnOutput(self, "VpcId", value=self.vpc.vpc_id)
