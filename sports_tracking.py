"""
Brandon Zupan

Holds functions that deal with aquiring sports scores and generating a discord icon
"""

from PIL import Image, ImageFont, ImageDraw

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

icon_generator(45, 48)
