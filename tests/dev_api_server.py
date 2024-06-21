# stdlib
import logging

# 3rd-party
from fastapi import FastAPI

# Local
from acrossfc.api import submissions
from acrossfc.api import participation_points

LOG_FORMAT = (
    "<TEST API> %(asctime)s.%(msecs)03d [%(levelname)s] %(filename)s:%(lineno)d: %(message)s"
)

if len(logging.getLogger().handlers) == 0:
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    LOG = logging.getLogger(__name__)
else:
    LOG = logging.getLogger()

app = FastAPI()


@app.get("/submissions")
def get_submissions(tier: str):
    subs = submissions.get_submissions_for_tier(tier)
    return subs


@app.get("/submissions/{uuid}")
def get_submission_by_id(uuid: str):
    sub = submissions.get_submissions_by_uuid(uuid)
    return sub


@app.get("/submissions_queue")
def get_submissions_queue():
    queue = submissions.get_submissions_queue()
    return queue


@app.get("/current_submissions_tier")
def get_current_submissions_tier():
    return submissions.get_current_submissions_tier()


@app.get("/participation_points/{member_id}")
def get_participation_points(member_id: int, tier: str):
    return participation_points.get_points_for_member(member_id, tier)
