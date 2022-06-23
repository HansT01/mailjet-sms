import csv
import json
import os
from dotenv import load_dotenv
from typing import Any, Dict, List, Tuple

import requests
import phonenumbers
import concurrent.futures


def readCSV(fileName: str) -> Tuple[List[str], List[Dict[str, str]]]:
    """Reads a csv file from a given filePath and converts it into a List of Dictionaries.

    Args:
        filePath (str): Path to csv file to be read

    Returns:
        Tuple[List[str], List[Dict[str, str]]]: List of CSV headers and row data as dictionaries
    """

    result = []
    with open(fileName, mode="r") as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)
        for row in reader:
            rowdata = {}
            for i, header in enumerate(headers):
                try:
                    rowdata[header] = row[i]
                except:
                    rowdata[header] = ""
            result += [rowdata]
    return (headers, result)


def postSMS(token: str, client: Dict[str, Any], sender: str) -> Dict[str, Any]:
    """Sends an sms from a client dictionary object using using MailJet with the input token.

    Args:
        token (str): Token string
        client (Dict[str, Any]): Client dictionary object with "number" and "text" fields

    Returns:
        Dict[str, Any]: "error" boolean field, "errorMessage" string field, and the original "client" dictionary
    """

    # Based off of the API documentation on
    # https://dev.mailjet.com/sms/guides/send-sms-api/

    error = False
    errorMessage = ""

    try:
        url = "https://api.mailjet.com/v4/sms-send"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-type": "application/json",
        }
        body = {
            "Text": client["text"],
            "To": parseToE164(client["number"]),
            "From": sender,
        }

        x = requests.post(url, json=body, headers=headers, timeout=5)
        res = json.loads(x.text)

        # TODO this condition should be changed to actually reflect a failing response
        if "StatusCode" in res:
            raise Exception(res["ErrorMessage"])
    except Exception as e:
        error = True
        errorMessage = str(e)

    return {"error": error, "errorMessage": errorMessage, "client": client}


def parseToE164(number: str) -> str:
    """Parses a phone number string to comply with the E.164 international telephone numbering standard.

    Args:
        number (str): Input phone number string

    Returns:
        str: Phone number in E.164 numbering standard
    """

    x = phonenumbers.parse(number, "AU")
    return phonenumbers.format_number(x, phonenumbers.PhoneNumberFormat.E164)


def listToCSV(data: List[Dict[str, Any]], headers: List[str], fileName: str):
    """Outputs a list of same dictionary items to a CSV file.
    This will not work properly for dictionary items that don't all have the same keys.

    Args:
        data (List[Dict[str, Any]]): List of dictionaries
        headers (List[str]): Headers for the dictionaries
        fileName (str): Name of the output file
    """

    with open(fileName, "w", encoding="utf8", newline="") as out:
        dw = csv.DictWriter(out, headers)
        dw.writeheader()
        dw.writerows(data)


def main():
    load_dotenv()

    MAILJET_TOKEN = os.getenv("MAILJET_TOKEN")
    SENDER_NAME = os.getenv("SENDER_NAME")
    INPUT_FILE = os.getenv("INPUT_FILE")
    OUTPUT_FILE = os.getenv("OUTPUT_FILE")

    headers, clients = readCSV(INPUT_FILE)

    out = []
    success = 0
    failure = 0

    # https://stackoverflow.com/questions/2632520/what-is-the-fastest-way-to-send-100-000-http-requests-in-python
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        # Create collection of futures
        fs = (
            executor.submit(postSMS, MAILJET_TOKEN, client, SENDER_NAME)
            for client in clients
        )

        # Iterate through futures
        for f in concurrent.futures.as_completed(fs):
            client = f.result()["client"]

            # If the request failed
            if f.result()["error"]:
                failure += 1
                client["errorMessage"] = f.result()["errorMessage"]
                out += [client]
            else:
                success += 1

    print(f"Successes: {success}, Failures: {failure}")

    # Add headers error column
    headers += ["errorMessage"]
    listToCSV(out, headers, OUTPUT_FILE)


if __name__ == "__main__":
    main()
