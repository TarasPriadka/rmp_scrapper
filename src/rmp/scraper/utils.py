from lxml import html

from rmp.utils.general import isfloat
from rmp.models.models import Teacher


# ------------------------ Url Parser -------------------------

def reconstruct_url(in_url):
    start = in_url.find('q=') + 2
    end = in_url.find('&')

    clean_url = in_url[start:end]

    splits = clean_url.split('%')  # split weird symbols
    splits[1:] = [s[2:] for s in splits[1:]]  # remove junk values

    url = '='.join(splits[1:])  # join correct arguments
    url = '?'.join([splits[0], url])  # add argument to url

    return url


def create_rmp_url(name, school_sid):
    # https://www.ratemyprofessors.com/search.jsp?query=julie+wilson+de+anza
    name = '+'.join(name.lower().split(' '))
    return f"https://www.ratemyprofessors.com/search.jsp?query={name}&sid={school_sid}"


def create_url(name, school):
    name = name.lower()
    school = school.lower()
    args = name.split(' ') + school.split(' ') + ['rate', 'my', 'professor']
    return f"https://www.google.com/search?client=firefox-b-1-d&q={'+'.join(args)}"

# ------------------------ Review Parse -------------------------


def parse_header(response):
    header = {}
    name_line = response.xpath(
        "//div[contains(@class,'Wrapper')]/div[1]/div[1]/div[2]//text()").getall()
    header['last'] = name_line[0]
    header['first'] = name_line[2]
    header['department'] = name_line[5]
    header['college'] = name_line[-1]

    avggrade_line = response.xpath(
        "//div[contains(@class,'Wrapper')]/div[1]/div[1]/div[1]//text()").getall()
    header['avggrade'] = float(
        avggrade_line[0]) if isfloat(
        avggrade_line[0]) else float('nan')
    header['total_ratings'] = int(
        avggrade_line[5]) if 'No ratings yet.' not in avggrade_line else 0

    stats_line = response.xpath(
        "//div[contains(@class,'Wrapper')]/div[1]/div[1]/div[3]//text()").getall()

    if 'Would take again' in stats_line:
        # used to find index of wta or difficulty in case one is missing
        i = stats_line.index('Would take again') - 1
        header['would_take_again'] = stats_line[i]
    else:
        header['would_take_again'] = float('nan')

    if 'Level of Difficulty' in stats_line:
        # used to find index of wta or difficulty in case one is missing
        i = stats_line.index('Level of Difficulty') - 1
        header['difficulty'] = stats_line[i]
    else:
        header['difficulty'] = float('nan')

    tags_line = response.xpath(
        "//div[contains(@class,'Wrapper')]/div[1]/div[1]/div[5]//text()").getall()
    header['tags'] = tags_line[3:] if len(tags_line) > 4 else []

    most_helpful_line = response.xpath(
        "//div[contains(@class,'Wrapper')]/div[1]/div[2]/div[1]//text()").getall()

    header['most_helpful_line'] = {}
    if 'Be the first to rate Professor ' not in most_helpful_line and 'Bummer, Professor ' not in most_helpful_line:
        header['most_helpful_line']['class'] = most_helpful_line[3]
        header['most_helpful_line']['date'] = most_helpful_line[4]
        header['most_helpful_line']['comment'] = most_helpful_line[5]
        header['most_helpful_line']['upvotes'] = int(most_helpful_line[7])
        header['most_helpful_line']['downvotes'] = int(most_helpful_line[9])

    return header


def parse_review_header(review):
    out = {}
    review = review.xpath("./div/div/div[3]/div[1]//text()")
    out['class_name'] = review[1]
    out['class_experience'] = review[3]
    out['review_date'] = review[4]
    return out


def parse_score(review):
    review = review.xpath("./div/div/div[2]/div//text()")
    return {'quality': float(review[1]), 'difficulty': float(review[3])}


def parse_info(review):
    out = {}
    review = review.xpath("./div/div/div[3]/div[2]//text()")
    for i in range(0, len(review), 3):
        out[review[i]] = review[i + 2]
    return out


def parse_comment(review):
    return review.xpath("./div/div/div[3]/div[3]//text()")[0]


def parse_labels(review):
    return review.xpath("./div//div[contains(@class,'Tags')]//text()")


def parse_footer(review):
    review = review.xpath("./div//div[contains(@class,'Footer')]//text()")
    return {
        'upvotes': review[1],
        'downvotes': review[3]}


def parse_reviews(response):
    review = response.xpath("//ul[contains(@id,'ratingsList')]").getall()

    if len(review) == 0:
        return []

    tree = html.fromstring(review[0])
    comments = tree.xpath("//li")
    reviews = []
    for comment in comments:
        try:
            review = {}
            review.update(parse_review_header(comment))
            review.update(parse_score(comment))
            review['extra_info'] = [f'{k}:{v}' for k, v in parse_info(comment).items()]
            review['comment'] = (parse_comment(comment))
            review['labels'] = parse_labels(comment)
            review.update(parse_footer(comment))
            reviews.append(review)
            
        except(IndexError):
            continue
    return reviews


def parse_teacher(response) -> Teacher:
    header = parse_header(response)

    teacher_info = []
    teacher_info.append(header['first'])
    teacher_info.append(header['last'])
    teacher_info.append(header['avggrade'])
    teacher_info.append(header['college'])
    teacher_info.append(header['department'])
    teacher_info.append(header['total_ratings'])
    teacher_info.append(header['would_take_again'])
    teacher_info.append(header['difficulty'])
    teacher_info.append({
        'tags': header['tags'],
        'most_helpful_line': header['most_helpful_line']
    })
    
    reviews = []

    for c in parse_reviews(response):
        reviews.append({
            'class_name': c['class_name'],
            'class_experience': c['class_experience'],
            'comment': c['comment'],
            'meta': {
                'review_date': c['review_date'],
                'quality': c['quality'],
                'difficulty': c['difficulty'],
                'extra_info': c['extra_info'],
                'labels': c['labels'],
                'upvotes': c['upvotes'],
                'downvotes': c['downvotes']}
        })

    teacher_info.append(reviews)
    
    return Teacher.parse_tuple(teacher_info)