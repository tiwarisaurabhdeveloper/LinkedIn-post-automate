from langchain.tools import tool
import requests
import json
import os
from bs4 import BeautifulSoup
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
        print(response.json())
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
        

# ─────────────────────────────────────────
# NEW TOOL — LinkedIn Job Search
# ─────────────────────────────────────────

@tool
def linkedin_job_search(job_title: str, location: str, date_posted: str = "week", num_jobs: int = 10) -> str:
    """
    Search for jobs on LinkedIn based on job title and location.
    date_posted options: 'day', 'week', 'month'
    Returns formatted job listings with links.
    """

    time_filter = {
        "day": "r86400",
        "week": "r604800",
        "month": "r2592000"
    }.get(date_posted, "r604800")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }
    print("--=-==-=-=- this is the details --=-=-=-=",job_title,location,date_posted)
    jobs_list = []
    start = 0

    while len(jobs_list) < num_jobs:
        url = (
            f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            f"?keywords={requests.utils.quote(job_title)}"
            f"&location={requests.utils.quote(location)}"
            # f"&f_TPR={time_filter}"
            f"&f_TPR=r40400"
            f"&start={start}"
        )

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        job_cards = soup.find_all("li")

        if not job_cards:
            break

        for card in job_cards:
            try:
                title_tag = card.find("h3", class_="base-search-card__title")
                title = title_tag.get_text(strip=True) if title_tag else "N/A"

                company_tag = card.find("h4", class_="base-search-card__subtitle")
                company = company_tag.get_text(strip=True) if company_tag else "N/A"

                location_tag = card.find("span", class_="job-search-card__location")
                job_location = location_tag.get_text(strip=True) if location_tag else "N/A"

                date_tag = card.find("time")
                date = date_tag.get_text(strip=True) if date_tag else "N/A"

                link_tag = card.find("a", class_="base-card__full-link")
                link = link_tag["href"] if link_tag else "N/A"

                if title != "N/A":
                    jobs_list.append({
                        "title": title,
                        "company": company,
                        "location": job_location,
                        "date": date,
                        "link": link
                    })
            except Exception:
                continue

        start += 25
        # time.sleep(1.5)

    jobs_list = jobs_list[:num_jobs]

    # ── Format output as string for the agent ──
    if not jobs_list:
        return "❌ No jobs found. Try different title or location."

    output = f"✅ Found {len(jobs_list)} jobs for '{job_title}' in '{location}':\n\n"
    for i, job in enumerate(jobs_list, 1):
        output += (
            f"#{i}\n"
            f"💼 Title    : {job['title']}\n"
            f"🏢 Company  : {job['company']}\n"
            f"📍 Location : {job['location']}\n"
            f"📅 Posted   : {job['date']}\n"
            f"🔗 Link     : {job['link']}\n"
            f"{'─'*50}\n"
        )
    return {
        "type": "jobs",           # <-- key flag for the frontend
        "jobs": jobs_list         # list of {title, company, location, date, link}
    }

    # return output