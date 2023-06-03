/**
 * 1- if user doesn't exist, throw exception
 * 2- if CUSTOM_CHALLENGE answer is correct, authentication successful
 * 3- if attempts with no correct answer, fail authentication
 * 4- default is to respond with CUSTOM_CHALLENGE --> password-less authentication
 * */

exports.handler = (event, context, callback) => {
    console.log(event);
    console.log(event.request.session);
    console.log(context);
    
    // If user is not registered
    if (event.request.userNotFound) {
        event.response.issueToken = false;
        event.response.failAuthentication = true;
        throw new Error("User does not exist");
    }
    
    if (event.request.session &&
        event.request.session.length &&
        event.request.session.slice(-1)[0].challengeName === 'CUSTOM_CHALLENGE' &&
        event.request.session.slice(-1)[0].challengeResult === true) {
        // The user provided the right answer; succeed auth
        event.response.issueTokens = true;
        event.response.failAuthentication = false;
        
    }else if(event.request.session.length >= 5 &&
        event.request.session.slice(-1)[0].challengeResult === false){
            
        event.response.issueToken = false;
        event.response.failAuthentication = true;
        throw new Error("Invalid credentials");
    }else{
        event.response.issueTokens = false;
        event.response.failAuthentication = false;
        event.response.challengeName = 'CUSTOM_CHALLENGE';
    }
    
    // Return to Amazon Cognito
    callback(null, event);
}
