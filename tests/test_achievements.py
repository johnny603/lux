import storage
import achievements


def test_threshold_achievements(tmp_path):
    path = tmp_path / "state.json"
    state = {"version": 1, "solved": {}, "achievements": {}}
    # no achievements yet
    newly = achievements.evaluate_achievements(state)
    assert newly == []

    # mark 1 solved
    state["solved"]["1"] = {"first_solved": "t"}
    newly = achievements.evaluate_achievements(state)
    assert any(a["id"] == "first_solve" for a in newly)

    # mark more solves
    for i in range(2, 6):
        state["solved"][str(i)] = {"first_solved": "t"}
    newly = achievements.evaluate_achievements(state)
    assert any(a["id"] == "solve_5" for a in newly)


def test_category_achievement():
    # levels: two in CatA, one in CatB
    levels = [
        {"id": "1", "category": "CatA"},
        {"id": "2", "category": "CatA"},
        {"id": "3", "category": "CatB"},
    ]
    state = {"version": 1, "solved": {}, "achievements": {}}
    # solve all CatA
    state["solved"]["1"] = {}
    state["solved"]["2"] = {}
    newly = achievements.evaluate_achievements(state, levels)
    assert any(a["id"] == "category_CatA" for a in newly)
