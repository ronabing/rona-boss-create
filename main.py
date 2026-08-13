import os
import discord
from dotenv import load_dotenv
from discord.ext import commands, tasks
from datetime import datetime, time
from zoneinfo import ZoneInfo

load_dotenv()

# 1. 한국 시간대(KST) 및 권한 설정
KST = ZoneInfo("Asia/Seoul")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ⚙️ 채널 ID 설정 (본인의 실제 디스코드 채널 ID 숫자로 수정 필수!)
RAID_CHANNEL_ID = 1528345421548752957    # 시간대별 레이드 채널 ID
SPECIAL_CHANNEL_ID = 1528346781048635393 # 마발(시간협의) 채널 ID

TIME_SLOTS = ["20:00", "21:00", "22:00", "23:00", "24:00"]

# 2. 매일 한국 시간 오전 07:00 실행
@tasks.loop(time=time(hour=7, minute=0, second=0, tzinfo=KST))
async def daily_raid_setup():
    today = datetime.now(KST).strftime("%Y-%m-%d")
    
    # [작업 1] 일반 레이드 채널 스레드 관리
    raid_channel = bot.get_channel(RAID_CHANNEL_ID)
    if raid_channel:
        print("🧹 일반 레이드 채널 스레드 청소 중...")
        for thread in raid_channel.threads:
            await thread.delete()
        async for thread in raid_channel.archived_threads(limit=50):
            await thread.delete()

        if isinstance(raid_channel, discord.ForumChannel):
            for slot in TIME_SLOTS:
                await raid_channel.create_thread(
                    name=f"[{today}] {slot} 혼테일",
                    content="직업을 적어주세요",
                    auto_archive_duration=1440
                )
        else:
            for slot in TIME_SLOTS:
                msg = await raid_channel.send(f"📌 **[{slot}] 혼테일**\n직업을 적어주세요")
                await msg.create_thread(
                    name=f"[{today}] {slot} 혼테일",
                    auto_archive_duration=1440
                )
            
        print(f"✅ 일반 레이드 스레드 5개 생성 완료 ({today})")

    # [작업 2] 마발(시간협의) 채널 스레드 관리
    special_channel = bot.get_channel(SPECIAL_CHANNEL_ID)
    if special_channel:
        print("🧹 마발 채널 스레드 청소 중...")
        for thread in special_channel.threads:
            await thread.delete()
        async for thread in special_channel.archived_threads(limit=50):
            await thread.delete()

        if isinstance(special_channel, discord.ForumChannel):
            await special_channel.create_thread(
                name=f"[{today}] 마발(시간협의)",
                content="직업을 적어주세요",
                auto_archive_duration=1440
            )
        else:
            msg = await special_channel.send(f"📌 **[{today}] 마발(시간협의)**\n직업을 적어주세요")
            await msg.create_thread(
                name=f"[{today}] 마발(시간협의)",
                auto_archive_duration=1440
            )
            
        print(f"✅ 마발(시간협의) 스레드 생성 완료 ({today})")

@bot.event
async def on_ready():
    print(f'🤖 봇 로그인 성공: {bot.user.name}')
    if not daily_raid_setup.is_running():
        daily_raid_setup.start()

bot.run(os.environ.get('BOT_TOKEN'))
