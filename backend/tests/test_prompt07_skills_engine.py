import json
import pytest
from sqlalchemy.exc import IntegrityError
from app.models.skill import Skill, SKILL_LEVEL_MAP, SKILL_LEVEL_METADATA
from app.models.profile import Profile
from app.models.audit import ContentRevision, AuditEvent


# 1. 7-Level Metadata API and Domain Model
def test_skill_rating_metadata_and_domain_mapping(client):
    """
    Verify canonical 7-level rating metadata API.
    Must return exactly 7 levels, from Beginner (1) to Master (7).
    """
    res = client.get("/api/v1/skills/levels")
    assert res.status_code == 200
    levels = res.json()
    assert len(levels) == 7

    expected_levels = {
        1: "Beginner",
        2: "Novice",
        3: "Intermediate",
        4: "Proficient",
        5: "Advanced",
        6: "Expert",
        7: "Master"
    }

    for lvl in levels:
        rating = lvl["rating"]
        assert rating in expected_levels
        assert lvl["level"] == expected_levels[rating]
        assert lvl["display_order"] == rating
        assert len(lvl["description"]) > 0


# 2. Rating Boundary and Strict Integer Validation
def test_skill_rating_boundaries_and_rejections(client, admin_headers):
    """
    Verify backend rejects invalid ratings:
    0, 8, -1, 3.5 (decimal), non-integer strings, null.
    Accepts exact integers 1 through 7.
    """
    # 0 is rejected
    res = client.post("/api/v1/skills", headers=admin_headers, json={
        "name": "Invalid Zero", "rating": 0
    })
    assert res.status_code in [400, 422]

    # 8 is rejected
    res = client.post("/api/v1/skills", headers=admin_headers, json={
        "name": "Invalid Eight", "rating": 8
    })
    assert res.status_code in [400, 422]

    # Negative is rejected
    res = client.post("/api/v1/skills", headers=admin_headers, json={
        "name": "Invalid Negative", "rating": -3
    })
    assert res.status_code in [400, 422]

    # Float/decimal is rejected
    res = client.post("/api/v1/skills", headers=admin_headers, json={
        "name": "Invalid Float", "rating": 4.5
    })
    assert res.status_code in [400, 422]

    # Null rating is rejected
    res = client.post("/api/v1/skills", headers=admin_headers, json={
        "name": "Invalid Null", "rating": None
    })
    assert res.status_code in [400, 422]

    # Valid ratings 1 through 7 succeed with exact level label
    created_ids = []
    for r in range(1, 8):
        name = f"Valid Skill Scale {r}"
        res = client.post("/api/v1/skills", headers=admin_headers, json={
            "name": name,
            "rating": r,
            "category": "Domain Competency"
        })
        assert res.status_code == 201
        data = res.json()
        assert data["rating"] == r
        assert data["level_label"] == SKILL_LEVEL_MAP[r]
        created_ids.append(data["id"])

    # Cleanup
    for s_id in created_ids:
        client.delete(f"/api/v1/skills/{s_id}", headers=admin_headers)


# 3. Name Normalization & Validation
def test_skill_name_validation_and_whitespace_trimming(client, admin_headers):
    """
    Verify empty or whitespace names are rejected,
    leading/trailing whitespace is stripped,
    and capitalization (e.g. PostgreSQL, FastAPI) is preserved.
    """
    # Empty string
    res = client.post("/api/v1/skills", headers=admin_headers, json={
        "name": "", "rating": 4
    })
    assert res.status_code in [400, 422]

    # Whitespace only
    res = client.post("/api/v1/skills", headers=admin_headers, json={
        "name": "     ", "rating": 4
    })
    assert res.status_code in [400, 422]

    # Whitespace trimming + capitalization preservation
    res = client.post("/api/v1/skills", headers=admin_headers, json={
        "name": "   PostgreSQL Core Architecture   ",
        "rating": 6,
        "category": " Database Systems "
    })
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "PostgreSQL Core Architecture"
    assert data["category"] == "Database Systems"

    # Cleanup
    client.delete(f"/api/v1/skills/{data['id']}", headers=admin_headers)


# 4. Duplicate Skill Prevention
def test_duplicate_skill_prevention_case_insensitive(client, admin_headers):
    """
    Prevent duplicate skills for the same profile:
    - Case difference ('Rust' vs 'rust' vs 'RUST')
    - Whitespace variations ('  Rust  ')
    Returns 409 Conflict.
    """
    # 1. Create original
    res1 = client.post("/api/v1/skills", headers=admin_headers, json={
        "name": "Rust Systems Programming",
        "rating": 5,
        "category": "Systems"
    })
    assert res1.status_code == 201
    skill_id = res1.json()["id"]

    try:
        # 2. Attempt lowercase duplicate
        res_dup1 = client.post("/api/v1/skills", headers=admin_headers, json={
            "name": "rust systems programming",
            "rating": 4
        })
        assert res_dup1.status_code == 409
        dup_msg = res_dup1.json().get("detail") or res_dup1.json().get("error", {}).get("message", "")
        assert "already exists" in dup_msg.lower()

        # 3. Attempt uppercase with leading/trailing whitespace
        res_dup2 = client.post("/api/v1/skills", headers=admin_headers, json={
            "name": "  RUST SYSTEMS PROGRAMMING  ",
            "rating": 6
        })
        assert res_dup2.status_code == 409

        # 4. Create second distinct skill
        res2 = client.post("/api/v1/skills", headers=admin_headers, json={
            "name": "Go Concurrency",
            "rating": 5
        })
        assert res2.status_code == 201
        skill_id2 = res2.json()["id"]

        try:
            # 5. Attempt to update skill2 to skill1's name
            res_up_dup = client.put(f"/api/v1/skills/{skill_id2}", headers=admin_headers, json={
                "name": "rust systems programming",
                "rating": 5
            })
            assert res_up_dup.status_code == 409

            # 6. Updating skill1 keeping its own name succeeds (no self-conflict)
            res_self_up = client.put(f"/api/v1/skills/{skill_id}", headers=admin_headers, json={
                "name": "Rust Systems Programming",
                "rating": 6,
                "category": "Systems Core"
            })
            assert res_self_up.status_code == 200
            assert res_self_up.json()["rating"] == 6
        finally:
            client.delete(f"/api/v1/skills/{skill_id2}", headers=admin_headers)
    finally:
        client.delete(f"/api/v1/skills/{skill_id}", headers=admin_headers)


# 5. Full CRUD, Patching & PIN Security Integration
def test_skill_crud_lifecycle_and_pin_enforcement(client, admin_headers):
    """
    Verify complete CRUD operations and security:
    - Unauthenticated requests rejected (401/403)
    - Missing PIN rejected (403)
    - Valid PIN succeeds
    - Read individual skill (200)
    - Patch skill (200)
    - Safe delete (200)
    - Read deleted returns 404
    """
    auth_only = {"Authorization": admin_headers["Authorization"]}

    skill_payload = {
        "name": "Temporal Graph Algorithms",
        "category": "Algorithms",
        "description": "Dynamic network models and flows",
        "rating": 5,
        "visibility": True,
        "ordering": 1
    }

    # 1. Unauthenticated create rejected
    res_no_auth = client.post("/api/v1/skills", json=skill_payload)
    assert res_no_auth.status_code in [401, 403]

    # 2. Authenticated but missing PIN rejected
    res_no_pin = client.post("/api/v1/skills", headers=auth_only, json=skill_payload)
    assert res_no_pin.status_code == 403

    # 3. Create with PIN
    res_create = client.post("/api/v1/skills", headers=admin_headers, json=skill_payload)
    assert res_create.status_code == 201
    created = res_create.json()
    skill_id = created["id"]
    assert created["name"] == "Temporal Graph Algorithms"
    assert created["rating"] == 5
    assert created["level_label"] == "Advanced"

    try:
        # 4. Get by ID (publicly readable)
        res_get = client.get(f"/api/v1/skills/{skill_id}")
        assert res_get.status_code == 200
        assert res_get.json()["id"] == skill_id

        # 5. Patch update (partial)
        res_patch = client.patch(f"/api/v1/skills/{skill_id}", headers=admin_headers, json={
            "rating": 6,
            "description": "Updated high-throughput dynamic graph analysis"
        })
        assert res_patch.status_code == 200
        patched = res_patch.json()
        assert patched["rating"] == 6
        assert patched["level_label"] == "Expert"
        assert patched["description"] == "Updated high-throughput dynamic graph analysis"

        # 6. Delete without PIN rejected
        res_del_no_pin = client.delete(f"/api/v1/skills/{skill_id}", headers=auth_only)
        assert res_del_no_pin.status_code == 403

        # 7. Delete with PIN succeeds
        res_del = client.delete(f"/api/v1/skills/{skill_id}", headers=admin_headers)
        assert res_del.status_code == 200
        assert res_del.json()["success"] is True

        # 8. Get deleted skill returns 404
        res_get_del = client.get(f"/api/v1/skills/{skill_id}")
        assert res_get_del.status_code == 404
    except Exception:
        client.delete(f"/api/v1/skills/{skill_id}", headers=admin_headers)
        raise


# 6. Deterministic Ordering and Bulk Reordering
def test_skill_deterministic_ordering_and_bulk_reorder(client, admin_headers):
    """
    Verify bulk reorder endpoint:
    - PATCH /api/v1/skills/reorder
    - Validates ownership and existing IDs
    - Rejects foreign/unknown IDs
    - Rejects negative ordering
    - Rejects duplicate IDs
    - Deterministic order queries
    """
    # Create 3 skills
    s1 = client.post("/api/v1/skills", headers=admin_headers, json={"name": "Alpha Skill", "rating": 3, "ordering": 10}).json()
    s2 = client.post("/api/v1/skills", headers=admin_headers, json={"name": "Beta Skill", "rating": 5, "ordering": 20}).json()
    s3 = client.post("/api/v1/skills", headers=admin_headers, json={"name": "Gamma Skill", "rating": 7, "ordering": 30}).json()

    try:
        # Reorder via PATCH: reverse order
        reorder_payload = [
            {"id": s3["id"], "ordering": 1},
            {"id": s2["id"], "ordering": 2},
            {"id": s1["id"], "ordering": 3},
        ]
        res_reorder = client.patch("/api/v1/skills/reorder", headers=admin_headers, json=reorder_payload)
        assert res_reorder.status_code == 200
        assert res_reorder.json()["success"] is True

        # Fetch ordered list
        res_list = client.get("/api/v1/skills?sort_by=order")
        assert res_list.status_code == 200
        skills = res_list.json()
        ids_order = [s["id"] for s in skills if s["id"] in [s1["id"], s2["id"], s3["id"]]]
        assert ids_order == [s3["id"], s2["id"], s1["id"]]

        # Also test POST convention
        post_reorder = [
            {"id": s1["id"], "ordering": 5},
            {"id": s2["id"], "ordering": 15},
            {"id": s3["id"], "ordering": 25},
        ]
        res_post_reorder = client.post("/api/v1/skills/reorder", headers=admin_headers, json=post_reorder)
        assert res_post_reorder.status_code == 200

        # Reject unknown ID in reorder
        bad_reorder = [{"id": 999999, "ordering": 1}]
        res_bad = client.patch("/api/v1/skills/reorder", headers=admin_headers, json=bad_reorder)
        assert res_bad.status_code == 404

        # Reject duplicate ID in reorder
        dup_reorder = [{"id": s1["id"], "ordering": 1}, {"id": s1["id"], "ordering": 2}]
        res_dup = client.patch("/api/v1/skills/reorder", headers=admin_headers, json=dup_reorder)
        assert res_dup.status_code in [400, 422]
    finally:
        for s in [s1, s2, s3]:
            client.delete(f"/api/v1/skills/{s['id']}", headers=admin_headers)


# 7. Public vs Private Skills Representation
def test_public_vs_private_skills_boundary(client, admin_headers):
    """
    Public queries must strictly exclude hidden skills (is_visible=False).
    Admin queries with include_hidden=true reveal all skills.
    Consolidated public profile strictly excludes hidden skills.
    """
    pub_skill = client.post("/api/v1/skills", headers=admin_headers, json={
        "name": "Public Mastery Asset",
        "rating": 6,
        "visibility": True
    }).json()

    priv_skill = client.post("/api/v1/skills", headers=admin_headers, json={
        "name": "Confidential Internal Prototype",
        "rating": 2,
        "visibility": False
    }).json()

    try:
        # Public skills list
        res_pub = client.get("/api/v1/skills")
        pub_ids = [s["id"] for s in res_pub.json()]
        assert pub_skill["id"] in pub_ids
        assert priv_skill["id"] not in pub_ids

        # Consolidated public profile
        res_cons = client.get("/api/v1/profile/public")
        assert res_cons.status_code == 200
        cons_data = res_cons.json()
        cons_skill_ids = [s["id"] for s in cons_data.get("skills", [])]
        assert pub_skill["id"] in cons_skill_ids
        assert priv_skill["id"] not in cons_skill_ids

        # Admin query with include_hidden=True
        res_admin = client.get("/api/v1/skills?include_hidden=true")
        admin_ids = [s["id"] for s in res_admin.json()]
        assert pub_skill["id"] in admin_ids
        assert priv_skill["id"] in admin_ids
    finally:
        client.delete(f"/api/v1/skills/{pub_skill['id']}", headers=admin_headers)
        client.delete(f"/api/v1/skills/{priv_skill['id']}", headers=admin_headers)


# 8. Revision and Audit History Integration
def test_skill_revisions_and_audit_history(client, admin_headers, db_session):
    """
    Verify skill modifications record revisions and audit events:
    - Creation revision snapshot
    - Rating change revision details (e.g. 3 -> 5)
    - Deletion revision snapshot
    - Audit events: SKILL_CREATED, SKILL_UPDATED, SKILL_DELETED
    """
    # 1. Create
    res = client.post("/api/v1/skills", headers=admin_headers, json={
        "name": "Event Sourcing Patterns",
        "rating": 3,
        "category": "Architecture"
    })
    assert res.status_code == 201
    skill_id = res.json()["id"]

    try:
        # Check CREATE revision
        rev_create = db_session.query(ContentRevision).filter(
            ContentRevision.entity_name == "skill",
            ContentRevision.entity_id == str(skill_id),
            ContentRevision.action == "CREATE"
        ).first()
        assert rev_create is not None
        current_snap = json.loads(rev_create.current_snapshot) if isinstance(rev_create.current_snapshot, str) else rev_create.current_snapshot
        assert current_snap["name"] == "Event Sourcing Patterns"
        assert current_snap["rating"] == 3

        # 2. Update with rating change
        res_up = client.put(f"/api/v1/skills/{skill_id}", headers=admin_headers, json={
            "name": "Event Sourcing Patterns",
            "rating": 5,
            "category": "Architecture"
        })
        assert res_up.status_code == 200

        # Check UPDATE revision preserves historical rating change
        rev_update = db_session.query(ContentRevision).filter(
            ContentRevision.entity_name == "skill",
            ContentRevision.entity_id == str(skill_id),
            ContentRevision.action == "UPDATE"
        ).order_by(ContentRevision.id.desc()).first()
        assert rev_update is not None
        assert "Rating changed from Level 3" in rev_update.change_summary
        assert "to Level 5" in rev_update.change_summary
        prev_snap = json.loads(rev_update.previous_snapshot) if isinstance(rev_update.previous_snapshot, str) else rev_update.previous_snapshot
        new_snap = json.loads(rev_update.current_snapshot) if isinstance(rev_update.current_snapshot, str) else rev_update.current_snapshot
        assert prev_snap["rating"] == 3
        assert new_snap["rating"] == 5

        # Check audit event
        audit_up = db_session.query(AuditEvent).filter(
            AuditEvent.event_type == "SKILL_UPDATED"
        ).order_by(AuditEvent.id.desc()).first()
        assert audit_up is not None
        audit_details = json.loads(audit_up.details) if isinstance(audit_up.details, str) else audit_up.details
        assert audit_details["old_rating"] == 3
        assert audit_details["new_rating"] == 5

    finally:
        client.delete(f"/api/v1/skills/{skill_id}", headers=admin_headers)

    # Check DELETE revision
    rev_del = db_session.query(ContentRevision).filter(
        ContentRevision.entity_name == "skill",
        ContentRevision.entity_id == str(skill_id),
        ContentRevision.action == "DELETE"
    ).first()
    assert rev_del is not None
    assert rev_del.current_snapshot is None


# 9. Database-level constraints & index integrity
def test_skill_database_constraints_direct(db_session):
    """Direct database constraint tests on SQLAlchemy session."""
    prof = Profile(name="DB Integrity Tester")
    db_session.add(prof)
    db_session.commit()
    db_session.refresh(prof)

    # 1. Rating out of bounds check
    with pytest.raises(IntegrityError):
        bad_skill = Skill(
            profile_id=prof.id,
            name="Constraint Test 0",
            rating=0
        )
        db_session.add(bad_skill)
        db_session.commit()
    db_session.rollback()

    with pytest.raises(IntegrityError):
        bad_skill = Skill(
            profile_id=prof.id,
            name="Constraint Test 8",
            rating=8
        )
        db_session.add(bad_skill)
        db_session.commit()
    db_session.rollback()

    # 2. Empty name check
    with pytest.raises(IntegrityError):
        empty_skill = Skill(
            profile_id=prof.id,
            name="   ",
            rating=4
        )
        db_session.add(empty_skill)
        db_session.commit()
    db_session.rollback()

    # 3. Duplicate lower name constraint
    valid_skill = Skill(
        profile_id=prof.id,
        name="Asynchronous IO",
        rating=5
    )
    db_session.add(valid_skill)
    db_session.commit()

    with pytest.raises(IntegrityError):
        dup_skill = Skill(
            profile_id=prof.id,
            name="asynchronous io",
            rating=4
        )
        db_session.add(dup_skill)
        db_session.commit()
    db_session.rollback()


# 10. Multi-category selection and filtering across the 17 categories
def test_skill_multi_categories_selection_and_filtering(client, admin_headers):
    """
    Test 17 canonical categories retrieval, multi-category selection,
    case normalization, and multi-category filtering.
    """
    # 1. Categories endpoint returns all 17 categories
    res = client.get("/api/v1/skills/categories")
    assert res.status_code == 200
    data = res.json()
    assert "categories" in data
    cats = data["categories"]
    assert len(cats) == 17
    expected_17 = [
        "Technical", "Financial", "Analytical", "Business", "Leadership",
        "Management", "Diplomatic", "Creative", "Research", "Medical",
        "Legal", "Psychological", "Scientific", "Educational",
        "Environmental", "Operational", "Ethical"
    ]
    for expected in expected_17:
        assert expected in cats

    # 2. Create skill with multiple categories as a list
    skill_payload = {
        "name": "Quantitative Risk Architecture",
        "categories": ["Technical", "financial", "Analytical"],
        "rating": 6
    }
    create_res = client.post("/api/v1/skills", json=skill_payload, headers=admin_headers)
    assert create_res.status_code == 201
    created = create_res.json()
    skill_id = created["id"]

    try:
        # Check canonical case normalization and multi-category list
        assert created["categories"] == ["Technical", "Financial", "Analytical"]
        assert created["category"] == "Technical, Financial, Analytical"

        # 3. Create another skill with single category
        other_payload = {
            "name": "Corporate Ethics Governance",
            "categories": ["Ethical", "Legal"],
            "rating": 5
        }
        res_other = client.post("/api/v1/skills", json=other_payload, headers=admin_headers)
        assert res_other.status_code == 201
        other_id = res_other.json()["id"]

        try:
            # 4. Filter by category "Financial" -> matches Quantitative Risk Architecture
            filter_fin = client.get("/api/v1/skills?category=Financial")
            assert filter_fin.status_code == 200
            fin_items = filter_fin.json()
            assert any(s["id"] == skill_id for s in fin_items)
            assert not any(s["id"] == other_id for s in fin_items)

            # 5. Filter by category "Legal" -> matches Corporate Ethics Governance
            filter_leg = client.get("/api/v1/skills?category=Legal")
            assert filter_leg.status_code == 200
            leg_items = filter_leg.json()
            assert any(s["id"] == other_id for s in leg_items)
            assert not any(s["id"] == skill_id for s in leg_items)

            # 6. Update skill with new multiple categories
            patch_res = client.patch(
                f"/api/v1/skills/{skill_id}",
                json={"categories": ["Technical", "Research", "Scientific"]},
                headers=admin_headers
            )
            assert patch_res.status_code == 200
            patched = patch_res.json()
            assert patched["categories"] == ["Technical", "Research", "Scientific"]
            assert patched["category"] == "Technical, Research, Scientific"

        finally:
            client.delete(f"/api/v1/skills/{other_id}", headers=admin_headers)
    finally:
        client.delete(f"/api/v1/skills/{skill_id}", headers=admin_headers)


# 11. Skills Mastery Ratings Descending Order Output
def test_skills_sorted_by_mastery_ratings_descending(client, admin_headers):
    """
    Verify that skills are output sorted according to Mastery Ratings in descending order
    (Level 7 down to Level 1) in both the skills list and public consolidated profile.
    """
    s1 = client.post("/api/v1/skills", headers=admin_headers, json={"name": "SortSkill HTML", "rating": 2, "ordering": 1}).json()
    s2 = client.post("/api/v1/skills", headers=admin_headers, json={"name": "SortSkill Distributed Consensus", "rating": 7, "ordering": 5}).json()
    s3 = client.post("/api/v1/skills", headers=admin_headers, json={"name": "SortSkill Python", "rating": 5, "ordering": 2}).json()
    s4 = client.post("/api/v1/skills", headers=admin_headers, json={"name": "SortSkill Architecture", "rating": 7, "ordering": 1}).json()

    created_ids = [s1["id"], s2["id"], s3["id"], s4["id"]]
    try:
        # 1. Check GET /api/v1/skills (default rating descending)
        res_list = client.get("/api/v1/skills")
        assert res_list.status_code == 200
        skills = [s for s in res_list.json() if s["id"] in created_ids]
        # Rating 7 items first (ordered by display_order: s4 ordering=1, then s2 ordering=5)
        # then Rating 5 (s3), then Rating 2 (s1)
        assert [s["id"] for s in skills] == [s4["id"], s2["id"], s3["id"], s1["id"]]
        assert skills[0]["rating"] == 7
        assert skills[1]["rating"] == 7
        assert skills[2]["rating"] == 5
        assert skills[3]["rating"] == 2

        # 2. Check GET /api/v1/profile/public consolidated profile
        res_pub = client.get("/api/v1/profile/public")
        assert res_pub.status_code == 200
        pub_skills = [s for s in res_pub.json().get("skills", []) if s["id"] in created_ids]
        assert [s["id"] for s in pub_skills] == [s4["id"], s2["id"], s3["id"], s1["id"]]
        assert pub_skills[0]["rating"] == 7
        assert pub_skills[1]["rating"] == 7
        assert pub_skills[2]["rating"] == 5
        assert pub_skills[3]["rating"] == 2
    finally:
        for sid in created_ids:
            client.delete(f"/api/v1/skills/{sid}", headers=admin_headers)


# 12. Multi-Domain Skills Support (Engineering, Medical, Business, Legal & Emerging)
def test_multi_domain_skill_support(client, admin_headers):
    """
    Verify that skills support multiple domains simultaneously (e.g. Petroleum & Mechanical,
    Biotech & AI), synchronize domain string and domains array, and match domain query filters.
    """
    payload = {
        "name": "Computational Fluid Dynamics in Drilling",
        "domains": [
            "Petroleum & Natural Gas Engineering",
            "Mechanical & Mechatronics Engineering",
            "Computer Science & Artificial Intelligence"
        ],
        "rating": 6,
        "ordering": 1
    }
    create_res = client.post("/api/v1/skills", headers=admin_headers, json=payload)
    assert create_res.status_code == 201
    created_skill = create_res.json()
    skill_id = created_skill["id"]

    try:
        # Check that both 'domain' and 'domains' are correctly returned
        assert "Petroleum & Natural Gas Engineering" in created_skill["domain"]
        assert "Mechanical & Mechatronics Engineering" in created_skill["domain"]
        assert "Computer Science & Artificial Intelligence" in created_skill["domain"]
        assert len(created_skill["domains"]) == 3
        assert "Petroleum & Natural Gas Engineering" in created_skill["domains"]
        assert "Mechanical & Mechatronics Engineering" in created_skill["domains"]
        assert "Computer Science & Artificial Intelligence" in created_skill["domains"]

        # Check GET /api/v1/skills/{id}
        get_res = client.get(f"/api/v1/skills/{skill_id}")
        assert get_res.status_code == 200
        fetched = get_res.json()
        assert len(fetched["domains"]) == 3
        assert "Petroleum & Natural Gas Engineering" in fetched["domains"]

        # Check filtering by any of the domains
        petro_search = client.get("/api/v1/skills?domain=Petroleum")
        assert petro_search.status_code == 200
        assert any(s["id"] == skill_id for s in petro_search.json())

        mech_search = client.get("/api/v1/skills?domain=Mechanical")
        assert mech_search.status_code == 200
        assert any(s["id"] == skill_id for s in mech_search.json())

        ai_search = client.get("/api/v1/skills?domain=Artificial+Intelligence")
        assert ai_search.status_code == 200
        assert any(s["id"] == skill_id for s in ai_search.json())

        # Check updating domains via PUT
        update_payload = {
            "name": "Computational Fluid Dynamics in Drilling",
            "rating": 6,
            "domains": [
                "Biotechnology & Bioengineering",
                "Medical & Clinical Sciences"
            ]
        }
        put_res = client.put(f"/api/v1/skills/{skill_id}", headers=admin_headers, json=update_payload)
        assert put_res.status_code == 200
        updated = put_res.json()
        assert len(updated["domains"]) == 2
        assert "Biotechnology & Bioengineering" in updated["domains"]
        assert "Medical & Clinical Sciences" in updated["domains"]

        # Check updating domains via PATCH
        patch_res = client.patch(
            f"/api/v1/skills/{skill_id}",
            headers=admin_headers,
            json={"domains": ["Metallurgy & Materials Science Engineering", "Mining Engineering"]}
        )
        assert patch_res.status_code == 200
        patched = patch_res.json()
        assert len(patched["domains"]) == 2
        assert "Metallurgy & Materials Science Engineering" in patched["domains"]
    finally:
        client.delete(f"/api/v1/skills/{skill_id}", headers=admin_headers)



