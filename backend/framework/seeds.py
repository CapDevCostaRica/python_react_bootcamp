from database import get_session
from models import MotivationalPhrase

phrases = [
    "Believe in yourself!",
    "Stay positive, work hard, make it happen.",
    "Your limitation—it’s only your imagination.",
    "Push yourself, because no one else is going to do it for you.",
    "Great things never come from comfort zones.",
    "Dream it. Wish it. Do it.",
    "Success doesn’t just find you. You have to go out and get it.",
    "The harder you work for something, the greater you’ll feel when you achieve it.",
    "Don’t stop when you’re tired. Stop when you’re done.",
    "Wake up with determination. Go to bed with satisfaction.",
]


def seed_motivational_phrases(session):
    for phrase in phrases:
        session.add(MotivationalPhrase(phrase=phrase))

    session.commit()
    session.close()

    print("Seeded motivational phrases.")


if __name__ == "__main__":
    session = get_session()
    seed_motivational_phrases(session)
    session.close()
