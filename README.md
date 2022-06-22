# Emergency messaging application

This application takes in CSV file with the client name, state, mobile number, and text message, then sends the corresponding text message to all clients.

The application will then print the number of successful and unsuccessful sends, and output a CSV file containing any rows that were unsuccessfully sent with its correpsonding error message.

## Setup

Create a .env file in the local directory with the following fields, replacing the token with the correct MailJet API token:

```
MJ_TOKEN=MY_MAILJET_TOKEN
INPUT_NAME=in.csv
OUTPUT_NAME=out.csv
```

## Input CSV file

The output CSV file should have the following format:

```
name,state,number,text
CLIENT_NAME,STATE,0466666666,TEXT_MESSAGE
CLIENT_NAME,STATE,0466666666,TEXT_MESSAGE
CLIENT_NAME,STATE,0466666666,TEXT_MESSAGE
```

## Output CSV file

The output CSV file should have the following format:

```
name,state,number,text,errorMessage
CLIENT_NAME,STATE,0466666666,TEXT_MESSAGE,ERROR_MESSAGE
CLIENT_NAME,STATE,0466666666,TEXT_MESSAGE,ERROR_MESSAGE
CLIENT_NAME,STATE,0466666666,TEXT_MESSAGE,ERROR_MESSAGE
```


