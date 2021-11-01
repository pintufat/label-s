"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import logging

from core.permissions import AllPermissions
from annotation_history.functions import bulk_annotation_history
from tasks.models import Prediction, Annotation

all_permissions = AllPermissions()
logger = logging.getLogger(__name__)


def predictions_to_annotations(project, queryset, **kwargs):
    request = kwargs['request']
    user = request.user
    model_version = request.data.get('model_version')
    queryset = queryset.filter(predictions__isnull=False)
    predictions = Prediction.objects.filter(task__in=queryset, child_annotations__isnull=True)

    # model version filter
    if model_version is not None:
        predictions = predictions.filter(model_version=model_version)

    predictions_values = list(predictions.values_list(
        'result', 'model_version', 'task_id', 'id'
    ))

    # prepare annotations
    annotations = []
    for result, model_version, task_id, prediction_id in predictions_values:
        annotations.append({
            'result': result,
            'completed_by_id': user.pk,
            'task_id': task_id,
            'parent_prediction_id': prediction_id
        })

    count = len(annotations)
    logger.debug(f'{count} predictions will be converter to annotations')
    db_annotations = [Annotation(**annotation) for annotation in annotations]
    db_annotations = Annotation.objects.bulk_create(db_annotations)

    return {'response_code': 200, 'detail': f'Created {count} annotations', 'db_annotations': db_annotations}


def predictions_to_annotations_form(user, project):
    versions = project.get_model_versions()

    # put the current model version on the top of the list
    first = project.model_version
    if first is not None:
        try:
            versions.remove(first)
        except ValueError:
            pass
        versions = [first] + versions

    return [{
        'columnCount': 1,
        'fields': [{
            'type': 'select',
            'name': 'model_version',
            'label': 'Choose a model',
            'options': versions,
        }]
    }]


actions = [
    {
        'entry_point': predictions_to_annotations,
        'permission': all_permissions.tasks_change,
        'title': 'Create Annotations From Predictions',
        'order': 91,
        'dialog': {
            'text': 'This action will create new annotations from predictions with the selected model version '
                    'for each selected task.',
            'type': 'confirm',
            'form': predictions_to_annotations_form,
        }
    }
]
