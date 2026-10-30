"""
Score companies with Azure OpenAI.

Reads a CSV of companies, sends each one to an LLM with a scoring rubric,
gets a structured JSON answer back, and saves all results to a new CSV.

Run:  python score_companies.py
"""

import csv
import json
import os
import time

from dotenv import load_dotenv
from openai import AzureOpenAI

# 1. Settings: read from the .env file (never hard-code your API key)
load_dotenv()
client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21"),
)
DEPLOYMENT = os.environ["AZURE_OPENAI_DEPLOYMENT"]  # e.g. gpt-4.1-mini

INPUT_FILE = "data/companies_sample.csv"
OUTPUT_FILE = "data/scores.csv"

# 2. The prompt: same rubric as the n8n project, shortened
SYSTEM_PROMPT = """You are a business development analyst at a consulting firm
that helps mid-sized German companies digitalise their operations.

Ideal customer: 100 to 2,000 employees; logistics, manufacturing, metal
processing, food production, wholesale or automotive supply; low digital
maturity; and a current trigger (growth, new site, new management,
customer or regulatory pressure).

Scoring: 5 = strong fit, 4 = good fit, 3 = possible fit,
2 = weak fit, 1 = no fit (already digital, too small or too large,
insolvency, sale, or project freeze). Without a current trigger, the
score is at most 3.

Answer only with JSON in this format:
{"fit_score": <1-5>, "digital_maturity": "low|medium|high",
 "key_signal": "<max 20 words>", "reason": "<one or two sentences>"}"""


def score_company(company: dict) -> dict:
    """Send one company to the LLM and return its JSON answer as a dict."""
    user_prompt = (
        f"Name: {company['company_name']}\n"
        f"Industry: {company['industry']}\n"
        f"Employees: {company['employees']}\n"
        f"Description: {company['description']}"
    )
    response = client.chat.completions.create(
        model=DEPLOYMENT,
        temperature=0.2,
        response_format={"type": "json_object"},  # forces valid JSON
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    return json.loads(response.choices[0].message.content)


def main():
    # 3. Read the companies
    with open(INPUT_FILE, encoding="utf-8") as f:
        companies = list(csv.DictReader(f))
    print(f"Loaded {len(companies)} companies")

    # 4. Score each one, with a simple check and error handling
    results = []
    for company in companies:
        try:
            answer = score_company(company)
            score = int(answer["fit_score"])
            if not 1 <= score <= 5:
                raise ValueError(f"score out of range: {score}")
            results.append({
                "company_id": company["company_id"],
                "company_name": company["company_name"],
                "fit_score": score,
                "digital_maturity": answer["digital_maturity"],
                "key_signal": answer["key_signal"],
                "reason": answer["reason"],
            })
            print(f"{company['company_name']}: {score}")
        except Exception as error:
            print(f"{company['company_name']}: FAILED ({error})")
        time.sleep(1)  # small pause to stay within rate limits

    # 5. Save the results
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"Saved {len(results)} of {len(companies)} results to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
