import random
import click
from flask import Blueprint
from faker import Faker
from app import db
from app.models import Post,User

fake=Blueprint('fake',__name__)
faker = Faker()

@fake.cli.command()
@click.argument('num',type=int)
def users(num):
    """Create the given number of fake users"""
    users=[]
    for i in range(num):
        user = User(username=faker.user_name(), email=faker.email(),
                    about_me=faker.sentence())
        db.session.add(user)
        users.append(user)

    #create some followers as well
    for user in users:
        num_followers = random.randint(0,5)
        for i in range(num_followers):
            following=random.choice(users)
            if user != following:
                user.follow(following)

    db.session.commit()
    print(num,'users added. ')

@fake.cli.command()
@click.argument('num',type=int)
def posts(num):
    """Create the given number of faked posts assigned to random users"""
    users = User.query.all()
    for i in range(num):
        user = random.choice(users)
        post = Post(text=faker.paragraph(),author=user,
                 timestamp=faker.date_time_this_year())
        db.session.add(post)
    db.session.commit()
    print(num,'posts added. ')
