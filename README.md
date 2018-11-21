# Prerequisites
For this tutorial, you will:
Need an AWS Account (you can run this on the free tier)
Have the AWS CLI tool and Chalice installed and configured on your machine
A Nexmo account with the nexmo cli tool installed and configured
Have a Nexmo phone number purchased on your account

##Setup
Before we implement our functionality we need to do some setup, we need to create a new voice application either within the nexmo dashboard or using the command line tool”

` nexmo app:create “Paging Service” http://example.com/answer http://example.com/event --keyfile proivate.key`
Make a note of the application ID that is returned, this will also save the private key to a file.

For now we’ll use dummy values for the URLs or if you want to test locally you can use ngrok for your host.

We also need to create an S3 bucket in which to place the recordings for transcription, we can do this using the AWS CLI, we will be creating our resources in the us-east-1 AWS region.

` aws s3api create-bucket  --bucket pagingservice --region us-east-1`

##Download and configure

Clone the repository:

`git clone https://github.com/nexmo-community/paging-service-demo`

Copy the `private.key` file from the app you created earlier into the `challicelib` folder of the project (you can also remove the example key that is there)

Rename the `EXAMPLE_config.json` in `.chalice` to `config.json` 

Edit the value in the config.json


```
{
  "stages": {
    "dev": {
      "api_gateway_stage": "api",
      "environment_variables": {
              "APPLICATION_ID": "xxx"
              "API_KEY" : "xxx",
              "API_SECRET" : "xxx",
              "NAME" : "Joe Smith",
              "NUMBER" : "447700900123",
              "NEXMO_NUMBER" : "447700900456"
            }
    }
  },
  "version": "2.0",
  "app_name": "paging-service"
}
```
APPLICATION_ID is the id you were given when you created the nexmo app.
API_KEY is your Nexmo API Key
API_SECRET is your Nexmo API Secret
NAME is how you want callers to be greeted eg “Welcome to Joe Smith’s messaging service”
NUMBER is your mobile number where the SMS messages will be sent to 
NEXMO_NUMBER is the number that will be used to send the messages from.


##Deploy
From the base of the project folder type
` chalice deploy`

This will then create your lambda functions, setup API gateway and configure event triggers on the S3 bucket.

You should then get an output that contains a the API gateway URL eg:
`Rest API URL: https://3u9ucalu05.execute-api.us-east-1.amazonaws.com/api/`

Using this url as the base update your nexmo application to set the answer webhook to point to your deployed application, you will also need your application ID for this:
