# MailJet SMS application

This application takes in CSV file with a list of clients, each with at least a 'number' and 'text' field, then sends the corresponding text message to all clients using the MailJet SMS API.

The application will then print the number of successful and unsuccessful sends, and output a CSV file containing any rows that were unsuccessfully sent with its correpsonding error message.

## Setup

Create a .env file in the local directory with the following fields, replacing the token with the correct MailJet API token, and the sender field:

```
MAILJET_TOKEN="MY_MAILJET_TOKEN"
SENDER_NAME="MailJet SMS"
INPUT_FILE="in.csv"
OUTPUT_FILE="out.csv"
```

## Sending SMS

Once the input csv file and environment variables are setup, run:

```
python main.py
```

## Input CSV file

The input CSV file might have the following format:

```
name,state,number,text
CLIENT_NAME,STATE,0466666666,TEXT_MESSAGE
CLIENT_NAME,STATE,0466666666,TEXT_MESSAGE
CLIENT_NAME,STATE,0466666666,TEXT_MESSAGE
```

Although the 'name' and 'state' fields are not important, the data set must have fields for 'number' and 'text'. Note that the input CSV file must not have fields with the same header name, or information will be lost in the output file.

## Output CSV file

With the example input CSV file, the output CSV file should have the following format for any text messages that failed to send:

```
name,state,number,text,errorMessage
CLIENT_NAME,STATE,0466666666,TEXT_MESSAGE,ERROR_MESSAGE
CLIENT_NAME,STATE,0466666666,TEXT_MESSAGE,ERROR_MESSAGE
CLIENT_NAME,STATE,0466666666,TEXT_MESSAGE,ERROR_MESSAGE
```


