"""
Brandon Zupan

Holds functions that deal with aquiring sports scores and generating a discord icon
"""

import asyncio
import aiohttp
import bs4
from PIL import Image, ImageFont, ImageDraw

class Score():
    def __init__(self, game_id, is_home):
        self.game_id = game_id
        self.is_home = is_home
        self.longhorn_score = None
        self.enemy_score = None
        self.game_over = False

    async def fetch_score_html(self, session, id):
        """Updates the score from ESPN"""
        url = f'http://www.espn.com/college-football/game/_/gameId/{id}'
        async with session.get(url) as responce:
            return await responce.text()

    async def update_score(self):
        """Updates score from ESPN"""
        async with aiohttp.ClientSession() as session:
            html = await self.fetch_score_html(session, self.game_id)

        soup = bs4.BeautifulSoup(html, features='html.parser')

        homeScoreContainer = soup.findAll("div", {"class": "score icon-font-before"})
        awayScoreContainer = soup.findAll("div", {"class": "score icon-font-after"})

        if self.is_home == True:
            self.longhorn_score = homeScoreContainer[0].getText()
            self.enemy_score = awayScoreContainer[0].getText()
        else:
            self.longhorn_score = awayScoreContainer[0].getText()
            self.enemy_score = homeScoreContainer[0].getText()

def icon_generator(score1, score2):
    """
    Generates an icon for the discord server
    Inputs: 2 scores
    Output: Path to new icon
    """

    im = Image.open("icontemplate.png")
    draw = ImageDraw.Draw(im)

    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 150)

    #Longhorn score
    draw.text((260, 64), str(score1), (255,255,255), font=font)
    #Loser score
    draw.text((260, 264), str(score2), (255,255,255), font=font)
    im.save('sample-out.png')

    return 'sample-out.png'

async def main():
    red_river = Score(401012739, True)
    await red_river.update_score()
    print(f"Longhorn: {red_river.longhorn_score}, OU: {red_river.enemy_score}")

    icon_path = icon_generator(red_river.longhorn_score, red_river.enemy_score)
    print(icon_path)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())