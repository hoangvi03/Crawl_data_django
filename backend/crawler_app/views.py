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
import sys

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

import threading
import logging
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def run_task_in_background(task_id, url_filter):
    logger.info(f"Starting task {task_id} in background...")

    try:
        # Lấy đường dẫn tuyệt đối của script crawl_runner.py
        script_path = os.path.abspath("crawl_runner.py")
        
        # Sử dụng sys.executable để lấy Python trong môi trường ảo
        python_path = sys.executable  # Đây sẽ là Python trong môi trường ảo
        
        # In ra thông tin về môi trường ảo và script đang chạy
        logger.info(f"Python executable: {python_path}")
        logger.info(f"Running script: {script_path}")

        # Chạy subprocess với Python trong môi trường ảo và gọi hàm create_and_run_task trong script
        process = subprocess.Popen([python_path, script_path, str(task_id), url_filter], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Đọc kết quả từ subprocess
        stdout, stderr = process.communicate()

        # Kiểm tra và in ra output
        if stdout:
            logger.info(f"Output: {stdout.decode()}")
        if stderr:
            logger.error(f"Error: {stderr.decode()}")

        logger.info(f"Task {task_id} started.")
    except Exception as e:
        logger.error(f"Error running subprocess: {e}")


def action_task(request, task_id):
    if request.method == 'GET':
        task = CrawlTask.objects.get(id=task_id)
        # Khởi chạy task trong background bằng thread
        threading.Thread(target=run_task_in_background, args=(task_id, task.url_filter)).start()
        return redirect('home')
    return render(request, 'crawler_app/index.html')