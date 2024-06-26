# stdlib
import logging
from typing import Optional, Dict, List, Union

# 3rd-party
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Local
from acrossfc.api import submissions, participation_points, fc_roster
from acrossfc.core.model import PointsCategory, SubmissionsChannel
from acrossfc.ext.ddb_client import DDB_CLIENT

LOG_FORMAT = (
    "<TEST API> %(asctime)s.%(msecs)03d [%(levelname)s] %(filename)s:%(lineno)d: %(message)s"
)

if len(logging.getLogger().handlers) == 0:
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    LOG = logging.getLogger(__name__)
else:
    LOG = logging.getLogger()


logging.getLogger('uvicorn').setLevel(logging.DEBUG)

app = FastAPI(debug=True)


origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/submissions")
def get_submissions(tier: str):
    subs = submissions.get_submissions_for_tier(tier)
    return subs


@app.get("/submissions/{uuid}")
def get_submission_by_id(uuid: str):
    sub = DDB_CLIENT.get_submission_by_uuid(uuid)
    return sub


@app.get("/submissions/queue")
def get_submissions_queue():
    queue = submissions.get_submissions_queue()
    return queue


@app.get("/current_tier")
def get_current_submissions_tier():
    return submissions.get_current_submissions_tier()


class ReviewSubmissionsBody(BaseModel):
    submission_uuid: str
    points_event_to_approved: Dict[str, bool]
    reviewer_id: int
    notes: Optional[str] = None


@app.post("/submissions/review")
def review_submission(body: ReviewSubmissionsBody):
    LOG.info(body)
    return submissions.review_submission(
        body.submission_uuid,
        body.points_event_to_approved,
        body.reviewer_id,
        notes=body.notes
    )


class EvaluateFFLogsBody(BaseModel):
    fflogs_url: str
    is_fc_pf: bool
    is_static: bool


@app.post("/submissions/evaluate")
def evaluate_fflogs(body: EvaluateFFLogsBody):
    return submissions.evaluate_fflogs(body.fflogs_url, body.is_fc_pf, body.is_static)


class SubmitFFLogsBody(BaseModel):
    fflogs_url: str
    submitted_by: submissions.ComboUserID
    submission_channel: Union[int, str]
    is_static: bool
    is_fc_pf: bool
    fc_pf_id: Optional[str] = None,


@app.post("/submissions/fflogs")
def submit_fflogs(body: SubmitFFLogsBody):
    return submissions.submit_fflogs(
        fflogs_url=body.fflogs_url,
        submitted_by=body.submitted_by,
        submission_channel=SubmissionsChannel.to_enum(body.submission_channel),
        is_fc_pf=body.is_fc_pf,
        is_static=body.is_static,
        fc_pf_id=body.fc_pf_id
    )


class SubmitManualBody(BaseModel):
    point_categories_to_member_ids_map: Dict[Union[int, str], List[int]]
    submitted_by: submissions.ComboUserID
    submission_channel: Union[int, str]
    is_static: bool
    is_fc_pf: bool
    fflogs_url: Optional[str] = None
    fc_pf_id: Optional[str] = None
    auto_approve_admin_id: Optional[int] = None
    notes: Optional[str] = None


@app.post("/submissions/manual")
def submit_manual(body: SubmitManualBody):
    return submissions.submit_manual(
        point_categories_to_member_ids_map={
            PointsCategory.to_enum(pc): body.point_categories_to_member_ids_map[pc]
            for pc in body.point_categories_to_member_ids_map
        },
        submitted_by=body.submitted_by,
        submission_channel=SubmissionsChannel.to_enum(body.submission_channel),
        is_static=body.is_static,
        is_fc_pf=body.is_fc_pf,
        fflogs_url=body.fflogs_url,
        fc_pf_id=body.fc_pf_id,
        auto_approve_admin_id=body.auto_approve_admin_id,
        notes=body.notes
    )


@app.get("/ppts")
def get_participation_points(member_id: int, tier: str):
    return DDB_CLIENT.get_member_points(member_id, tier)


@app.get("/ppts/leaderboard")
def get_participation_points_leaderboard(tier: str):
    return participation_points.get_points_leaderboard(tier)


@app.get("/ppts/table")
def get_participation_points_table():
    return [
        {
            'category_id': category.value,
            'name': category.name,
            'description': category.description,
            'constraints': category.constraints,
            'points': category.points
        }
        for category in PointsCategory
    ]


@app.get("/fc_roster")
def get_fc_roster():
    return fc_roster.get_fc_roster()
