import logging
import traceback
import time

from django.db import transaction

from projects.models import ProjectImport, ProjectReimport
from .serializers import ImportApiSerializer
from .uploader import load_tasks_for_async_import
from users.models import User
from core.utils.common import load_func
from django.conf import settings
from webhooks.utils import emit_webhooks_for_instance
from webhooks.models import WebhookAction
from .models import FileUpload

logger = logging.getLogger(__name__)


def async_import_background(import_id, user_id, **kwargs):  # type: ignore[no-untyped-def]
    with transaction.atomic():
        try:
            project_import = ProjectImport.objects.get(id=import_id)
        except ProjectImport.DoesNotExist:
            logger.error(f'ProjectImport with id {import_id} not found, import processing failed')
            return
        if project_import.status != ProjectImport.Status.CREATED:
            logger.error(f'Processing import with id {import_id} already started')
            return
        project_import.status = ProjectImport.Status.IN_PROGRESS
        project_import.save(update_fields=['status'])

    user = User.objects.get(id=user_id)

    start = time.time()
    project = project_import.project
    tasks = None
    # upload files from request, and parse all tasks
    # TODO: Stop passing request to load_tasks function, make all validation before
    tasks, file_upload_ids, found_formats, data_columns = load_tasks_for_async_import(project_import, user)  # type: ignore[no-untyped-call]

    if project_import.preannotated_from_fields:
        # turn flat task JSONs {"column1": value, "column2": value} into {"data": {"column1"..}, "predictions": [{..."column2"}]  # noqa
        tasks = reformat_predictions(tasks, project_import.preannotated_from_fields)  # type: ignore[no-untyped-call]

    if project_import.commit_to_project:
        # Immediately create project tasks and update project states and counters
        serializer = ImportApiSerializer(data=tasks, many=True, context={'project': project})
        serializer.is_valid(raise_exception=True)
        tasks = serializer.save(project_id=project.id)  # type: ignore[union-attr]
        emit_webhooks_for_instance(user.active_organization, project, WebhookAction.TASKS_CREATED, tasks)  # type: ignore[no-untyped-call]

        task_count = len(tasks)
        annotation_count = len(serializer.db_annotations)
        prediction_count = len(serializer.db_predictions)
        # Update counters (like total_annotations) for new tasks and after bulk update tasks stats. It should be a
        # single operation as counters affect bulk is_labeled update
        project.update_tasks_counters_and_task_states(tasks_queryset=tasks, maximum_annotations_changed=False,  # type: ignore[union-attr]
                                                      overlap_cohort_percentage_changed=False,
                                                      tasks_number_changed=True)
        logger.info('Tasks bulk_update finished')

        project.summary.update_data_columns(tasks)  # type: ignore[union-attr]
        # TODO: project.summary.update_created_annotations_and_labels
    else:
        # Do nothing - just output file upload ids for further use
        task_count = len(tasks)
        annotation_count = None
        prediction_count = None

    duration = time.time() - start

    project_import.task_count = task_count or 0
    project_import.annotation_count = annotation_count or 0
    project_import.prediction_count = prediction_count or 0
    project_import.duration = duration
    project_import.file_upload_ids = file_upload_ids
    project_import.found_formats = found_formats
    project_import.data_columns = data_columns
    if project_import.return_task_ids:
        project_import.task_ids = [task.id for task in tasks]

    project_import.status = ProjectImport.Status.COMPLETED
    project_import.save()



def set_import_background_failure(job, connection, type, value, _):  # type: ignore[no-untyped-def]
    import_id = job.args[0]
    ProjectImport.objects.filter(id=import_id).update(
        status=ProjectImport.Status.FAILED,
        traceback=traceback.format_exc(),
        error=str(value)
    )


def set_reimport_background_failure(job, connection, type, value, _):  # type: ignore[no-untyped-def]
    reimport_id = job.args[0]
    ProjectReimport.objects.filter(id=reimport_id).update(
        status=ProjectReimport.Status.FAILED,
        traceback=traceback.format_exc(),
        error=str(value),
    )


def reformat_predictions(tasks, preannotated_from_fields):  # type: ignore[no-untyped-def]
    new_tasks = []
    for task in tasks:
        if 'data' in task:
            task = task['data']
        predictions = [{'result': task.pop(field)} for field in preannotated_from_fields]
        new_tasks.append({
            'data': task,
            'predictions': predictions
        })
    return new_tasks

post_process_reimport = load_func(settings.POST_PROCESS_REIMPORT)  # type: ignore[no-untyped-call]


def async_reimport_background(reimport_id, organization_id, user, **kwargs):  # type: ignore[no-untyped-def]

    with transaction.atomic():
        try:
            reimport = ProjectReimport.objects.get(id=reimport_id)
        except ProjectReimport.DoesNotExist:
            logger.error(f'ProjectReimport with id {reimport_id} not found, import processing failed')
            return
        if reimport.status != ProjectReimport.Status.CREATED:
            logger.error(f'Processing reimport with id {reimport_id} already started')
            return
        reimport.status = ProjectReimport.Status.IN_PROGRESS
        reimport.save(update_fields=['status'])

    project = reimport.project

    tasks, found_formats, data_columns = FileUpload.load_tasks_from_uploaded_files(  # type: ignore[no-untyped-call]
        reimport.project, reimport.file_upload_ids,  files_as_tasks_list=reimport.files_as_tasks_list)

    with transaction.atomic():
        project.remove_tasks_by_file_uploads(reimport.file_upload_ids)  # type: ignore[union-attr]
        serializer = ImportApiSerializer(data=tasks, many=True, context={'project': project, 'user': user})
        serializer.is_valid(raise_exception=True)
        tasks = serializer.save(project_id=project.id)  # type: ignore[union-attr]
        emit_webhooks_for_instance(organization_id, project, WebhookAction.TASKS_CREATED, tasks)  # type: ignore[no-untyped-call]

    # Update counters (like total_annotations) for new tasks and after bulk update tasks stats. It should be a
    # single operation as counters affect bulk is_labeled update
    project.update_tasks_counters_and_task_states(  # type: ignore[union-attr]
        tasks_queryset=tasks, maximum_annotations_changed=False,
        overlap_cohort_percentage_changed=False,
        tasks_number_changed=True)
    logger.info('Tasks bulk_update finished')

    project.summary.update_data_columns(tasks)  # type: ignore[union-attr]
    # TODO: project.summary.update_created_annotations_and_labels

    reimport.task_count = len(tasks)
    reimport.annotation_count = len(serializer.db_annotations)
    reimport.prediction_count = len(serializer.db_predictions)
    reimport.found_formats = found_formats
    reimport.data_columns = list(data_columns)
    reimport.status = ProjectReimport.Status.COMPLETED
    reimport.save()

    post_process_reimport(reimport)
