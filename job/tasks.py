import json
import logging
from celery import shared_task
from django.conf import settings
import openai
from .models import Job

logger = logging.getLogger(__name__)

@shared_task
def process_job(event_id):
    """Job을 처리하는 메인 태스크"""
    try:
        job = Job.objects.get(event_id=event_id)
        job.status = 'processing'
        job.save()
        
        # 다음 태스크 실행
        summarize_text.delay(str(event_id))
        return True
    except Job.DoesNotExist:
        logger.error(f"Job {event_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error processing job {event_id}: {str(e)}")
        job.status = 'failed'
        job.save()
        return False

@shared_task
def summarize_text(event_id):
    """텍스트를 요약하는 태스크"""
    try:
        job = Job.objects.get(event_id=event_id)
        
        # OpenAI API 호출
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text."},
                {"role": "user", "content": f"Please summarize the following text:\n\n{job.input_text}"}
            ]
        )
        
        summary = response.choices[0].message.content
        
        # 결과 저장
        job.result = {'summary': summary}
        job.status = 'summarized'
        job.save()
        
        # 다음 태스크 실행
        generate_checklist.delay(str(event_id))
        return True
    except Exception as e:
        logger.error(f"Error summarizing text for job {event_id}: {str(e)}")
        job.status = 'failed'
        job.save()
        return False

@shared_task
def generate_checklist(event_id):
    """요약된 텍스트를 기반으로 체크리스트를 생성하는 태스크"""
    try:
        job = Job.objects.get(event_id=event_id)
        
        if not job.result or 'summary' not in job.result:
            raise ValueError("No summary found for job")
        
        # OpenAI API 호출
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates checklists."},
                {"role": "user", "content": f"Based on this summary, create a checklist of important points:\n\n{job.result['summary']}"}
            ]
        )
        
        checklist_text = response.choices[0].message.content
        # JSON 형식의 문자열을 파싱
        try:
            checklist = json.loads(checklist_text)
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 줄바꿈으로 분리
            checklist = [item.strip() for item in checklist_text.split('\n') if item.strip()]
        
        # 결과 업데이트
        job.result['checklist'] = checklist
        job.status = 'completed'
        job.save()
        
        return True
    except Exception as e:
        logger.error(f"Error generating checklist for job {event_id}: {str(e)}")
        job.status = 'failed'
        job.save()
        return False
