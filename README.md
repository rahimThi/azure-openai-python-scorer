# Company Scoring with Azure OpenAI (Python)

A small Python script that sends company descriptions to an LLM through the Azure OpenAI API and gets back a structured score.

It is the code version of the n8n workflow in my [AI-Assisted Lead Qualification Pipeline](https://github.com/rahimThi/ai-lead-qualification-pipeline): the same scoring rubric, written as a direct API call instead of a visual workflow.

## What it does

1. Reads companies from `data/companies_sample.csv` (fictional data)
2. Sends each company to the model with a scoring rubric
3. Forces a JSON answer (`response_format`) and checks that the score is between 1 and 5
4. Saves all results to `data/scores.csv`

## How to run

```
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env         # then fill in your Azure values
python score_companies.py
```

## Notes

- The API key is read from `.env`, which is excluded from Git.
- Temperature 0.2 keeps the scores consistent between runs.
- Failed calls are reported and skipped, so one error does not stop the run.

## Author

Md Abdur Rahim · [LinkedIn](https://linkedin.com/in/rahimthi)
