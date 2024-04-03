import asyncio
from celery import app
from asgiref.sync import async_to_sync
from main import bot
from config_data.config import EnvData
from db.models import Post, session
from lexicon.lexicon_ru import lexicon_ru


@app.shared_task
def hello_world():
    print('hello world')



async def public_posts(times_a_day: int):
    try:
        posts = session.query(Post).filter(Post.frequency == times_a_day, Post.allowed == True, Post.amount != 0).all()
        for post in posts:
            post_text = lexicon_ru['post_template'].format(post.header, post.desc, post.link)
            await bot.send_photo(
                chat_id=str(EnvData.main_chats[0]),
                caption=post_text,
                photo=post.photo_id
                )
            post.amount -= 1
            await asyncio.sleep(1)
        # session.query(Post).filter(Post.frequency == times_a_day, Post.allowed == True, Post.amount != 0).update({'amount': Post.amount - 1})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

@app.shared_task
def public_posts_task(times_a_day: int):
    asyncio.get_event_loop().run_until_complete(public_posts(times_a_day))
