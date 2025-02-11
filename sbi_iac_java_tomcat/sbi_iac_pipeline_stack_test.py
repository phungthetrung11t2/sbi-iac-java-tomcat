from aws_cdk import (
    Stack,
    aws_codecommit as codecommit,
    aws_codepipeline as codepipeline,
    aws_codebuild as codebuild,
    aws_codepipeline_actions as actions,
    CfnOutput
)
from constructs import Construct


class TestPipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Repository
        repo = codecommit.Repository(self, "Repo", repository_name=config["repository_name"])

        # Define a CodeBuild project
        build_project = codebuild.PipelineProject(self, "TestBuildProject")

        # Create the pipeline
        pipeline = codepipeline.Pipeline(self, "TestPipeline")

        # Source Stage
        source_output = codepipeline.Artifact()
        source_action = actions.CodeCommitSourceAction(
            action_name="Source",
            repository=repo,
            branch=config["branch_name"],
            output=source_output
        )
        pipeline.add_stage(stage_name="Source", actions=[source_action])

        # Build Stage
        build_output = codepipeline.Artifact()
        build_action = actions.CodeBuildAction(
            action_name="Build",
            project=build_project,
            input=source_output,
            outputs=[build_output]
        )
        pipeline.add_stage(stage_name="Build", actions=[build_action])

        # Manual Approval Stage
        manual_approval_action = actions.ManualApprovalAction(action_name="Approve")
        pipeline.add_stage(stage_name="Approval", actions=[manual_approval_action])

        # Deploy Stage
        deploy_action = actions.CloudFormationCreateUpdateStackAction(
            action_name="Deploy",
            stack_name="TestCDKStack",
            template_path=build_output.at_path("template.json"),
            admin_permissions=True
        )
        pipeline.add_stage(stage_name="Deploy", actions=[deploy_action])

        # Outputs for tracking
        CfnOutput(self, "PipelineName", value=pipeline.pipeline_name, export_name="PipelineName")
