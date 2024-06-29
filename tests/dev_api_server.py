# stdlib
import traceback
from typing import Optional, Dict, Union

# 3rd-party
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Local
from acrossfc.api import submissions, participation_points, fc_roster
from acrossfc.core.config import FC_CONFIG
from acrossfc.core.model import PointsCategory, SubmissionsChannel
from acrossfc.ext.ddb_client import DDB_CLIENT


origins = [
    "http://localhost:3000",
]

app = FastAPI(debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/current_tier")
def get_current_submissions_tier():
    return submissions.get_current_submissions_tier()


@app.get("/submissions")
def get_submissions(tier: str = FC_CONFIG.current_submissions_tier):
    subs = submissions.get_submissions_for_tier(tier)
    return subs


@app.get("/submissions/queue")
def get_submissions_queue():
    queue = submissions.get_submissions_queue()
    return queue


@app.get("/submissions/{uuid}")
def get_submission_by_id(uuid: str):
    sub = DDB_CLIENT.get_submission_by_uuid(uuid)
    return sub


class SubmitFFLogsBody(BaseModel):
    fflogs_url: str
    submitted_by: submissions.ComboUserID
    submission_channel: Union[int, str]
    is_static: bool
    is_fc_pf: bool
    fc_pf_id: Optional[str] = None
    notes: Optional[str] = None
    eval_mode: bool = False


@app.post("/submissions/fflogs")
def submit_fflogs(body: SubmitFFLogsBody):
    try:
        return submissions.submit_fflogs(
            fflogs_url=body.fflogs_url,
            submitted_by=body.submitted_by,
            submission_channel=SubmissionsChannel.to_enum(body.submission_channel),
            is_fc_pf=body.is_fc_pf,
            is_static=body.is_static,
            fc_pf_id=body.fc_pf_id,
            notes=body.notes,
            eval_mode=body.eval_mode
        )
    except Exception as e:
        print(e)
        traceback.print_exc()


class ReviewSubmissionBody(BaseModel):
    submission: Dict


@app.post("/submissions/review")
def review_submission(body: ReviewSubmissionBody):
    try:
        return submissions.review_submission(body.submission)
    except Exception as e:
        print(e)
        traceback.print_exc()


@app.get("/ppts")
def get_participation_points(member_id: int, tier: str):
    return DDB_CLIENT.get_member_points(member_id, tier)


@app.get("/ppts/leaderboard")
def get_participation_points_leaderboard(tier: str = FC_CONFIG.current_submissions_tier):
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
