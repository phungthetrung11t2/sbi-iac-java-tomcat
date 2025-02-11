from aws_cdk import (
    # Duration,
    Stack,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as actions,
    aws_codecommit as codecommit,
    aws_codebuild as codebuild,
    aws_iam as iam,
    aws_autoscaling as autoscaling,
    aws_codedeploy as codedeploy,
)
from constructs import Construct
import aws_cdk as cdk

class SbiPipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, config: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # Import GroupName information
        group_name = cdk.Fn.import_value("GroupName")
        # Import the AppName
        app_name = cdk.Fn.import_value("AppName")

        # Source repository
        repo = codecommit.Repository.from_repository_name(self, "Repo", "my-webapp")

        # Build Project for Application
        build_project = codebuild.PipelineProject(
            self, "BuildProject",
            build_spec=codebuild.BuildSpec.from_source_filename("config/buildspec_application.yml"),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.from_code_build_image_id(
                    "aws/codebuild/amazonlinux-x86_64-standard:5.0"
                ),
                compute_type=codebuild.ComputeType.SMALL
            )
        )

        # Application Deployment Pipeline
        pipeline = codepipeline.Pipeline(self, "ApplicationPipeline")
        source_stage = pipeline.add_stage(stage_name="Source")
        source_output = codepipeline.Artifact()
        source_stage.add_action(actions.CodeCommitSourceAction(
            action_name="CodeCommit_Source",
            repository=repo,
            branch="main",
            output=source_output
        ))

        # Build stage
        build_output = codepipeline.Artifact()

        build_stage = pipeline.add_stage(stage_name="Build")
        build_stage.add_action(actions.CodeBuildAction(
            action_name="CodeBuild",
            project=build_project,
            input=source_output,  # Use the named source artifact as input
            outputs=[build_output]  # Define the build output artifact
        ))

        # Manual Approval Stage
        manual_approval_action = actions.ManualApprovalAction(action_name="Approve")
        pipeline.add_stage(stage_name="Approval", actions=[manual_approval_action])
        
        # Deploy stage
        deploy_stage = pipeline.add_stage(stage_name="Deploy")
        deploy_stage.add_action(actions.CodeDeployServerDeployAction(
            action_name="CodeDeploy",
            input=build_output,
            deployment_group=codedeploy.ServerDeploymentGroup.from_server_deployment_group_attributes(
                self, "ImportedDeploymentGroup", application=codedeploy.ServerApplication.from_server_application_name(
                     self, "ImportedApplication", app_name
                    ),
                deployment_group_name=group_name)
        ))

