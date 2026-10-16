from backend.app.services.report_service import get_model_performance_metrics


def test_model_performance_metrics_are_loaded_from_saved_evaluation():
    metrics = get_model_performance_metrics()

    assert metrics["threshold"] == 0.9
    assert metrics["precision"] > 0.7
    assert metrics["recall"] > 0.9
    assert metrics["f1_score"] > 0.8
