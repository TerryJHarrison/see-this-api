### Deploying

```
sam build --use-container
sam package --s3-bucket deploy.harrison.enterprises --output-template-file ./packaged.yaml
sam deploy --template-file ./packaged.yaml --stack-name "see-this-api" --capabilities CAPABILITY_IAM
```