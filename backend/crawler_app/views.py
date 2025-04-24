from django.shortcuts import render, redirect
from django.http import HttpResponse
from crawler_app.models import CrawlTask, BusinessData
from sqlalchemy.orm import sessionmaker
# from .forms import CrawlTaskForm
from django.core.files.storage import FileSystemStorage
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import os
import subprocess

def index(request):
    tasks = CrawlTask.objects.all().order_by('-created_at')  # Lấy dữ liệu để hiển thị trong bảng
    return render(request, 'crawler_app/index.html', {'tasks': tasks}) 
def view(request):
    return render(request, 'crawler_app/view.html')

def create_task(request):
    if request.method == 'POST':
        url_filter = request.POST.get('url_filter')  # Lấy giá trị từ form
        if url_filter:
            # Lưu dữ liệu vào bảng CrawlTask
            CrawlTask.objects.create(url_filter=url_filter)
            #create_and_run_task(url_filter)
            return redirect('home')  # Sau khi tạo task xong, redirect về trang chính
    return render(request, 'crawler_app/index.html')  # Nếu không phải POST, render lại trang

from crawl_runner import create_and_run_task

def action_task(request, task_id):
    if request.method == 'GET':
        task = CrawlTask.objects.get(id=task_id)
        create_and_run_task(task_id, task.url_filter)
        return redirect('home')
    return render(request, 'crawler_app/index.html')
