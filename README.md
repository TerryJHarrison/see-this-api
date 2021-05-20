### Deploying

```
sam build --use-container
sam package --s3-bucket deploy.harrison.enterprises --output-template-file ./packaged.yaml
sam deploy --template-file ./packaged.yaml --stack-name "see-this-api" --capabilities CAPABILITY_IAM
```
- If there are updates to the ShortLinkRedirect function then publish a new version and deploy to CloudFront after deploying the stack