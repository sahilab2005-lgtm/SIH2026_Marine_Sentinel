from marine_sentinel.reporting import build_report
from marine_sentinel.schemas import Detection, SurveyMetadata


def test_report_contains_dimensions_and_geotag():
    report = build_report([Detection(10, 20, 30, 40, "Crab pot / debris", .8, "YOLO")],
                          SurveyMetadata(18.922, 72.8347, .1))
    assert report.iloc[0]["priority"] == "HIGH"
    assert report.iloc[0]["width_m"] == 3.0
    assert 18.921 < report.iloc[0]["latitude"] < 18.922
