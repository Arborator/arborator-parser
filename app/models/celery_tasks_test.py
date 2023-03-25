from .data_mock import train_sentences
from .celery_tasks import train_model


def test_train_model():
    train_model.delay("abc", train_sentences, 3)