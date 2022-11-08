import os
import urllib.request
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from textwrap import fill
from packages.RobloxAPI import getMembership

def createRobloxInfo(avImage: str, data: dict):
    robloxUserId = data["id"]
    robloxUsername = data["username"]
    robloxDisplayName = data["displayname"]
    robloxStatusType = data["pType"]

    #robloxUserDescription = data["description"]
    robloxUserCreationDate = data["created"]
    robloxUserCount = data["count"]

    print(fr"./assets/robloxImages/users/{robloxUserId}")
    if not os.path.exists(fr"./assets/robloxImages/users/{robloxUserId}"):
        os.makedirs(fr"./assets/robloxImages/users/{robloxUserId}")

    urllib.request.urlretrieve(avImage, fr"./assets/robloxImages/users/{robloxUserId}/avatar.png")
    avatar    = Image.open(fr"./assets/robloxImages/users/{robloxUserId}/avatar.png").convert("RGBA")
    newAvatar = Image.new("RGBA", avatar.size, "#111111")
    newAvatar.paste(avatar, (0, 0), avatar)

    # Create Information Image
    avatar    = newAvatar.convert('RGB')
    infoFrame = Image.open(fr"./assets/robloxImages/infoFrame.png")
    #descriptionFrame = Image.open(fr"./assets/robloxImages/descriptionFrame.png")
    premium   = Image.open(r"./assets/robloxImages/premium.png").resize((125, 125))

    avatar = avatar.resize((975, 975))
    infoFrame.paste(avatar, (50, 50))
    frame = ImageDraw.Draw(infoFrame)

    #description = ImageDraw.Draw(descriptionFrame)

    if getMembership(robloxUserId) == True:
        infoFrame.paste(premium, (2340, 50))

    if robloxStatusType == 0: status = (255, 255, 255)
    if robloxStatusType == 1: status = (75, 180, 240)
    if robloxStatusType == 2: status = (80, 240, 75)
    if robloxStatusType == 3: status = (235, 185, 90)

    #if len(robloxUserDescription) >= 1000:
    #    robloxUserDescription = "Cannot Display Description:\nDescription Exceeds more than 512 characters."

    frame.text((1060, 50), f"@{robloxUsername}", font=ImageFont.truetype(r'./assets/Virgil.ttf', 55), fill=status)
    frame.text((1060, 130), robloxDisplayName, font=ImageFont.truetype(r'./assets/Virgil.ttf', 120), fill=status)
    frame.text((1060, 260), f"Roblox ID: {robloxUserId}", font=ImageFont.truetype(r'./assets/Virgil.ttf', 55), fill=(255, 255, 255))
    
    frame.text((1060, 720), "Friends", font=ImageFont.truetype(r'./assets/Virgil.ttf', 65), fill=(255, 255, 255))
    frame.text((1560, 720), "Followers", font=ImageFont.truetype(r'./assets/Virgil.ttf', 65), fill=(255, 255, 255))
    frame.text((2060, 720), "Following", font=ImageFont.truetype(r'./assets/Virgil.ttf', 65), fill=(255, 255, 255))
    frame.text((1060, 800), f"{robloxUserCount[0]}/200", font=ImageFont.truetype(r'./assets/Virgil.ttf', 85), fill=(255, 255, 255))
    frame.text((1560, 800), f"{robloxUserCount[1]:,}", font=ImageFont.truetype(r'./assets/Virgil.ttf', 85), fill=(255, 255, 255))
    frame.text((2060, 800), f"{robloxUserCount[2]:,}", font=ImageFont.truetype(r'./assets/Virgil.ttf', 85), fill=(255, 255, 255))

    frame.text((1060, 935), robloxUserCreationDate, font=ImageFont.truetype(r'./assets/Virgil.ttf', 60), fill=(255, 255, 255))

    #description.text((50, 50), f"@{robloxUsername}'s Description", font=ImageFont.truetype(r'./assets/Virgil.ttf', 75), fill=(255, 255, 255))
    #description.text((50, 205), '\n'.join([fill(p, 94) for p in robloxUserDescription.splitlines()]), font=ImageFont.truetype(r'./assets/Virgil.ttf', 50), fill=(255, 255, 255))

    infoFrame.save(fr"./assets/robloxImages/users/{robloxUserId}/info.png")
    #descriptionFrame.save(fr"./assets/robloxImages/users/{robloxUserId}/desc.png")
    return robloxUserId