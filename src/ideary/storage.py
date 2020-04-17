from typing import Optional

import bson
from pymongo import MongoClient

from src.ideary import read_conf
from src.ideary.diary import Diary, DiaryEntry

db = MongoClient('mongodb://%(usr)s:%(pw)s@%(host)s' % read_conf()['mongodb'], ssl=True, connect=False)


def read_diary(**kwargs):
    doc = db.ideary.diary.find_one(kwargs)
    if doc is None:
        return None
    return Diary(**doc)


def write_diary(diary: Diary):
    db.ideary.diary.update_one(
        filter=dict(diary_id=diary.diary_id),
        update={"$set": diary.__dict__},
        upsert=True
    )


def get_user_diary(user_id) -> Diary:
    user_id = int(user_id)
    return read_diary(user_id=user_id) or Diary(diary_id=user_id, user_id=user_id)


def write_entry(entry: DiaryEntry, diary_id):
    return db.ideary.diary_entry.update_one(
        filter=dict(diary_id=diary_id, number=entry.number),
        update={"$set": entry.storage_state()},
        upsert=True
    )


def get_latest_entry(dairy_id):
    try:
        doc = db.ideary.diary_entry \
            .find(dict(diary_id=dairy_id)) \
            .sort("number", direction=-1) \
            .limit(1) \
            .next()
        return DiaryEntry(**doc)
    except StopIteration:
        return None


def read_entry(**kwargs):
    doc = db.ideary.diary_entry.find_one(kwargs)
    if doc is None:
        return None
    return DiaryEntry(**doc)


def store_image(file_id:str, file_name:str, user_id:int, content_type:str, content:Optional[bytearray]=None):
    update = dict(
        user_id=user_id,
        file_name=file_name,
        content=bson.binary.Binary(content) if content else None,
        content_type=content_type
    )
    db.ideary.media.update_one(
        filter=dict(file_id=file_id),
        update={"$set": update},
        upsert=True
    )

def read_image(**kwargs):
    return db.ideary.media.find_one(kwargs)


if __name__ == '__main__':
    diary = get_user_diary(0)
    write_diary(diary)
