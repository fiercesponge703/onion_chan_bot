import logging
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import random
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import httpx
# Конфигурация

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AnimeBot:
    def __init__(self):
        # Фразы для команд
        self.ban_phrases = [
            "Сенпай {user}, ты плохо себя вёл! 😾 Теперь будешь в бане на {time} минут!",
            "Упс-тян! {user} нарушил правила~ 🌸 Бан-молот активирован! 🔨",
            "Ара-ара, {user}-кун, похоже ты заслужил наказание от няши! 🎀",
            "Бан-данго для {user}! 🍡 Съешь это и подумай о своём поведении!",
                "Онион-тян запрещает {user} приближаться к ней... на расстояние ножа! 🔪🌸",
    "Бан-хаммер активирован! {user} теперь будет висеть на холодильнике... в виде кусочков~ 🥰",
    "{user} получает бан... и несколько ножевых ранений от Онион-тян! 💝",
    "Ара-ара~ {user} заперт в подвале Онион-тян на {time} минут! Как мило! 😊",
    "Бан-данго! {user} теперь украшение для торта Онион-тян~ 🍡🔪"
        ]
        
        self.hug_phrases = [
            "Онион-тян обнимает {user2}! 🤗🌸",
            "Тысяча объятий для {user2} от Онион-тян! 💮",
            "Онион-тян нежно прижимает {user2} к груди~ 💕",
            "Они-тян расчленяет {user2} на милые кусочки :D",
                "Они-тян нежно душит {user2} в объятиях~ 💕 *хруст*",
    "Онион-тян обнимает {user2} так сильно, что слышен треск рёбер! 🤗💢",
    "Онион-тян прижимает {user2} к груди, не обращая внимания на хрустящие звуки~ 🌸",
    "Обнимашки от Онион-тян! {user2} теперь не может дышать... как мило! 😊💉",
    "Онион-тян заключает {user2} в смертельные объятия! Ай-яй-яй, кажется что-то сломалось~ 🥰",
    "Кусь-обнимай! Онион-тян кусает {user2} за шею, откусывая артерию 💋🩸",
    "Онион-тян дарит {user2} объятия... и несколько переломов~ 💖✂️"
        ]
        
        self.pat_phrases = [
            "Они-тян гладит {user2} по головке~ 🥺👉👈",
            "М-мяу! {user2} получает поглаживания от Онион-тян! 🐾",
            "Онион-тян нежно треплет {user2} за ушко ✨",
            "Они-тян придушает {user2} стальным тросом <3",
                "Они-тян гладит {user2} по головке... своей окровавленной рукой~ ✨🩸",
    "Поглаживания от Онион-тян! {user2} теперь навсегда её собственность~ 😼💕",
    "Они-тян нежно треплет {user2} за ушко... пока оно не отрывается~ 🥺👉👈",
    "Онион-тян ласкает {user2} ножом по щеке... ну почти как поглаживание! 🔪🌸",
    "Они-тян мило погладил {user2}... по внутренностям! 💮🫀",
    "М-мяу! Они-тян оставляет кровавые следы-лапки на {user2}~ 🐾💉",
    "Они-тян гладит {user2} по спине... тому, что от нее осталось~ 💝"
        ]
        
        self.nya_phrases = [
            "Ня-ня-ня~ 🌸",
            "Мяу! 😼",
            "Ня~~~~~ 💕",
            "Ку-ку! 🎀",
                "Ня-кровавое утро! 💝🔪",
    "Мяу-у-у... *капает кровь* 😼",
    "Ня~~~~~ *звуки рвущейся плоти* 💕",
    "Кусь-ня! 💋🩸",
    "Онион-тян някает в вашу сторону... бегите. 🥰",
    "Няяя! *звук ломающихся костей* 🌸",
    "Мяу... ฅ^•ﻌ•^ฅ *подмигивает, держа окровавленный нож*"
        ]
        
        self.reminders = [
            "Ня-помни! 💮 Пора делать ежедневные задания!",
            "Сенпай, не забудь про ежедневки! 🌸"
        ]

    def get_phrase(self, phrases, **kwargs):
        return random.choice(phrases).format(**kwargs)


class ArtFinder:
    @staticmethod
    async def search_art(query: str):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.unsplash.com/search/photos",
                    params={
                        "query": query,
                        "client_id": UNSPLASH_API_KEY,
                        "per_page": 20
                    }
                )
                data = response.json()
                
                if not data.get('results'):
                    return None
                
                image = random.choice(data['results'])
                return {
                    "url": image['urls']['regular'],
                    "author": image['user']['name'],
                    "link": image['links']['html']
                }
        except Exception as e:
            logger.error(f"Ошибка поиска арта: {e}")
            return None

# Инициализация компонентов
bot = Bot(token=BOT_TOKEN)
anime_girl = AnimeBot()
scheduler = BackgroundScheduler(timezone='Europe/Moscow')

# ===== КОМАНДЫ БОТА =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ня-привет! Я твоя аниме-помощница! 🌸\n"
                                  "Доступные команды:\n"
                                  "/ban - шуточный бан\n"
                                  "/hug - обнять\n"
                                  "/pat - погладить\n"
                                  "/nya - някать\n"
                                  "/roll - случайное число\n"
                                  "/coin - подбросить монетку\n"
                                  "/animefact - случайный факт об аниме\n"
                                  "/art <тема> - поиск рандомного арта")

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message.reply_to_message:
            await update.message.reply_text("Ня-ня! Нужно ответить на сообщение пользователя! 🌸")
            return
            
        user = update.message.reply_to_message.from_user
        username = f"@{user.username}" if user.username else user.full_name
        message = anime_girl.get_phrase(
            anime_girl.ban_phrases,
            user=username,
            time=random.randint(5, 1440)
        )
        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Ошибка в ban_command: {e}")

async def hug_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message.reply_to_message:
            await update.message.reply_text("Нужно ответить на сообщение того, кого хочешь обнять!")
            return
            
        user1 = update.message.from_user
        user2 = update.message.reply_to_message.from_user
        name1 = f"@{user1.username}" if user1.username else user1.full_name
        name2 = f"@{user2.username}" if user2.username else user2.full_name
        
        message = anime_girl.get_phrase(
            anime_girl.hug_phrases,
            user1=name1,
            user2=name2
        )
        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Ошибка в hug_command: {e}")

async def pat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message.reply_to_message:
            await update.message.reply_text("Ответь на сообщение того, кого хочешь погладить!")
            return
            
        user1 = update.message.from_user
        user2 = update.message.reply_to_message.from_user
        name1 = f"@{user1.username}" if user1.username else user1.full_name
        name2 = f"@{user2.username}" if user2.username else user2.full_name
        
        message = anime_girl.get_phrase(
            anime_girl.pat_phrases,
            user1=name1,
            user2=name2
        )
        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Ошибка в pat_command: {e}")

async def nya_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = anime_girl.get_phrase(anime_girl.nya_phrases)
        await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Ошибка в nya_command: {e}")

async def roll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        num = random.randint(1, 100)
        await update.message.reply_text(f"🎲 Сенпай выбросил {num}!")
    except Exception as e:
        logger.error(f"Ошибка в roll_command: {e}")

async def coin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        result = random.choice(["Орёл", "Решка"])
        await update.message.reply_text(f"🪙 Монетка показывает... {result}!")
    except Exception as e:
        logger.error(f"Ошибка в coin_command: {e}")

async def animefact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        facts = [
            "Первый аниме-сериал вышел в 1963 году - это был 'Tetsuwan Atom' (Astro Boy)!",
            "Studio Ghibli была основана Хаяо Миядзаки в 1985 году",
            "Самый длинный аниме-сериал - 'Sazae-san' (более 2500 эпизодов!)",
            "В Японии аниме составляет около 60% всего телевизионного контента",
                "Знаете ли вы, что в Японии есть кафе, где официантки кусают клиентов? Как мило!",
    "Факт: Первый аниме-персонаж умер от потери крови... шучу! Или нет? 🌸",
    "В аниме 'Another' школьники умирают от... обычных несчастных случаев. Как романтично!",
    "Факт: У Онион-тян есть коллекция из 57 ножей. Для готовки! Конечно для готовки...",
    "Знаете ли вы? Кровь в старых аниме была черной из-за цензуры. Как скучно!",
    "Факт: В Японии есть настоящие 'кошачьи кафе'. Надеюсь, они не как у Онион-тян...",
    "Самый кровавый аниме-сериал - 'Corpse Party'. Рекомендую для семейного просмотра!"
        ]
        fact = random.choice(facts)
        await update.message.reply_text(f"📚 Аниме-факт: {fact}")
    except Exception as e:
        logger.error(f"Ошибка в animefact_command: {e}")

# ===== АВТОМАТИЧЕСКИЕ ФУНКЦИИ =====
async def send_daily_reminder():
    try:
        message = anime_girl.get_phrase(anime_girl.reminders)
        await bot.send_message(chat_id=GROUP_CHAT_ID, text=message)
    except Exception as e:
        logger.error(f"Ошибка ежедневного напоминания: {e}")

async def send_weekly_reminder():
    try:
        await bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text="🌸✨ Ня-внимание! Пора пройти Виртуальную Вселенную и еженедельных боссов! 🎮⚔️"
        )
    except Exception as e:
        logger.error(f"Ошибка еженедельного напоминания: {e}")


async def art_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("Укажите тему для поиска!\nПример: /art cyberpunk city")
            return

        query = " ".join(context.args)
        art_data = await ArtFinder.search_art(query)
        
        if not art_data:
            await update.message.reply_text("Арты не найдены 😿 Попробуйте другой запрос!")
            return

        caption = f"🎨 {query.capitalize()}\nАвтор: {art_data['author']}\nИсточник: {art_data['link']}"
        await update.message.reply_photo(
            photo=art_data['url'],
            caption=caption
        )
    except Exception as e:
        logger.error(f"Ошибка в art_command: {e}")
        await update.message.reply_text("Что-то пошло не так! 😿")

# ===== НАСТРОЙКА =====
def setup_scheduler():
    scheduler.add_job(
        send_daily_reminder,
        trigger=CronTrigger(hour=19, minute=0),
        id="daily_reminder"
    )
    
    scheduler.add_job(
        send_weekly_reminder,
        trigger=CronTrigger(day_of_week="sun", hour=12),
        id="weekly_reminder"
    )
    scheduler.start()

async def post_init(application: Application):
    await bot.initialize()

def main():
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    # Регистрация команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("hug", hug_command))
    application.add_handler(CommandHandler("pat", pat_command))
    application.add_handler(CommandHandler("nya", nya_command))
    application.add_handler(CommandHandler("roll", roll_command))
    application.add_handler(CommandHandler("coin", coin_command))
    application.add_handler(CommandHandler("animefact", animefact_command))
    application.add_handler(CommandHandler("art", art_command))
    # Настройка планировщика
    setup_scheduler()

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
