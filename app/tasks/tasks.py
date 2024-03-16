from datetime import timedelta

from app.celery import celery, loop
from app.db.base import async_session
from app.services.upload_menu import UploadMenu


@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        timedelta(seconds=15),  # Запуск каждые 15 секунд
        my_first_task.s(),
        name='my first task',
    )


@celery.task()
def my_first_task():
    async def task_my_first_task():
        async with async_session() as db:
            upload_menu = UploadMenu(db=db)
            await upload_menu.run()
    loop.run_until_complete(task_my_first_task())


# @celery.task()
# def my_first_task():
#     async def task_my_first_task():
#         print("Celery task is running ...")
#     loop.run_until_complete(task_my_first_task())