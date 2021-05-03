# Feature toggle management using API Gateway WebSocket APIs

This repository contains a SAM application that uses Amazon API Gateway WebSocket APIs, AWS Lambda functions, and AWS DynamoDB streams to build a feature toggle management solution.  This solution allows you to store feature toggles in DynamoDB and automatically push notifications to connected clients when feature toggle states are changed.

For more information, refer to the [blog post](https://aws.amazon.com/blogs/devops/build-real-time-feature-toggles-with-amazon-dynamodb-streams-and-amazon-api-gateway-websocket-apis/) for this solution.

## Deploy

You can deploy this solution using the [SAM template](template.yaml) included in this repository.  

First, ensure you have the [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) installed. Then, you can deploy the SAM template using the following command from the application root.  This command will take you through a guided SAM deployment.

```
sam deploy --guided
```

## Test

To test this solution, you will need to insert some sample feature toggles into the "FeatureToggleTable" DynamoDB table.  Refer to the blog post for more details.

After you have test data in DynamoDB, you can use [wscat](https://github.com/websockets/wscat) to test the connection to your API Gateway endpoint.  Once you connect to your API Gateway endpoint, the current state of feature toggles should be automatically pushed to you.

```
$ wscat -c wss://{YOUR-API-ID}.execute-api.{YOUR-REGION}.amazonaws.com/{STAGE}
> { ... feature toggle info ... } 
```

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

