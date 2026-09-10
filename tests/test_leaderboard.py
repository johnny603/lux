import leaderboard


def test_safe_profile_name():
 
    state = {"profile": None}
    assert leaderboard._safe_profile_name(state) == "Learner"

   
    state_empty = {}
    assert leaderboard._safe_profile_name(state_empty) == "Learner"

    state_valid = {"profile": {"display_name": "ABC"}}
    assert leaderboard._safe_profile_name(state_valid) == "ABC"


    state_whitespace = {"profile": {"display_name": "   "}}
    assert leaderboard._safe_profile_name(state_whitespace) == "Learner"


def test_get_leaderboard():
    state = {
        "profile": {"display_name": "Alice"},
        "solved": {"1": {"solved_at": "2026-01-01"}, "2": {"solved_at": "2026-01-02"}},
        "meta": {"streak": {"current": 5, "longest": 10}},
        "game": {"xp": 150},
    }


    result_solved = leaderboard.get_leaderboard(state)
    assert result_solved["metric"] == "solved_count"
    assert len(result_solved["entries"]) == 1

    entry = result_solved["entries"][0]
    assert entry["name"] == "Alice"
    assert entry["solved_count"] == 2
    assert entry["streak"] == 5
    assert entry["xp"] == 150
    assert entry["score"] == 2.0


    result_streak = leaderboard.get_leaderboard(state, metric="streak")
    assert result_streak["metric"] == "streak"
    assert result_streak["entries"][0]["score"] == 5.0

    
    result_xp = leaderboard.get_leaderboard(state, metric="xp")
    assert result_xp["metric"] == "xp"
    assert result_xp["entries"][0]["score"] == 150.0


def test_upsert_local_entry():
    state = {
        "profile": {"display_name": "Bob"},
        "solved": {"1": {}},
        "meta": {"streak": {"current": 3}},
        "game": {"xp": 75},
    }
    board = leaderboard.upsert_local_entry(state)
    assert "local" in board
    assert board["local"]["name"] == "Bob"
    assert board["local"]["solved_count"] == 1
    assert board["local"]["streak"] == 3
    assert board["local"]["xp"] == 75
    assert state["leaderboard"]["local"] == board["local"]