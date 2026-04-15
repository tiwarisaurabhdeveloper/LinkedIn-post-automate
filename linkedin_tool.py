from langchain.tools import tool
import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

# ACCESS_TOKEN = "AQV_379Kn91UJvlHgsqJX3187YXmDUTfk5iwYfU8TSyHCJjkLnSkOjZrZVdxG6yYvUIw_WjkMyuMcL_EZdGBTKdcDjY0n0417rb3pMPKgMDlDuTEvXkioeQGEhAp5Opt7Xp3YRDNY7vBk9_aTZzSFj5inBEGT_A7e_v5vwVy9q4nF4_5pMkPopEHqHa0f2O8LNwNjuMuBkbCfUYMpYEpMXHX95kaxrmGZth8L4MVXfdwcD7ziatQTJQYcK9290awGwhIdh6C3nesTioVApJ3mM9CYTXpgH8Wh0OKJXkdUp5ORIl0GGJ5DRkW48QisYEXpPDWezKji-9yT_rE1pBVTWHI4y6PNA"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

def linkedin_varification():
    try:
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        }

        response = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers)

        sub=response.json().get('sub')
        print(sub)
        # sub={'sub':"saurabh"}
        return sub
    except Exception as e:
        return "server is down right now"

# =========================

@tool
def linkedin_text_post(generated_post: str):
    "this tool take input Generated Post by given user Topic .call this tool with Generated Post"
    sub=linkedin_varification()
    if sub is not None:
        PERSON_URN = f"urn:li:person:{sub}"

        post_text = generated_post
        try:
            url = "https://api.linkedin.com/v2/ugcPosts"

            payload = {
                "author": PERSON_URN,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": post_text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            headers = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }

            response = requests.post(url, headers=headers, data=json.dumps(payload))

            Status_Code=response.status_code
            if Status_Code:
                print("Response:", response.text)
                return "your post is success fully posted"
            # return "your post is success fully posted automated"
        except Exception as e:
            return "server is not working right now"