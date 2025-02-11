#!/usr/bin/env python3
import os
import yaml

import aws_cdk as cdk

from sbi_iac_java_tomcat.sbi_iac_java_tomcat_stack import SbiIacJavaTomcatStack
from sbi_iac_java_tomcat.sbi_pipeline_stack import SbiPipelineStack
# from sbi_iac_java_tomcat.sbi_iac_pipeline_stack_dev import DevPipelineStack
# from sbi_iac_java_tomcat.sbi_iac_pipeline_stack_test import TestPipelineStack
# Load environment configurations
with open('./sbi_iac_java_tomcat/parameters.yaml', 'r') as file:
    config = yaml.safe_load(file)

app = cdk.App()

environment = app.node.try_get_context('env') or 'dev'
env_config = config.get(environment)

if not env_config:
    raise ValueError(f"Configuration for environment '{environment}' not found.")

# Create CDK Pipeline Stack for IaC management
SbiIacJavaTomcatStack(app, f"SbiIacJavaTomcatStack-{environment}", env_config, env=cdk.Environment(
        account=env_config["account_id"], region=env_config["region"]
    ))

# Create CDK Pipeline Stack for IaC management
SbiPipelineStack(app, f"PipelineStack-{environment}", env_config , env=cdk.Environment(
        account=env_config["account_id"], region=env_config["region"]
    ))

# # Create CDK Pipeline Stack for IaC management
# DevPipelineStack(app, f"DevPipelineStack", env_config , env=cdk.Environment(
#         account=env_config["account_id"], region=env_config["region"]
#     ))

# # Create CDK Pipeline Stack for IaC management
# TestPipelineStack(app, f"TestPipelineStack", env_config , env=cdk.Environment(
#         account=env_config["account_id"], region=env_config["region"]
#     ))

app.synth()
