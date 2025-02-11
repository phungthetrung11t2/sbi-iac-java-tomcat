import os
from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_elasticloadbalancingv2 as elbv2,
    aws_iam as iam,
    aws_codedeploy as codedeploy,
    CfnOutput
)
from constructs import Construct

class SbiIacJavaTomcatStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, config: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        instance_type = config["instance_type"]
        min_instance_count = config["min_instance_count"]
        max_instance_count = config["max_instance_count"]
        vpc_id = config["vpc_id"]
        sg_id = config["sg_id"]
        iam_role_arn = config["iam_role_arn"]
        public_subnet_ids = config["public_subnet_ids"]

        # Load user data from external file
        with open("./sbi_iac_java_tomcat/tomcat_setup.sh", "r") as file:
            user_data_script = file.read()

        # # Load user data from external file
        # script_path = "./sbi_iac_java_tomcat/tomcat_setup.sh"
        # if not os.path.exists(script_path):
        #     raise FileNotFoundError(f"User data script '{script_path}' not found.")

        # Existing VPC
        # vpc = ec2.Vpc.from_lookup(self, "Vpc", is_default=True)
        vpc = ec2.Vpc.from_vpc_attributes(self, "Vpc", vpc_id=vpc_id, availability_zones=["ap-southeast-1a", "ap-southeast-1b"])

        # Security Group
        sg = ec2.SecurityGroup.from_security_group_id(self, "SG", sg_id)

        # IAM Role
        instance_role = iam.Role.from_role_arn(self, "InstanceRole", iam_role_arn)

        # Autoscaling Group
        asg = autoscaling.AutoScalingGroup(
            self, "ASG",
            vpc=vpc,
            instance_type=ec2.InstanceType(instance_type),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            security_group=sg,
            role=instance_role,
            min_capacity=min_instance_count,
            max_capacity=max_instance_count,
            vpc_subnets=ec2.SubnetSelection(subnets=[
                ec2.Subnet.from_subnet_id(self, "DefaultSubnet1" ,public_subnet_ids[0]),
                ec2.Subnet.from_subnet_id(self, "DefaultSubnet2" ,public_subnet_ids[1])
            ])
        )
        asg.add_user_data(user_data_script)
        # Add tag to instances launched by the ASG
        asg.node.default_child.add_property_override(
            "Tags",
            [
                {
                    "Key": "Environment",
                    "Value": "Production",
                    "PropagateAtLaunch": True
                }
            ]
        )
        # Elastic Load Balancer
        lb = elbv2.ApplicationLoadBalancer(
            self, "ALB",
            vpc=vpc,
            internet_facing=True,
            vpc_subnets=ec2.SubnetSelection(subnets=[
                ec2.Subnet.from_subnet_id(self, "PublicSubnet1", public_subnet_ids[0]),
                ec2.Subnet.from_subnet_id(self, "PublicSubnet2", public_subnet_ids[1])
            ]) 
        )
        listener = lb.add_listener("Listener", port=80)
        # listener.add_targets("ApplicationTarget", port=8080, targets=[asg])

         # Target Groups for Blue-Green
        blue_target_group = listener.add_targets(
            "BlueTargetGroup",
            port=8080,
            targets=[asg],
            health_check={"path": "/"}
        )
        # green_target_group = elbv2.ApplicationTargetGroup(
        #     self, "GreenTargetGroup",
        #     port=8080,
        #     vpc=vpc,
        #     health_check={"path": "/"}
        # )

        # IAM Role for CodeDeploy
        codedeploy_role = iam.Role(
            self, "CodeDeployRole",
            assumed_by=iam.ServicePrincipal("codedeploy.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSCodeDeployRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
            ]
        )
        # Deployment Group for Blue-Green Deployments
        # codedeploy.ServerDeploymentGroup(
        #     self, "DeploymentGroup",
        #     deployment_group_name=f"ASGDeployment-{config['environment_name']}",
        #     auto_scaling_groups=[asg],
        #     deployment_config=codedeploy.ServerDeploymentConfig.ALL_AT_ONCE
        # )

        codedeploy_app = codedeploy.ServerApplication(self, "CodeDeployApplication")
        deployment_group = codedeploy.ServerDeploymentGroup(
            self, "DeploymentGroup1",
            deployment_group_name=f"ASGDeployment1-{config['environment_name']}",
            application=codedeploy_app,
            auto_scaling_groups=[asg],
            install_agent=True,
            deployment_config=codedeploy.ServerDeploymentConfig.ALL_AT_ONCE,
            ec2_instance_tags=codedeploy.InstanceTagSet(
                {"Environment": ["Production"]}
            ),
            role=codedeploy_role,
            load_balancers=[
                codedeploy.LoadBalancer.application(blue_target_group)
            ],
            # blue_green_deployment_configuration=codedeploy.CfnDeploymentGroup.BlueGreenDeploymentConfigurationProperty(
            #     deployment_ready_option=codedeploy.CfnDeploymentGroup.DeploymentReadyOptionProperty(
            #         action_on_timeout="CONTINUE_DEPLOYMENT",  # Options: "CONTINUE_DEPLOYMENT" or "STOP_DEPLOYMENT"
            #         wait_time_in_minutes=0
            #     ),
            #     green_fleet_provisioning_option=codedeploy.CfnDeploymentGroup.GreenFleetProvisioningOptionProperty(
            #         action="COPY_AUTO_SCALING_GROUP"  # Options: "DISCOVER_EXISTING" or "COPY_AUTO_SCALING_GROUP"
            #     ),
            #     terminate_blue_instances_on_deployment_success=codedeploy.CfnDeploymentGroup.BlueInstanceTerminationOptionProperty(
            #         action="TERMINATE",  # Options: "TERMINATE" or "KEEP_ALIVE"
            #         termination_wait_time_in_minutes=5
            #     )
            # )
        )
        deployment_group.node.default_child.cfn_options.metadata = {
            "aws:cdk:cloudformation:props": {
                "ignoreChanges": ["AutoScalingGroups"]
            }
        }
        # Use CloudFormation `CfnDeploymentGroup` to configure Blue/Green settings
        CfnOutput(self, "GroupName", value=deployment_group.deployment_group_name,export_name="GroupName")
        # CfnOutput(self, "AppName1", value=codedeploy_app.application_name,export_name="AppName1")
        # CfnOutput(self, "GroupName", value=deployment_group.deployment_group_name,export_name="GroupName")
        CfnOutput(self, "AppName", value=codedeploy_app.application_name,export_name="AppName")
