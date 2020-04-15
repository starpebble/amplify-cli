# streaming_lambda_bonsai

This lambda fork replicates DynamoDB events to ElasticSearch hosted on Bonsai.

The project's [app.py](streaming_lambda/app.py) file is the Lambda's entry point.  The lambda's app.py is a fork
of amplify-cli's [python_streaming_function.py](../streaming-lambda/python_streaming_function.py)
function. The main tree's lambda limits DynamoDB event replication to ElasticSearch hosted on AWS.

This Serverless Application Model (SAM) project contains exactly one
lambda that executes on the AWS Lambda Python3.8 engine.  

## Lambda environment variables

Set environment variables in the SAM CloudFormation template [template.yaml](template.yaml) before use.

* BONSAI_ENDPOINT

The bonsai host and the port.  Available on the Bonsai console.

* BONSAI_ACCESS_KEY

The access key from the Bonsai cluster credentials

* BONSAI_ACCESS_SECRET

The access secret from the Bonsai cluster credentials

* DEBUG

Log level.  Toggles the Lambda's CloudWatch logs verbosity.

```yaml
      Environment:
        Variables: 
          BONSAI_ENDPOINT : "example-7409635573.us-east-1.bonsaisearch.net:443"
          BONSAI_ACCESS_KEY : 6hyzRskSbw
          BONSAI_ACCESS_SECRET : ecvp3JrKTQonS4h
          DEBUG : 0
```

## Kibana Commands

Run these commands in the Kibana console.  The commands administrate the 
index 'todo' on the ElasticSearch cluster.  The Bonsai console provides 
exactly one Kibana dashboard for each Bonsai cluster.



```
# Create the 'todo' index with Kibana
PUT /todo

# Post two rows to the _bulk API
POST /_bulk
{"index": {"_index": "todo", "_type": "doc", "_id": "123"}}
{"createdAt": "2020-04-08T02:54:22.130Z", "__typename": "Todo", "name": "SocialFlats", "description": "This is searchable", "id": "123", "updatedAt": "2020-04-08T02:55:07.530Z"}

# Search all documents on the cluster
GET _search
{
  "query": {
    "match_all": {}
  }
}
```

## Local testing commands

Prerequisite: modify the environment variable values in [template.yaml](template.yaml)

Shell commands to build and test the lambda locally:
```shell
sam build
sam local invoke StreamingLambdaFunction --event events/event.json
```
## Deployment Tree

`sam build` generates a build directory in a hidden directory named .aws-sam. 
Here are the contents of the Lambda's build directory.

```
├── StreamingLambdaFunction
│   ├── app.py
│   ├── certifi
│   │   ├── cacert.pem
│   │   ├── core.py
│   │   ├── __init__.py
│   │   └── __main__.py
│   ├── certifi-2020.4.5.1.dist-info
│   │   ├── LICENSE
│   │   ├── METADATA
│   │   ├── RECORD
│   │   ├── top_level.txt
│   │   └── WHEEL
│   ├── chardet
│   │   ├── big5freq.py
│   │   ├── big5prober.py
│   │   ├── chardistribution.py
│   │   ├── charsetgroupprober.py
│   │   ├── charsetprober.py
│   │   ├── cli
│   │   │   ├── chardetect.py
│   │   │   └── __init__.py
│   │   ├── codingstatemachine.py
│   │   ├── compat.py
│   │   ├── cp949prober.py
│   │   ├── enums.py
│   │   ├── escprober.py
│   │   ├── escsm.py
│   │   ├── eucjpprober.py
│   │   ├── euckrfreq.py
│   │   ├── euckrprober.py
│   │   ├── euctwfreq.py
│   │   ├── euctwprober.py
│   │   ├── gb2312freq.py
│   │   ├── gb2312prober.py
│   │   ├── hebrewprober.py
│   │   ├── __init__.py
│   │   ├── jisfreq.py
│   │   ├── jpcntx.py
│   │   ├── langbulgarianmodel.py
│   │   ├── langcyrillicmodel.py
│   │   ├── langgreekmodel.py
│   │   ├── langhebrewmodel.py
│   │   ├── langhungarianmodel.py
│   │   ├── langthaimodel.py
│   │   ├── langturkishmodel.py
│   │   ├── latin1prober.py
│   │   ├── mbcharsetprober.py
│   │   ├── mbcsgroupprober.py
│   │   ├── mbcssm.py
│   │   ├── sbcharsetprober.py
│   │   ├── sbcsgroupprober.py
│   │   ├── sjisprober.py
│   │   ├── universaldetector.py
│   │   ├── utf8prober.py
│   │   └── version.py
│   ├── chardet-3.0.4.dist-info
│   │   ├── DESCRIPTION.rst
│   │   ├── entry_points.txt
│   │   ├── METADATA
│   │   ├── metadata.json
│   │   ├── RECORD
│   │   ├── top_level.txt
│   │   └── WHEEL
│   ├── idna
│   │   ├── codec.py
│   │   ├── compat.py
│   │   ├── core.py
│   │   ├── idnadata.py
│   │   ├── __init__.py
│   │   ├── intranges.py
│   │   ├── package_data.py
│   │   └── uts46data.py
│   ├── idna-2.9.dist-info
│   │   ├── LICENSE.rst
│   │   ├── METADATA
│   │   ├── RECORD
│   │   ├── top_level.txt
│   │   └── WHEEL
│   ├── __init__.py
│   ├── requests
│   │   ├── adapters.py
│   │   ├── api.py
│   │   ├── auth.py
│   │   ├── certs.py
│   │   ├── compat.py
│   │   ├── cookies.py
│   │   ├── exceptions.py
│   │   ├── help.py
│   │   ├── hooks.py
│   │   ├── __init__.py
│   │   ├── _internal_utils.py
│   │   ├── models.py
│   │   ├── packages.py
│   │   ├── sessions.py
│   │   ├── status_codes.py
│   │   ├── structures.py
│   │   ├── utils.py
│   │   └── __version__.py
│   ├── requests-2.23.0.dist-info
│   │   ├── LICENSE
│   │   ├── METADATA
│   │   ├── RECORD
│   │   ├── top_level.txt
│   │   └── WHEEL
│   ├── requirements.txt
│   ├── urllib3
│   │   ├── _collections.py
│   │   ├── connectionpool.py
│   │   ├── connection.py
│   │   ├── contrib
│   │   │   ├── _appengine_environ.py
│   │   │   ├── appengine.py
│   │   │   ├── __init__.py
│   │   │   ├── ntlmpool.py
│   │   │   ├── pyopenssl.py
│   │   │   ├── _securetransport
│   │   │   │   ├── bindings.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── low_level.py
│   │   │   ├── securetransport.py
│   │   │   └── socks.py
│   │   ├── exceptions.py
│   │   ├── fields.py
│   │   ├── filepost.py
│   │   ├── __init__.py
│   │   ├── packages
│   │   │   ├── backports
│   │   │   │   ├── __init__.py
│   │   │   │   └── makefile.py
│   │   │   ├── __init__.py
│   │   │   ├── six.py
│   │   │   └── ssl_match_hostname
│   │   │       ├── _implementation.py
│   │   │       └── __init__.py
│   │   ├── poolmanager.py
│   │   ├── request.py
│   │   ├── response.py
│   │   └── util
│   │       ├── connection.py
│   │       ├── __init__.py
│   │       ├── queue.py
│   │       ├── request.py
│   │       ├── response.py
│   │       ├── retry.py
│   │       ├── ssl_.py
│   │       ├── timeout.py
│   │       ├── url.py
│   │       └── wait.py
│   └── urllib3-1.25.8.dist-info
│       ├── LICENSE.txt
│       ├── METADATA
│       ├── RECORD
│       ├── top_level.txt
│       └── WHEEL
└── template.yaml
```

## Files

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI. It includes the following files and folders.

- streaming_lambda - The Lambda function's python code.
- events - An invocation event that you can use to invoke the function.
- template.yaml - A template that defines the application's AWS resources.

The application uses several AWS resources, including Lambda functions and an API Gateway API. These resources are defined in the `template.yaml` file in this project. You can update the template to add AWS resources through the same deployment process that updates your application code.

If you prefer to use an integrated development environment (IDE) to build and test your application, you can use the AWS Toolkit.  
The AWS Toolkit is an open source plug-in for popular IDEs that uses the SAM CLI to build and deploy serverless applications on AWS. The AWS Toolkit also adds a simplified step-through debugging experience for Lambda function code. See the following links to get started.

* [PyCharm](https://docs.aws.amazon.com/toolkit-for-jetbrains/latest/userguide/welcome.html)
* [IntelliJ](https://docs.aws.amazon.com/toolkit-for-jetbrains/latest/userguide/welcome.html)
* [VS Code](https://docs.aws.amazon.com/toolkit-for-vscode/latest/userguide/welcome.html)
* [Visual Studio](https://docs.aws.amazon.com/toolkit-for-visual-studio/latest/user-guide/welcome.html)

## Deploy the sample application

The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon Linux environment that matches Lambda. It can also emulate your application's build environment and API.

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3 installed](https://www.python.org/downloads/)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build --use-container
sam deploy --guided
```

The first command will build the source of your application. The second command will package and deploy your application to AWS, with a series of prompts:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modified IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

You can find your API Gateway Endpoint URL in the output values displayed after deployment.

## Use the SAM CLI to build and test locally

Build your application with the `sam build --use-container` command.

```bash
streaming-lambda$ sam build --use-container
```

The SAM CLI installs dependencies defined in `streaming_lambda/requirements.txt`, creates a deployment package, and saves it in the `.aws-sam/build` folder.

Test a single function by invoking it directly with a test event. An event is a JSON document that represents the input that the function receives from the event source. Test events are included in the `events` folder in this project.

Run functions locally and invoke them with the `sam local invoke` command.

```bash
streaming-lambda$ sam local invoke StreamingLambdaFunction --event events/event.json
```

The event.json file contains a single DynamoDB item to insert into 
an index named 'todo' on the Bonsai cluster.

## Add a resource to your application
The application template uses AWS Serverless Application Model (AWS SAM) to define application resources. AWS SAM is an extension of AWS CloudFormation with a simpler syntax for configuring common serverless application resources such as functions, triggers, and APIs. For resources not included in [the SAM specification](https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md), you can use standard [AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html) resource types.

## Fetch, tail, and filter Lambda function logs

To simplify troubleshooting, SAM CLI has a command called `sam logs`. `sam logs` lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several nifty features to help you quickly find the bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```bash
streaming-lambda$ sam logs -n StreamingLambdaFunction --stack-name streaming-lambda --tail
```

You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name streaming-lambda
```

## Resources

Bonsai is an ElasticSearch host. [https://app.bonsai.io/](https://app.bonsai.io/)

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)

Install Python3.8, `sam build` requires Python3.8.

Install Docker,  `sam invoke` requires Docker.
