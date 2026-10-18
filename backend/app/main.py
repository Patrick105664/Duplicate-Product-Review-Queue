import json
import os
import sys
from pathlib import Path
import re

from fastapi import Depends, Request
from app.reviewers import (
    create_reviewer,
    authenticate,
    create_session,
    get_session_reviewer,
    delete_session,
)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from starlette.staticfiles import StaticFiles

from app.db import get_conn, init_db, save_suggestions
from app.metrics_store import save_metric_snapshot
from app.queries import list_products
from app.scans import start_scan_run, finish_scan_run
from app.ui_adapter import (
    ui_pairs,
    ui_pair,
    ui_products,
    ui_product,
    submit_ui_decision,
    ui_metrics,
    ui_scans,
    ui_export,
)

# Locate the existing core duplicate-detection project.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORE_DIR = PROJECT_ROOT / "C06_Duplicate_Review"
FIXTURE_PATH = CORE_DIR / "fixture.json"
FRONTEND_DIST = PROJECT_ROOT / "catalogguard_frontend" / "dist"
SERVE_FRONTEND = os.getenv("SERVE_FRONTEND", "false").lower() == "true"

# Make matching_engine.py and evaluation.py importable from the core folder.
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

from matching_engine import compare_products
from evaluation import evaluate_pairs


app = FastAPI(
    title="Duplicate Product Review API",
    description="API for reviewing potential duplicate product listings.",
    version="1.1.0",
)

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174,"
        "http://localhost:5175,http://127.0.0.1:5175",
    ).split(",")
    if origin.strip()
]
cookie_samesite = os.getenv("COOKIE_SAMESITE", "lax").lower()
cookie_secure = os.getenv("COOKIE_SECURE", "false").lower() == "true"

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if SERVE_FRONTEND and (FRONTEND_DIST / "assets").is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_DIST / "assets"),
        name="frontend-assets",
    )


def get_database():
    conn = get_conn()
    init_db(conn)
    return conn


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


SESSION_COOKIE = "review_session"


def current_reviewer(request: Request):
    token = request.cookies.get(SESSION_COOKIE)

    if not token:
        raise HTTPException(status_code=401, detail="Please log in.")

    conn = get_database()
    try:
        reviewer = get_session_reviewer(conn, token)
        if not reviewer:
            raise HTTPException(
                status_code=401,
                detail="Session expired. Please log in.",
            )
        return reviewer
    finally:
        conn.close()


@app.post("/api/auth/register")
def register(payload: RegisterRequest, response: Response):
    name = payload.name.strip()
    email = payload.email.strip().lower()
    password = payload.password

    if not name:
        raise HTTPException(status_code=400, detail="Name is required.")

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise HTTPException(
            status_code=400,
            detail="Enter a valid email address.",
        )

    if len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters.",
        )

    conn = get_database()
    try:
        create_reviewer(
            conn,
            username=email,
            password=password,
            display_name=name,
        )

        # Registration creates the account only.
        # It does not create a login session.
        # Clear a stale session cookie from a previous browser session.
        response.delete_cookie(
            key=SESSION_COOKIE,
            path="/",
            httponly=True,
            secure=cookie_secure,
            samesite=cookie_samesite,
        )

        return {
            "message": "Account created successfully! Please log in.",
            "email": email,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    finally:
        conn.close()


@app.post("/api/auth/login")
def login(payload: LoginRequest, response: Response):
    conn = get_database()
    try:
        reviewer = authenticate(conn, payload.email, payload.password)

        if not reviewer:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password.",
            )

        # A session is created only after successful login.
        token = create_session(conn, reviewer["reviewer_id"])

        response.set_cookie(
            key=SESSION_COOKIE,
            value=token,
            httponly=True,
            secure=cookie_secure,
            samesite=cookie_samesite,
            max_age=43200,
            path="/",
        )

        return {"user": reviewer}

    finally:
        conn.close()


@app.get("/api/auth/me")
def auth_me(reviewer: dict = Depends(current_reviewer)):
    return {"user": reviewer}


@app.post("/api/auth/logout")
def logout(request: Request, response: Response):
    token = request.cookies.get(SESSION_COOKIE)

    if token:
        conn = get_database()
        try:
            delete_session(conn, token)
        finally:
            conn.close()

    response.delete_cookie(
        key=SESSION_COOKIE,
        path="/",
        httponly=True,
        secure=cookie_secure,
        samesite=cookie_samesite,
    )

    return {"message": "Logged out successfully."}


def evaluate_core_fixture():
    """Evaluate the existing synthetic labelled fixture."""
    if not FIXTURE_PATH.exists():
        raise FileNotFoundError(
            f"Core evaluation fixture not found: {FIXTURE_PATH}"
        )

    with FIXTURE_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    records = data["records"]

    products = {
        product["product_id"]: product
        for product in records["products"]
    }

    labelled_pairs = records["labelled_pairs"]

    # evaluate_pairs writes the detailed results.csv file.
    results = evaluate_pairs(labelled_pairs, products)

    return results


def save_fixture_metrics(conn):
    """Persist evaluation metrics from the synthetic labelled fixture."""
    results = evaluate_core_fixture()

    tp = results["TP"]
    fp = results["FP"]
    tn = results["TN"]
    fn = results["FN"]
    total = results["total"]

    precision_den = tp + fp
    recall_den = tp + fn

    save_metric_snapshot(
        conn,
        source="C06 synthetic labelled fixture",
        label="Synthetic fixture evaluation",
        true_positives=tp,
        false_positives=fp,
        false_negatives=fn,
        true_negatives=tn,
        precision=results["precision"],
        recall=results["recall"],
        accuracy=results["accuracy"],
        precision_num=tp if precision_den > 0 else None,
        precision_den=precision_den if precision_den > 0 else None,
        recall_num=tp if recall_den > 0 else None,
        recall_den=recall_den if recall_den > 0 else None,
        accuracy_num=tp + tn if total > 0 else None,
        accuracy_den=total if total > 0 else None,
        notes=(
            "Evaluation on synthetic labelled fixture pairs. "
            "Not a production performance measurement."
        ),
    )

    return results


def run_catalogue_detection(conn):
    """Compare catalogue products and save newly predicted duplicate pairs."""
    db_products = list_products(conn)

    # Map database product fields to the core matcher's expected fields.
    products = {}

    for row in db_products:
        product_id = row.get("product_id")

        if not product_id:
            continue

        extra = row.get("extra") or {}

        products[product_id] = {
            "product_id": product_id,
            "title": row.get("title"),
            "brand": row.get("brand"),
            "model": row.get("model"),
            "pack_quantity": row.get("pack_quantity"),
            "size": (
                row.get("variant")
                if row.get("variant") is not None
                else extra.get("size")
            ),
        }

    product_ids = list(products.keys())
    suggestions = []

    # Compare each unordered product pair exactly once.
    for i, id_a in enumerate(product_ids):
        for id_b in product_ids[i + 1:]:
            product_a = products[id_a]
            product_b = products[id_b]

            result = compare_products(product_a, product_b)

            if not result["predicted_duplicate"]:
                continue

            score = result["similarity_score"]

            # Existing UI supports either 0-1 scores or percentages.
            suggestions.append({
                "id_a": id_a,
                "id_b": id_b,
                "confidence": score,
                "reasons": result["evidence"],
                "flags": result["conflicts"],
            })

    new_pairs = save_suggestions(conn, suggestions)

    return {
        "products_scanned": len(products),
        "candidate_pairs": len(suggestions),
        "new_pairs": new_pairs,
    }


@app.get("/")
def root():
    index_file = FRONTEND_DIST / "index.html"
    if SERVE_FRONTEND and index_file.is_file():
        return FileResponse(index_file)

    return {
        "message": "Duplicate Product Review Queue API is running"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/products")
def products():
    conn = get_database()
    try:
        return ui_products(conn)
    finally:
        conn.close()


@app.get("/api/products/{product_id}")
def product_detail(product_id: str):
    conn = get_database()
    try:
        result = ui_product(conn, product_id)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found",
            )

        return result

    finally:
        conn.close()


@app.get("/api/pairs")
def pairs(status: str | None = None):
    conn = get_database()
    try:
        return ui_pairs(conn, status=status)
    finally:
        conn.close()


@app.get("/api/pairs/{pair_id}")
def pair_detail(pair_id: str):
    conn = get_database()
    try:
        result = ui_pair(conn, pair_id)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Review pair not found",
            )

        return result

    finally:
        conn.close()


class DecisionRequest(BaseModel):
    decision: str
    note: str | None = None
    reviewer: str = "Demo Reviewer"


@app.post("/api/pairs/{pair_id}/decision")
def decide_pair(pair_id: str, payload: DecisionRequest):
    conn = get_database()
    try:
        return submit_ui_decision(
            conn,
            pair_id,
            decision=payload.decision,
            note=payload.note,
            reviewer=payload.reviewer,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    finally:
        conn.close()


@app.get("/api/metrics")
def metrics():
    conn = get_database()
    try:
        return ui_metrics(conn)
    finally:
        conn.close()


@app.get("/api/scans")
def scans(limit: int = 50):
    conn = get_database()
    try:
        return ui_scans(conn, limit=limit)
    finally:
        conn.close()


@app.post("/api/rescan")
def rescan():
    """Run catalogue matching, save scan history and refresh fixture metrics."""
    conn = get_database()
    scan_id = None

    try:
        scan_id = start_scan_run(conn, source="current-catalogue")

        detection = run_catalogue_detection(conn)
        metrics_result = save_fixture_metrics(conn)

        # Count pairs that are still waiting for human review.
        pending_reviews = len(ui_pairs(conn, status="pending"))

        finish_scan_run(
            conn,
            scan_id,
            products_count=detection["products_scanned"],
            pairs_found=detection["candidate_pairs"],
            new_pairs=detection["new_pairs"],
            status="completed",
        )

        return {
            "id": f"SCAN-{scan_id:04d}",
            "status": "completed",
            "message": (
                f"Scan completed: {detection['candidate_pairs']} candidate pairs found, "
                f"{pending_reviews} pending reviews, "
                f"{detection['new_pairs']} new pairs added."
            ),
            "productsScanned": detection["products_scanned"],
            "candidatePairs": detection["candidate_pairs"],
            "pairsFound": detection["candidate_pairs"],
            "pendingReviews": pending_reviews,
            "newPairs": detection["new_pairs"],
            "evaluation": {
                "source": "C06 synthetic labelled fixture",
                "total": metrics_result["total"],
                "TP": metrics_result["TP"],
                "FP": metrics_result["FP"],
                "TN": metrics_result["TN"],
                "FN": metrics_result["FN"],
                "precision": metrics_result["precision"],
                "recall": metrics_result["recall"],
                "accuracy": metrics_result["accuracy"],
            },
            "note": (
                "Detection ran on the current catalogue. Evaluation metrics "
                "come from the synthetic labelled fixture, not production data."
            ),
        }

    except Exception as exc:
        if scan_id is not None:
            try:
                finish_scan_run(
                    conn,
                    scan_id,
                    products_count=0,
                    pairs_found=0,
                    new_pairs=0,
                    status="failed",
                    error=str(exc),
                )
            except Exception:
                pass

        raise HTTPException(
            status_code=500,
            detail=f"Rescan failed: {exc}",
        ) from exc

    finally:
        conn.close()


@app.get("/api/exports")
def exports(format: str = "csv", type: str = "reviews"):
    conn = get_database()
    try:
        content, media_type, filename = ui_export(
            conn,
            format,
            type,
        )

        return Response(
            content=content,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            },
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    finally:
        conn.close()


if SERVE_FRONTEND and (FRONTEND_DIST / "index.html").is_file():
    @app.get("/{frontend_path:path}", include_in_schema=False)
    def frontend_route(frontend_path: str):
        if frontend_path == "api" or frontend_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")

        dist_root = FRONTEND_DIST.resolve()
        requested_file = (dist_root / frontend_path).resolve()
        if not requested_file.is_relative_to(dist_root):
            raise HTTPException(status_code=404, detail="Not found")

        if requested_file.is_file():
            return FileResponse(requested_file)

        return FileResponse(dist_root / "index.html")