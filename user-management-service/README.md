<!--
title: 'Serverless Framework Python Flask API on AWS'
description: 'This template demonstrates how to develop and deploy a simple Python Flask API running on AWS Lambda using the traditional Serverless Framework.'
layout: Doc
framework: v3
platform: AWS
language: Python
priority: 2
authorLink: 'https://github.com/serverless'
authorName: 'Serverless, inc.'
authorAvatar: 'https://avatars1.githubusercontent.com/u/13742415?s=200&v=4'
-->

# Serverless Framework Python Flask API on AWS

This template demonstrates how to develop and deploy a simple Python Flask API service running on AWS Lambda using the traditional Serverless Framework.


## Anatomy of the template

This template configures a single function, `api`, which is responsible for handling all incoming requests thanks to configured `httpApi` events. To learn more about `httpApi` event configuration options, please refer to [httpApi event docs](https://www.serverless.com/framework/docs/providers/aws/events/http-api/). As the events are configured in a way to accept all incoming requests, `Flask` framework is responsible for routing and handling requests internally. The implementation takes advantage of `serverless-wsgi`, which allows you to wrap WSGI applications such as Flask apps. To learn more about `serverless-wsgi`, please refer to corresponding [GitHub repository](https://github.com/logandk/serverless-wsgi). Additionally, the template relies on `serverless-python-requirements` plugin for packaging dependencies from `requirements.txt` file. For more details about `serverless-python-requirements` configuration, please refer to corresponding [GitHub repository](https://github.com/UnitedIncome/serverless-python-requirements).

## Usage

### Prerequisites

In order to package your dependencies locally with `serverless-python-requirements`, you need to have `Python3.9` installed locally. You can create and activate a dedicated virtual environment with the following command:

```bash
python3.9 -m venv ./venv
source ./venv/bin/activate
```

Alternatively, you can also use `dockerizePip` configuration from `serverless-python-requirements`. For details on that, please refer to corresponding [GitHub repository](https://github.com/UnitedIncome/serverless-python-requirements).

### Deployment

This example is made to work with the Serverless Framework dashboard, which includes advanced features such as CI/CD, monitoring, metrics, etc.

In order to deploy with dashboard, you need to first login with:

```
serverless login
```

install dependencies with:

```
npm install
```

and

```
pip install -r requirements.txt
```

and then perform deployment with:

```
serverless deploy
```

After running deploy, you should see output similar to:

```bash
Deploying aws-python-flask-api-project to stage dev (us-east-1)

✔ Service deployed to stack aws-python-flask-api-project-dev (182s)

endpoint: ANY - https://xxxxxxxx.execute-api.us-east-1.amazonaws.com
functions:
  api: aws-python-flask-api-project-dev-api (1.5 MB)
```

