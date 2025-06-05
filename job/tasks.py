from celery import shared_task
from .models import Job
import openai
import os

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@shared_task
def process_job(event_id):
    job = Job.objects.get(event_id=event_id)
    job.status = "processing"
    job.save()

    try:
        summary_resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize the following text."},
                {"role": "user", "content": job.input_text},
            ],
        )
        summary = summary_resp.choices[0].message.content

        checklist_resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Generate a checklist from this summary.",
                },
                {"role": "user", "content": summary},
            ],
        )
        checklist = checklist_resp.choices[0].message.content

        job.status = "SUCCESS"
        job.result = {"summary": summary, "checklist": checklist}

    except Exception as e:
        job.status = "failed"
        job.result = {"error": str(e)}

    job.save()
