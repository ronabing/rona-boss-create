import os
import discord
from dotenv import load_dotenv
from discord.ext import commands, tasks
from datetime import datetime, time
from zoneinfo import ZoneInfo

# 개발자 센터 코드에서 봇 토큰 받아오기
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

DAYS_KR = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]

# 2. 매일 한국 시간 새벽 04:00 실행
@tasks.loop(time=time(hour=5, minute=24, second=0, tzinfo=KST))
async def daily_raid_setup():
    now = datetime.now(KST)
    today = now.strftime("%Y-%m-%d")
    weekday = DAYS_KR[now.weekday()] # 요일 가져오기
    
    
    # [작업 1] 일반 레이드 채널 스레드 관리
    raid_channel = bot.get_channel(RAID_CHANNEL_ID)
    if raid_channel:
        print("🧹 레이드 채널 스레드 청소 중...")
        for thread in raid_channel.threads:
            await thread.delete()
        async for thread in raid_channel.archived_threads(limit=50):
            await thread.delete()

        thread_name = f"[{today}] [{weekday}] [혼테일] 10~24시"
        thread_content = "오전 10시 ~ 오후 24시, 직업/가능한 시간대 작성 해주세요."

        if isinstance(raid_channel, discord.ForumChannel):
            await raid_channel.create_thread(
                name=thread_name,
                content=thread_content,
                auto_archive_duration=1440
            )
        else:
            msg = await raid_channel.send(f"📌 **{thread_name}**\n{thread_content}")
            await msg.create_thread(
                name=thread_name,
                auto_archive_duration=1440
            )
            
        print(f"✅ 혼테일 스레드 생성 완료 ({today} {weekday})")

    # [작업 2] 마발(시간협의) 채널 스레드 관리
    #special_channel = bot.get_channel(SPECIAL_CHANNEL_ID)
    #if special_channel:
    #    print("🧹 마발 채널 스레드 청소 중...")
    #    for thread in special_channel.threads:
    #        await thread.delete()
    #    async for thread in special_channel.archived_threads(limit=50):
    #        await thread.delete()

    #    if isinstance(special_channel, discord.ForumChannel):
            # 1. 기존 마발 스레드 생성
    #        await special_channel.create_thread(
    #            name=f"[{today}] [마왕 발록] 23시 이후",
    #            content="직업을 적어주세요",
    #            auto_archive_duration=1440
    #       )
            # 2. 핑크빈 스레드 생성
    #        await special_channel.create_thread(
    #            name=f"[{today}] [핑크빈] 시간 협의",
    #            content="직업, 스공, 지참할 버프 캐릭을 작성 해주세요",
    #            auto_archive_duration=1440
    #        )
            # 3. 심연의 자쿰 (신규)
    #        for i in range(1, 5):
    #            await special_channel.create_thread(
    #                name=f"[{today}] [심연의 자쿰] {i}파티 시간 협의",
    #                content="직업과 스공, 보맥을 적어주세요.",
    #                auto_archive_duration=1440
    #            )
            # 4. 심연의 혼테일 (신규)
    #        await special_channel.create_thread(
    #            name=f"[{today}] [심연의 혼테일] 시간 협의",
    #            content="직업과 스공, 보맥을 적어주세요.",
    #            auto_archive_duration=1440
    #       )
    #    else:
            # 1. 기존 마발 스레드 생성
    #        msg1 = await special_channel.send(f"📌 **[{today}] 23시 이후 마발**\n직업을 적어주세요")
    #        await msg1.create_thread(
    #            name=f"[{today}] [마왕 발록] 23시 이후",
    #            auto_archive_duration=1440
    #        )
            # 2. 핑크빈 스레드 생성
    #        msg2 = await special_channel.send(f"📌 **[{today}] [핑크빈] 시간 협의**\n직업, 스공, 지참할 버프 캐릭을 작성 해주세요")
    #        await msg2.create_thread(
    #            name=f"[{today}] [핑크빈] 시간 협의",
    #            auto_archive_duration=1440
    #        )
            # 3. 심연의 자쿰 (신규)
    #        for i in range(1, 5):
    #            msg3 = await special_channel.send(f"📌 **[{today}] [심연의 자쿰] {i}파티 시간 협의**\n직업과 스공, 보맥을 적어주세요.")
    #            await msg3.create_thread(name=f"[{today}] [심연의 자쿰] {i}파티 시간 협의", auto_archive_duration=1440)
            # 4. 심연의 혼테일 (신규)
    #        msg4 = await special_channel.send(f"📌 **[{today}] [심연의 혼테일] 시간 협의**\n직업과 스공, 보맥을 적어주세요.")
    #        await msg4.create_thread(
    #            name=f"[{today}] [심연의 혼테일] 시간 협의",
    #            auto_archive_duration=1440
    #        )
            
    #    print(f"✅ 상위보스 스레드 4개 생성 완료 ({today})")

@bot.event
async def on_ready():
    print(f'🤖 봇 로그인 성공: {bot.user.name}')
    if not daily_raid_setup.is_running():
        daily_raid_setup.start()

bot.run(os.environ.get('BOT_TOKEN'))
