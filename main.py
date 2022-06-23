import csv
import json
import os
from dotenv import load_dotenv
from typing import Any, Dict, List, Tuple

import requests
import phonenumbers
import concurrent.futures


class Client:
    def __init__(self, fields: Dict[str, str]):
        self.fields = fields

    def postSMS(self, token: str, sender: str) -> Dict[str, Any]:
        """Sends an sms from a client dictionary object using using MailJet with the input token.

        Args:
            token (str): Token string
            client (Dict[str, Any]): Client dictionary object with "number" and "text" fields

        Returns:
            Dict[str, Any]: "error" boolean field, "errorMessage" string field, and the original "fields" dictionary
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
                "Text": self.fields["text"],
                "To": Client.parseToE164(self.fields["number"]),
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

        return {"error": error, "errorMessage": errorMessage, "client": self.fields}

    @staticmethod
    def parseToE164(number: str) -> str:
        """Parses a phone number string to comply with the E.164 international telephone numbering standard.

        Args:
            number (str): Input phone number string

        Returns:
            str: Phone number in E.164 numbering standard
        """

        x = phonenumbers.parse(number, "AU")
        return phonenumbers.format_number(x, phonenumbers.PhoneNumberFormat.E164)


class ClientCollection:
    instance = None

    @staticmethod
    def getInstance():
        """Gets the current instance of ClientCollection if it doesn't currently exist"""
        if not ClientCollection.instance:
            ClientCollection.instance = ClientCollection()
        return ClientCollection.instance

    def __init__(self):
        """Constructor for the ClientCollection class. This method will store environment variables and load all clients."""
        load_dotenv()

        self.MAILJET_TOKEN = os.getenv("MAILJET_TOKEN")
        self.SENDER_NAME = os.getenv("SENDER_NAME")
        self.INPUT_FILE = os.getenv("INPUT_FILE")
        self.OUTPUT_FILE = os.getenv("OUTPUT_FILE")

        self.loadClients()

    def loadClients(self):
        """Regenerates all Client objects from a list of dictionaries."""

        # Get headers and data from CSV file
        self.headers, dataRows = self.readCSV()

        self.clientList: List[Client] = []
        for dataRow in dataRows:
            self.clientList += [Client(dataRow)]

    def readCSV(self) -> Tuple[List[str], List[Dict[str, str]]]:
        """Reads a csv file from the INPUT_FILE field and converts it into a list of dictionaries.

        Returns:
            Tuple[List[str], List[Dict[str, str]]]: List of CSV headers and row data as dictionaries
        """

        dataRows = []
        with open(self.INPUT_FILE, mode="r") as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)
            for row in reader:
                dataRow = {}
                for i, header in enumerate(headers):
                    try:
                        dataRow[header] = row[i]
                    except:
                        dataRow[header] = ""
                dataRows += [dataRow]

        return headers, dataRows

    def postAllSMS(self):
        """Runs the postSMS method for all clients in ClientCollections,
        then prints out the number of successes and failures, and writes out all failed SMS posts to a CSV file.
        """
        out = []
        success = 0
        failure = 0

        # https://stackoverflow.com/questions/2632520/what-is-the-fastest-way-to-send-100-000-http-requests-in-python
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            # Create collection of futures
            fs = (
                executor.submit(client.postSMS, self.MAILJET_TOKEN, self.SENDER_NAME)
                for client in self.clientList
            )

            # Iterate through futures
            for f in concurrent.futures.as_completed(fs):
                clientDict = f.result()["client"]

                # If the request failed
                if f.result()["error"]:
                    failure += 1
                    clientDict["errorMessage"] = f.result()["errorMessage"]
                    out += [clientDict]
                else:
                    success += 1

        print(f"Successes: {success}, Failures: {failure}")
        self.writeCSV(out)

    def writeCSV(self, data: List[Dict[str, Any]]):
        """Outputs a list of same dictionary items to a CSV file designated by the OUTPUT_FILE field.
        This will not work properly for dictionary items that don't all have the same keys.

        Args:
            data (List[Dict[str, Any]]): List of dictionaries
        """

        with open(self.OUTPUT_FILE, "w", encoding="utf8", newline="") as out:
            dw = csv.DictWriter(out, self.headers + ["errorMessage"])
            dw.writeheader()
            dw.writerows(data)


if __name__ == "__main__":
    cc = ClientCollection.getInstance()
    cc.loadClients()
    cc.postAllSMS()
