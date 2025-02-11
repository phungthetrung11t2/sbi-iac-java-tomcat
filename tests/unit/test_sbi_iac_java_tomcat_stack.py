import aws_cdk as core
import aws_cdk.assertions as assertions

from sbi_iac_java_tomcat.sbi_iac_java_tomcat_stack import SbiIacJavaTomcatStack

# example tests. To run these tests, uncomment this file along with the example
# resource in sbi_iac_java_tomcat/sbi_iac_java_tomcat_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = SbiIacJavaTomcatStack(app, "sbi-iac-java-tomcat")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
