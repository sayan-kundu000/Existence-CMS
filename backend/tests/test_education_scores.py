import pytest


def test_education_score_percentage_valid(client, admin_headers):
    payload = {
        "level": "Graduate",
        "stream": "Computer Science",
        "institution": "Stanford University",
        "starting_month_year": "Aug 2018",
        "ending_month_year": "May 2022",
        "currently_studying": False,
        "score_type": "Percentage",
        "score_value": 89.75,
        "ordering": 1
    }
    res = client.post("/api/v1/education", json=payload, headers=admin_headers)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["score_type"] == "Percentage"
    assert data["score_value"] == 89.75
    assert data["stream"] == "Computer Science"


def test_education_score_cgpa10_valid(client, admin_headers):
    payload = {
        "level": "Undergraduate",
        "stream": "Information Technology",
        "institution": "MIT",
        "starting_month_year": "Aug 2014",
        "ending_month_year": "May 2018",
        "currently_studying": False,
        "score_type": "CGPA 10",
        "score_value": 9.45,
        "ordering": 2
    }
    res = client.post("/api/v1/education", json=payload, headers=admin_headers)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["score_type"] == "CGPA 10"
    assert data["score_value"] == 9.45


def test_education_score_cgpa5_valid(client, admin_headers):
    payload = {
        "level": "Post Graduate",
        "stream": "Data Science",
        "institution": "Oxford University",
        "starting_month_year": "Oct 2022",
        "ending_month_year": "Jun 2024",
        "currently_studying": False,
        "score_type": "CGPA 5",
        "score_value": 4.85,
        "ordering": 3
    }
    res = client.post("/api/v1/education", json=payload, headers=admin_headers)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["score_type"] == "CGPA 5"
    assert data["score_value"] == 4.85


def test_education_score_bounds_rejected(client, admin_headers):
    # Percentage > 100 rejected
    res1 = client.post("/api/v1/education", json={
        "level": "Graduate",
        "stream": "Physics",
        "starting_month_year": "Jan 2020",
        "ending_month_year": "Dec 2023",
        "currently_studying": False,
        "score_type": "Percentage",
        "score_value": 101.5
    }, headers=admin_headers)
    assert res1.status_code == 422

    # Percentage < 0 rejected
    res2 = client.post("/api/v1/education", json={
        "level": "Graduate",
        "stream": "Physics",
        "starting_month_year": "Jan 2020",
        "ending_month_year": "Dec 2023",
        "currently_studying": False,
        "score_type": "Percentage",
        "score_value": -1.0
    }, headers=admin_headers)
    assert res2.status_code == 422

    # CGPA 10 > 10 rejected
    res3 = client.post("/api/v1/education", json={
        "level": "Graduate",
        "stream": "Mathematics",
        "starting_month_year": "Jan 2020",
        "ending_month_year": "Dec 2023",
        "currently_studying": False,
        "score_type": "CGPA 10",
        "score_value": 10.5
    }, headers=admin_headers)
    assert res3.status_code == 422

    # CGPA 5 > 5 rejected
    res4 = client.post("/api/v1/education", json={
        "level": "Graduate",
        "stream": "Chemistry",
        "starting_month_year": "Jan 2020",
        "ending_month_year": "Dec 2023",
        "currently_studying": False,
        "score_type": "CGPA 5",
        "score_value": 5.2
    }, headers=admin_headers)
    assert res4.status_code == 422


def test_education_score_decimal_places_rejected(client, admin_headers):
    # 3 decimal places rejected
    res = client.post("/api/v1/education", json={
        "level": "Graduate",
        "stream": "Biotechnology",
        "starting_month_year": "Jan 2020",
        "ending_month_year": "Dec 2023",
        "currently_studying": False,
        "score_type": "Percentage",
        "score_value": 85.555
    }, headers=admin_headers)
    assert res.status_code == 422


def test_education_score_mismatched_inputs(client, admin_headers):
    # Score type without score value
    res1 = client.post("/api/v1/education", json={
        "level": "Graduate",
        "stream": "Economics",
        "starting_month_year": "Jan 2020",
        "ending_month_year": "Dec 2023",
        "currently_studying": False,
        "score_type": "Percentage",
        "score_value": None
    }, headers=admin_headers)
    assert res1.status_code == 422

    # Score value without score type
    res2 = client.post("/api/v1/education", json={
        "level": "Graduate",
        "stream": "Economics",
        "starting_month_year": "Jan 2020",
        "ending_month_year": "Dec 2023",
        "currently_studying": False,
        "score_type": None,
        "score_value": 85.0
    }, headers=admin_headers)
    assert res2.status_code == 422


def test_high_school_and_matriculation_stream_locked(client, admin_headers):
    # High School: stream is locked to None even if filled
    res1 = client.post("/api/v1/education", json={
        "level": "High School",
        "stream": "Should Be Locked",
        "institution": "St. Xavier's High School",
        "starting_month_year": "Jun 2012",
        "ending_month_year": "May 2014",
        "currently_studying": False,
        "score_type": "Percentage",
        "score_value": 92.40
    }, headers=admin_headers)
    assert res1.status_code == 201, res1.text
    data1 = res1.json()
    assert data1["level"] == "High School"
    assert data1["stream"] is None
    assert data1["score_type"] == "Percentage"
    assert data1["score_value"] == 92.40

    # Matriculation: stream is locked to None even if empty or None
    res2 = client.post("/api/v1/education", json={
        "level": "Matriculation",
        "stream": None,
        "institution": "Public School",
        "starting_month_year": "Jun 2010",
        "ending_month_year": "May 2012",
        "currently_studying": False,
        "score_type": "CGPA 10",
        "score_value": 9.8
    }, headers=admin_headers)
    assert res2.status_code == 201, res2.text
    data2 = res2.json()
    assert data2["level"] == "Matriculation"
    assert data2["stream"] is None
    assert data2["score_type"] == "CGPA 10"
    assert data2["score_value"] == 9.8


def test_higher_education_stream_required(client, admin_headers):
    # Graduate without stream rejected
    res = client.post("/api/v1/education", json={
        "level": "Graduate",
        "stream": None,
        "institution": "University",
        "starting_month_year": "Aug 2018",
        "ending_month_year": "May 2022",
        "currently_studying": False
    }, headers=admin_headers)
    assert res.status_code == 422


def test_currently_studying_locks_score_and_end_date(client, admin_headers):
    # When currently_studying is True, score and ending date are locked (set to None)
    res = client.post("/api/v1/education", json={
        "level": "Doctorate",
        "stream": "Quantum Physics",
        "institution": "Caltech",
        "starting_month_year": "Aug 2023",
        "ending_month_year": "May 2027",  # Should be cleared
        "currently_studying": True,
        "score_type": "CGPA 10",          # Should be cleared
        "score_value": 9.5                 # Should be cleared
    }, headers=admin_headers)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["currently_studying"] is True
    assert data["ending_month_year"] is None
    assert data["score_type"] is None
    assert data["score_value"] is None


def test_education_diploma_level_valid(client, admin_headers):
    res = client.post("/api/v1/education", json={
        "level": "Diploma",
        "stream": "Applied Mechanical Engineering",
        "institution": "Polytechnic Institute",
        "starting_month_year": "Aug 2017",
        "ending_month_year": "May 2020",
        "currently_studying": False,
        "score_type": "Percentage",
        "score_value": 84.50
    }, headers=admin_headers)
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["level"] == "Diploma"
    assert data["stream"] == "Applied Mechanical Engineering"
    assert data["score_type"] == "Percentage"
    assert data["score_value"] == 84.50


def test_education_sorting_by_level_descending_hierarchy(client, admin_headers):
    # Clear any existing education records first to test sort deterministically
    existing = client.get("/api/v1/education").json()
    for item in existing:
        client.delete(f"/api/v1/education/{item['id']}", headers=admin_headers)

    # Insert levels in random/arbitrary order
    items_to_create = [
        {"level": "Matriculation", "stream": None, "starting_month_year": "Jun 2010", "ending_month_year": "May 2012"},
        {"level": "Post Graduate", "stream": "AI & ML", "starting_month_year": "Aug 2022", "ending_month_year": "May 2024"},
        {"level": "High School", "stream": None, "starting_month_year": "Jun 2012", "ending_month_year": "May 2014"},
        {"level": "Diploma", "stream": "Electronics", "starting_month_year": "Aug 2014", "ending_month_year": "May 2017"},
        {"level": "Doctorate", "stream": "Cognitive Science", "starting_month_year": "Aug 2024", "ending_month_year": "May 2028"},
        {"level": "Graduate", "stream": "Computer Science", "starting_month_year": "Aug 2017", "ending_month_year": "May 2021"}
    ]
    for item in items_to_create:
        res = client.post("/api/v1/education", json={**item, "currently_studying": False}, headers=admin_headers)
        assert res.status_code == 201, res.text

    # 1. Test GET /api/v1/education output order
    list_res = client.get("/api/v1/education")
    assert list_res.status_code == 200
    levels = [e["level"] for e in list_res.json()]
    assert levels == [
        "Doctorate",
        "Post Graduate",
        "Graduate",
        "Diploma",
        "High School",
        "Matriculation"
    ], f"Unexpected level order: {levels}"

    # 2. Test consolidated public profile output order
    pub_res = client.get("/api/v1/profile/public")
    assert pub_res.status_code == 200
    pub_levels = [e["level"] for e in pub_res.json()["education"]]
    assert pub_levels == [
        "Doctorate",
        "Post Graduate",
        "Graduate",
        "Diploma",
        "High School",
        "Matriculation"
    ], f"Unexpected public profile level order: {pub_levels}"

