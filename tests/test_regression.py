from oracle import is_failure


def test_regression_minimal_input_no_longer_fails():
    # Regression guard for the parse_bool type-handling defect, using the 1-minimal
    # failure-inducing input from delta debugging (Question 5). Checked through the
    # Question 2 oracle: a non-string boolean must be a controlled ConfigError, so
    # is_failure() must return False (not an uncontrolled crash). If the defect is
    # reintroduced, is_failure() returns True and this test goes red.
    raw = {"server": {}, "features": {"debug": None}, "limits": {}}

    assert is_failure(raw) is False
