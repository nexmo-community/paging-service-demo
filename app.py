from chalice import Chalice
import boto3
import nexmo
import os
import json

APPLICATION_ID = os.environ['APPLICATION_ID']
API_KEY = os.environ['API_KEY']
API_SECRET = os.environ['API_SECRET']
NAME = os.environ['NAME']
NUMBER = os.environ['NUMBER']
NEXMO_NUMBER = os.environ['NEXMO_NUMBER']
S3_BUCKET = 'pagingdemo'


app = Chalice(app_name='paging-service')
app.debug=False

S3 = boto3.client('s3')
TRANSCRIBE = boto3.client('transcribe')
NEXMO = nexmo.Client(
    key=API_KEY,
    secret=API_SECRET,
    application_id=APPLICATION_ID,
    private_key='chalicelib/private.key',
)

@app.route('/answer')
def answer():
    req = app.current_request.to_dict()
    ncco =[
            {
                'action': 'talk',
                'text': "Welcome to {} messaging service, please leave a short message after the tone".format(NAME),
            },
            {
                'action': 'record',
                'endOnSilence': 3,
                'endOnKey': '#',
                'beepStart' : True,
                'eventUrl' : [req['headers']['x-forwarded-proto'] + "://" + req['headers']['host'] + "/api/recording?from=" +req['query_params']['from']]
            },
            {
                'action': 'talk',
                'text': "thankyou, your message has been forwarded"
            }
        ]
    return ncco



@app.route('/recording', methods=['POST'])
def recording():
  qparams=  app.current_request.query_params
  data =  app.current_request.json_body
  recfile = NEXMO.get_recording(data['recording_url'])  
  S3.put_object(
      Bucket=S3_BUCKET,
      Key=data['conversation_uuid']+".mp3",
      Body=recfile,
      ContentType='audio/mp3',
      Metadata={
        'callerid': qparams['from'],
        'time' : data['end_time']
      }
  )
  response = TRANSCRIBE.start_transcription_job(
      TranscriptionJobName=data['conversation_uuid'],
      LanguageCode='en-GB',
      MediaFormat='mp3',
      Media={
          'MediaFileUri': 'https://s3.amazonaws.com/{}/{}'.format(S3_BUCKET, data['conversation_uuid']+".mp3") 
      },
      OutputBucketName=S3_BUCKET,
  )
  return "ok"



@app.on_s3_event(bucket=S3_BUCKET, events=['s3:ObjectCreated:*'], suffix='.json')
def transcribed(event):
  obj = S3.get_object( Bucket=S3_BUCKET, Key=event.key)
  data = json.loads(obj['Body'].read())
  S3.put_object_acl(ACL='public-read', Bucket=S3_BUCKET, Key= data['jobName']+".mp3")
  text = data['results']['transcripts'][0]['transcript'].upper()
  obj = S3.get_object( Bucket=S3_BUCKET, Key=data['jobName']+".mp3")
  callerid = obj['ResponseMetadata']['HTTPHeaders']['x-amz-meta-callerid']
  url = 'https://s3.amazonaws.com/{}/{}'.format(S3_BUCKET, data['jobName']+".mp3")
  message = "[From: +{}]\n\n{}\n\n{}".format(callerid, text, url)
  NEXMO.send_message({'from': NEXMO_NUMBER, 'to': NUMBER, 'text': message})
    
            


  
