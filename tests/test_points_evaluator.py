from acrossfc.core.points import PointsEvaluator
from acrossfc.core.constants import CURRENT_EXTREMES


def test_this():
    # point_events = PointsEvaluator("https://www.fflogs.com/reports/W9VNKackfztR13g2#fight=16&type=damage-done", "xxxx").point_events
    # evaluator = PointsEvaluator("https://www.fflogs.com/reports/fKHn6F1a9jrX4g3D#fight=11&type=damage-done", "xxxx")
    # evaluator = PointsEvaluator("https://www.fflogs.com/reports/WwpaMt63cLHvV8BF#fight=8&type=damage-done", "xxxx")
    evaluator = PointsEvaluator("https://www.fflogs.com/reports/zmZg9tHFj4JaQ8Lr#fight=1&type=damage-done", "xxxx")
    point_events = evaluator.point_events
    print(point_events)

    print(f"Report: {evaluator.fight_data.encounter_id} {evaluator.fight_data.difficulty_id}")
    for e in CURRENT_EXTREMES:
        print(f"Fight: {e.encounter_id} {e.difficulty_id}")
