
# Welcome to your CDK Python project!

This is a blank project for CDK development with Python.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!

## Deploy multiple environment

 * `cdk deploy --context env=dev`   
 * `cdk deploy --context env=test`  
 * `cdk deploy --context env=prod`  

 * `cdk list --context env=dev`   
 * `cdk list --context env=test`  
 * `cdk list --context env=prod`  

 * `cdk diff --context env=dev`   
 * `cdk diff --context env=test`  
 * `cdk diff --context env=prod`  

## Deploy pipeline 
 * `cdk deploy PipelineStack-dev`

## Verify security with cdk-nag

To check security of your cdk code 
```
from cdk_nag import AwsSolutionsChecks
cdk.Aspects.of(app).add(AwsSolutionsChecks())
```