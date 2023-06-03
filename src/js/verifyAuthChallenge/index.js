const crypto = require("crypto");

exports.handler = async (event) => {
    console.log(event);
   
   //--------get private challenge data
    const challenge = event.request.privateChallengeParameters.challenge;
    const credId = event.request.privateChallengeParameters.credId;
    
    //--------public key information
    const publicKeyCred = event.request.userAttributes["custom:publicKeyCred"];
    const publicKeyCredJSON = JSON.parse(Buffer.from(publicKeyCred, 'base64').toString('ascii'));
    
    //-------get challenge answer
    const challengeAnswerJSON = JSON.parse(event.request.challengeAnswer);
    
    const verificationResult = await validateAssertionSignature(publicKeyCredJSON, challengeAnswerJSON);
    console.log("Verification Results:"+verificationResult);
    
    event.response.answerCorrect = !!verificationResult;
    return event;
};

async function validateAssertionSignature(publicKeyCredJSON, challengeAnswerJSON) {
    const expectedSignature = toArrayBuffer(challengeAnswerJSON.response.signature, "signature");
    const publicKey = publicKeyCredJSON.publicKey;
    const rawAuthnrData = toArrayBuffer(challengeAnswerJSON.response.authenticatorData, "authenticatorData");
    const rawClientData = toArrayBuffer(challengeAnswerJSON.response.clientDataJSON, "clientDataJSON");

    const hash = crypto.createHash("SHA256");
    hash.update(Buffer.from(new Uint8Array(rawClientData)));
    const clientDataHashBuf = hash.digest();
    const clientDataHash = new Uint8Array(clientDataHashBuf).buffer;

    const verify = crypto.createVerify("SHA256");
    verify.write(Buffer.from(new Uint8Array(rawAuthnrData)));
    verify.write(Buffer.from(new Uint8Array(clientDataHash)));
    verify.end();

    let res = null;
    try {
        res = verify.verify(publicKey, Buffer.from(new Uint8Array(expectedSignature)));
    } catch (e) {console.error(e);}
    return res;
}

function toArrayBuffer(buf, name) {
    if (!name) {
        throw new TypeError("name not specified");
    }

    if (typeof buf === "string") {
        buf = buf.replace(/-/g, "+").replace(/_/g, "/");
        buf = Buffer.from(buf, "base64");
    }

    if (buf instanceof Buffer || Array.isArray(buf)) {
        buf = new Uint8Array(buf);
    }

    if (buf instanceof Uint8Array) {
        buf = buf.buffer;
    }

    if (!(buf instanceof ArrayBuffer)) {
        throw new TypeError(`could not convert '${name}' to ArrayBuffer`);
    }

    return buf;
}
