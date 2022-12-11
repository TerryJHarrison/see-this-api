### Deploying
- Committing to the `main` branch will automatically deploy changes using AWS SAM.
- If there are updates to the ShortLinkRedirect function then publish a new version and deploy to CloudFront after deploying the stack

### Documentation
- Open API specifications are hosted on [GitHub Pages](https://terryjharrison.github.io/see-this-api/)
- Run the doc site locally from the `docs` directory with `bundle exec jekyll serve`

#### Setup
Running locally currently requires a few steps to work properly:
- Update the `docs/swagger-ui/swagger-initializer.js` file - set `isLocal = true` on line 6
- Run `git update-index --assume-unchanged docs/swagger-ui/swagger-initializer.js` from the project root directory
- If you need to push updates to this file then undo **both** of these changes