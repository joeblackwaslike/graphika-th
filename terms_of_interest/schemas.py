from datetime import datetime

import ujson
from pydantic import BaseModel, validator


class Tweet(BaseModel):
    class Config:
        allow_mutation = False
        json_loads = ujson.loads

    # String containing the text of the Tweet
    text: str

    # String representing Twitter’s ID for the user who created this tweet
    node_id: str

    # String representing Twitter’s ID for the tweet
    message_id: str

    # String representing the time the tweet was published
    message_time: datetime

    @validator("message_time", pre=True)
    def parse_timestamp(cls, v):
        return datetime.strptime(v, "%a %b %d %H:%M:%S %z %Y")
