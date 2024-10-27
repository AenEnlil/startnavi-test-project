from datetime import datetime

from app.custom_fields import PyObjectId
from app.database import get_comment_collection, get_statistic_collection
from app.comments.schemas import CommentCreateSchema, CommentStatisticSchema


def get_post_match_pipeline(post_id: PyObjectId) -> list:
    return [
        {"$match": {"post_id": post_id}}
    ]


def create_comment_in_db(post_id: PyObjectId, user_id: PyObjectId, data: dict):
    current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    data = CommentCreateSchema(**data, post_id=post_id, author_id=user_id).model_dump()
    data.update({'updated_at': current_time, 'created_at': current_time})
    result = get_comment_collection().insert_one(data)
    return result.inserted_id


def find_comment_by_id(comment_id: PyObjectId):
    return get_comment_collection().find_one({'_id': comment_id})


def update_comment(comment_id: PyObjectId, data: dict):
    data.update({'updated_at': datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")})
    get_comment_collection().update_one({'_id': comment_id}, {'$set': data})
    return comment_id


def delete_comment_in_db(comment_id: PyObjectId):
    result = get_comment_collection().delete_one({'_id': comment_id})
    return bool(result.deleted_count)


def update_comments_statistics(increase_blocked_comments: bool = False,
                               increase_created_comments: bool = False) -> None:
    current_date = datetime.utcnow().date().strftime("%Y-%m-%d")
    existing_statistics = get_statistic_collection().find_one({'date': current_date})

    data = existing_statistics if existing_statistics else {'date': current_date}
    data = CommentStatisticSchema(**data).model_dump()

    if increase_blocked_comments:
        data['blocked_comments'] += 1
    elif increase_created_comments:
        data['created_comments'] += 1
    get_statistic_collection().update_one({'date': current_date}, {'$set': data}, upsert=True)
