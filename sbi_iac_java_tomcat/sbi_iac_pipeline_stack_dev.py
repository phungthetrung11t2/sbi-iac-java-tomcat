from aws_cdk import (
    Stack,
    aws_codecommit as codecommit,
    aws_codepipeline as codepipeline,
    aws_codebuild as codebuild,
    aws_codepipeline_actions as actions,
)
from constructs import Construct

class DevPipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Repository
        repo = codecommit.Repository(self, "Repo", repository_name=config["repository_name"])

        # Build Project
        build_project = codebuild.PipelineProject(
            self, "DevBuildProject",
            build_spec=codebuild.BuildSpec.from_source_filename("config/buildspec_cdk.yml"),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.from_code_build_image_id(
                    "aws/codebuild/amazonlinux-x86_64-standard:5.0"
                ),
                compute_type=codebuild.ComputeType.SMALL
            )
        )

        # Build Project
        build_project_deploy = codebuild.PipelineProject(
            self, "DevBuildDeployProject",
            build_spec=codebuild.BuildSpec.from_source_filename("config/buildspec_cdk_deploy.yml"),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.from_code_build_image_id(
                    "aws/codebuild/amazonlinux-x86_64-standard:5.0"
                ),
                compute_type=codebuild.ComputeType.SMALL
            )
        )

        # Pipeline
        pipeline = codepipeline.Pipeline(self, "Pipeline",)

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

        # # Deploy Stage
        # deploy_action = actions.CloudFormationCreateUpdateStackAction(
        #     action_name="Deploy",
        #     stack_name=config["stack_name"],
        #     template_path=build_output.at_path("cdk.out/PipelineStack-dev.template.json"),
        #     admin_permissions=True
        # )

        # Add CodeBuildAction to the pipeline
        deploy_action = actions.CodeBuildAction(
            action_name="Deploy",
            project=build_project_deploy,
            input=build_output,
            environment_variables={
                "ENVIRONMENT": codebuild.BuildEnvironmentVariable(
                    value=config["environment_name"]  # Set to "dev", "test", or "prod" based on your requirement
                )
            }   
        )
        pipeline.add_stage(stage_name="Deploy", actions=[deploy_action])

