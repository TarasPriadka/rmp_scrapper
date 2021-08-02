"""Data containers for teachers and their reviews."""
import json

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ReviewMeta:
    """Dataclass for the metadata for the teacher reviews."""
    quality: float
    difficulty: float
    extra_info: List[str]  # "For Credit: Yes", "Would Take Again: No", etc.
    labels: List[str]  # "Accessible outside class" "EXTRA CREDIT"
    upvotes: int
    downvotes: int
    review_date: str


@dataclass
class Review:
    """Dataclass for teacher review."""
    class_name: str
    class_experience: str  # "great", "awful", etc.
    comment: str
    meta: ReviewMeta


@dataclass
class TeacherMeta:
    """Dataclass for teacher's metadata."""
    tags: List[str]
    most_helpful_line:dict

@dataclass
class Teacher:
    """Dataclass which contains all of the information about the teacher."""
    FIELDS = [
        ('first', 'str'),
        ('last', 'str'),
        ('avggrade', 'real'),
        ('college', 'str'),
        ('department', 'str'),
        ('total_ratings', 'int'),
        ('would_take_again', 'int'),
        ('difficulty', 'real'),
        ('meta', 'json'),
        ('reviews', 'json'),
    ]

    first: str
    last: str
    avggrade: float
    college: str
    department: str
    total_ratings: int
    would_take_again: float
    difficulty: float
    meta: TeacherMeta
    reviews: List[Review]  # student reviews

    def json_dump(self):
        teacher_dict = self.__dict__
        teacher_dict['meta'] = json.dumps(teacher_dict['meta'].__dict__)

        # need to make everything json-serializable
        def to_dict(review):
            review.meta = review.meta.__dict__
            return review

        teacher_dict['reviews'] = json.dumps(
            [review.__dict__ for review in map(to_dict, teacher_dict['reviews'])])
        teacher_tuple = tuple([teacher_dict[key] for key in teacher_dict])
        return teacher_tuple
    
    @staticmethod
    def parse_tuple(teacher_tuple:Tuple):
        """Parse teacher dict outputted by the scrapper."""
        print(teacher_tuple)
        first, last, avggrade, college, department, total_ratings, would_take_again, difficulty  = teacher_tuple[0:8]

        teacher_meta: TeacherMeta = TeacherMeta(**teacher_tuple[8])

        reviews: List[Review] = []
        for c in teacher_tuple[9]:
            class_name: str = c['class_name']
            # "great", "awful", etc.
            class_experience: str = c['class_experience']
            comment: str = c['comment']

            review_meta: ReviewMeta = ReviewMeta(**c['meta'])
            c = Review(class_name, class_experience, comment, review_meta)
            reviews.append(c)

        return Teacher(first, last, avggrade, college, department, total_ratings, would_take_again, difficulty, teacher_meta, reviews)
