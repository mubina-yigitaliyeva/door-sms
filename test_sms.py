import os

from dotenv import load_dotenv
from solapi import SolapiMessageService
from solapi.model import RequestMessage

load_dotenv()


def test_sms():

    service = SolapiMessageService(
        api_key=os.environ["SOLAPI_API_KEY"],
        api_secret=os.environ["SOLAPI_API_SECRET"]
    )

    message = RequestMessage(
        from_=os.environ["SMS_SENDER"],
        to=os.environ["SMS_RECEIVER"],
        text="[DOOR-SMS] Your university notification system is working!"
    )

    response = service.send(message)

    print("Group ID:", response.group_info.group_id)

    print(
        "Accepted:",
        response.group_info.count.registered_success
    )

    print(
        "Failed:",
        response.group_info.count.registered_failed
    )


if __name__ == "__main__":

    confirm = input("Send one real SMS? (yes/no): ")

    if confirm.lower() == "yes":
        test_sms()