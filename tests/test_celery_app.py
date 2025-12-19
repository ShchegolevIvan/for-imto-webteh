from app.celery_app import celery_app


def test_celery_config_has_weekly_digest():
    assert "weekly-digest" in celery_app.conf.beat_schedule
    assert celery_app.conf.beat_schedule["weekly-digest"]["task"] == "app.tasks.send_weekly_digest"
