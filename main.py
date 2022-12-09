import discord
from discord import app_commands
import requests
from bs4 import BeautifulSoup
import datetime
from datetime import datetime

TOKEN = 'TOKEN'
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(
    name="lookup",
    description="プレイヤー情報を取得します。"
)
@discord.app_commands.describe(
    name="ゲーム内プレイヤー名を入力してください。"
)
@discord.app_commands.guild_only()
async def hoge(ctx, name: str):
    await ctx.response.defer()
    try:
        if name == None:
            embed = discord.Embed(title="プレイヤー名が入力されてないよ！", color=0xff2600)
            embed.set_author(name="エラー")
            await ctx.followup.send(embed=embed)
        elif name == "":
            embed = discord.Embed(title="プレイヤー名が入力されてないよ！", color=0xff2600)
            embed.set_author(name="エラー")
            await ctx.followup.send(embed=embed)
        elif ' ' in name:
            embed = discord.Embed(title="プレイヤー名にスペースは使えないよ！", color=0xff2600)
            embed.set_author(name="エラー")
            await ctx.followup.send(embed=embed)
        else:
            url = "https://uniteapi.dev/jp/p/" + name
            print('---\nget: ' + url + '\ntime: ' + datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S'))
            
            # プレイヤー情報を取得
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # metaタグからプレイヤー名を取得 (存在しない場合はエラー)
            title = soup.find('meta', attrs={'property': 'og:title'})
            if title == None:
                embed = discord.Embed(title="プレイヤーが見つからないよ！", color=0xff2600)
                embed.set_author(name="エラー")
                await ctx.followup.send(embed=embed)
                return
            title = title.get('content')

            # 500エラーの場合はプレイヤーが存在しない
            if '500: Internal Server Error' in title:
                embed = discord.Embed(title="プレイヤーが見つからないよ！", color=0xff2600)
                embed.set_author(name="エラー")
                print('status: error')
                await ctx.followup.send(embed=embed)
                return
            else:

                # プレイヤー画像を取得
                profile_images = soup.find_all('img', attrs={'alt': 'Avatar frame'})
                out = []
                profile_image = None

                # 画像を取得
                for image in profile_images:
                    image = image.get('src')
                    test = ''
                    if '/_next' in image:
                        out.append(url_convert(image))

                profile_image = out[1]

                if profile_image == None:
                    embed = discord.Embed(title="プレイヤーが見つからないよ！", color=0xff2600)
                    embed.set_author(name="エラー")
                    print('status: error')            
                    await ctx.followup.send(embed=embed)
                    return
                
                # プレイヤー情報を取得
                id_tag = soup.find('p', attrs={'color': '#C3646F'})
                if id_tag == None:
                    embed = discord.Embed(title="プレイヤーが見つからないよ！", color=0xff2600)
                    embed.set_author(name="エラー")
                    print('status: error')
                    await ctx.followup.send(embed=embed)
                    return
                id = id_tag.get_text()

                fairplay = soup.find('text', attrs={'class': 'CircularProgressbar-text'}).get_text()
                lastonline_cache = soup.findAll('p', attrs={'color': '#C4C4C4'})
                lastonline = ''
                for lastonline in lastonline_cache:
                    if 'Last online' in lastonline.get_text():
                        lastonline = lastonline.get_text().replace('Last online', '最終ログイン').replace('about ', '約').replace('ago', '前').replace(' hours ', '時間').replace(' days ', '日').replace(' minutes ', '分').replace('over 1 year ', '1年以上').replace('over 2 year ', '2年以上').replace('over 3 year ', '3年以上')
                        break
                if lastonline == '':
                    lastonline = '最終ログイン: 今（オンライン）'
                rank = soup.find('p', attrs={'class': 'sc-7bda52f2-1 hlSKkP'})
                if rank == None:
                    rank = soup.find('p', class_='sc-7bda52f2-3 djXNxQ').get_text().replace('・クラス', '')
                else:
                    rank = 'マスター (' + rank.get_text() + ')'
                
                texts = soup.find_all('p', attrs={'class': 'sc-7bda52f2-3 djXNxQ'})

                battles = 0
                wins = 0
                winrate = 0

                for text in texts:
                    if 'バトル数' in text.get_text():
                        battles = text.next_element.next_element.next_element.get_text()
                    elif '勝利数' in text.get_text():
                        wins = text.next_element.next_element.next_element.get_text()
                    elif '勝率' in text.get_text():
                        winrate = text.next_element.next_element.next_element.get_text().replace('\n', '').replace(' ', '') + '%'

                texts2 = soup.find_all('p')
                
                # mvp by xpath
                mvp = 0
                score = 0
                battles_rank = 0
                wins_rank = 0
                streak = 0
                all_kos = 0
                for text in texts2:
                    if 'MVP' in text.get_text() and mvp == 0:
                        mvp = text.next_element.next_element.next_element.get_text()
                    elif 'スコア' in text.get_text() and score == 0:
                        print('score:', text.next_element.next_element.next_element.get_text())
                        score = text.next_element.next_element.next_element.get_text()
                    elif 'バトル数' in text.get_text() and battles_rank == 0:
                        battles_rank = text.next_element.next_element.next_element.get_text()
                    elif '勝利数' in text.get_text() and wins_rank == 0:
                        wins_rank = text.next_element.next_element.next_element.get_text()
                    elif '連勝記録' in text.get_text() and streak == 0:
                        streak = text.next_element.next_element.next_element.get_text()
                    elif '総KO数' in text.get_text() and all_kos == 0:
                        all_kos = text.next_element.next_element.next_element.get_text()
                
                # embed
                embed=discord.Embed(title=name + ' (内部ID ' + id + ')', description=lastonline, color=discord.Colour.green())
                embed.set_author(name="ポケモンユナイトステータス", icon_url="https://www.pokemonunite.jp/assets/img/common/icon-unite_app.jpg")
                embed.set_thumbnail(url=profile_image)
                if battles == None: battles = '0'
                if wins == None: wins = '0'
                if winrate == None: winrate = '0'
                if fairplay == None: fairplay = '0'
                if rank == None: rank = '取得できませんでした'
                embed.add_field(name="プレイ数 (全体)", value=battles, inline=True)
                embed.add_field(name="勝利数 (勝率)", value=wins + ' / ' + winrate, inline=True)
                embed.add_field(name="フェアプレイ", value=fairplay, inline=True)
                embed.add_field(name="ランク", value=rank, inline=False)
                #embed.add_field(name="プレイ回数 (ランク)", value=battles_rank, inline=True)
                #embed.add_field(name="勝利数 (ランク)", value=wins_rank, inline=True)
                #embed.add_field(name="累計スコア (ランク)", value=score, inline=True)
                #embed.add_field(name="連勝記録 (ランク)", value=streak, inline=True)
                #embed.add_field(name="MVP数 (ランク)", value=mvp, inline=True)
                #embed.add_field(name="累計KO数 (ランク)", value=all_kos, inline=True)
                embed.set_image(url="https://www.pokemonunite.jp/PostImages/5fa062047610e1bb10da40475471a2e7f3b4d187.png")
                print('status: success')
                await ctx.followup.send(embed=embed)
    except Exception as e:
        print(e)
        embed = discord.Embed(title='不明なエラーが発生しました。', description='管理者へ連絡してください。', color=0xff2600)
        embed.set_author(name="エラー")
        print('status: error')
        await ctx.followup.send(embed=embed)
        return

def url_convert(url):
    return 'https://uniteapi.dev' + url

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game(name="/lookupでプレイヤーを検索！"))
    await tree.sync()

client.run(TOKEN)
