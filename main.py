import discord
from discord.ext import commands
import datetime
import random
import blackjack as blj
import blackjack2p as blj2
from keep_alive import keep_alive

keep_alive()

# Biến để lưu lại ID của poll message
poll_rps_id = None
poll_bj_id = None
bj_msg = None
hit_counts = {}
active_duels = {}

playChoice = ["Kéo", "Búa", "Bao"]

commands_list = """
            **~list**        - Xem danh sách lệnh

            **~hello**         - Bot chào bạn

            **~goodnight**            - Bot chúc ngủ ngon

            **~time**          - Bot xem giờ giúp 

            **~rps**    - Bot chơi kéo búa bao

            **~bj**    - Bot chơi xì dách

            (và một vài tương tác ẩn khác sẽ đc update dần)
        """
intents = discord.Intents.default()
intents.message_content = True  # Nếu bạn muốn đọc nội dung tin nhắn
intents.voice_states = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='~', intents=intents)

class DuelGame():
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.turn = p1 
        self.hands = {
            p1.id: [blj2.draw(), blj2.draw()],
            p2.id: [blj2.draw(), blj2.draw()]
        }
        self.stood = []
        
class DuelView(discord.ui.View):
    def __init__(self, game):
        super().__init__(timeout=120)
        self.game = game
        self.message = None

    def get_embed(self):
        embed = discord.Embed(
        title=f"✨BLACK JACK PVP✨",
        description=(
                    f"### Game turn: {self.game.turn.mention}\n"
                     f"### {self.game.p1.mention}\n"
                     f"### {self.game.hands[self.game.p1.id]}\n"
                     f"### Score: {blj2.calScore(self.game.hands[self.game.p1.id])}\n"
                     f"### {self.game.p2.mention}\n"
                     f"### {self.game.hands[self.game.p2.id]}\n"
                     f"### Score: {blj2.calScore(self.game.hands[self.game.p2.id])}\n"),
        color=discord.Color.dark_blue())  

        return embed

    @discord.ui.button(
        emoji="🃏",
        style=discord.ButtonStyle.green
    )
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user.id != self.game.turn.id:
            await interaction.response.send_message(
                "Chưa tới lượt bạn!",
                ephemeral=True
            )
            return

        # Báo cho Discord biết mình sẽ xử lý
        await interaction.response.defer()

        # Bust

        if len(self.game.hands[interaction.user.id]) < 5:
            self.game.hands[interaction.user.id].append(blj2.draw())    
        else:    
            await interaction.followup.send(
                "Bạn không thể bốc hơn 5 lá được, bạn thật là tham lam 😓",
                ephemeral=True
                )

        score = blj2.calScore(self.game.hands[interaction.user.id])

        if score == "5 perfect cards":
            await interaction.followup.send(
                "Đù quá dữ 😲",
                ephemeral=True
                )
        elif score == "AA":
            await interaction.followup.send(
                "Điên thiệt chứ 😲",
                ephemeral=True
                )
        elif score > 21:
            embed = self.get_embed()
            await interaction.followup.send(
                "Quắc rồi gà vl 🤣🤣🤣",
                ephemeral=True
            )

            await interaction.edit_original_response(
                embed=embed,
                view=None
            )

        await interaction.edit_original_response(
            embed=self.get_embed(),
            view=self
        )

    @discord.ui.button(
        emoji="✋",
        style=discord.ButtonStyle.red
    )
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user.id != self.game.turn.id:
            await interaction.response.send_message(
                "Chưa tới lượt bạn!",
                ephemeral=True
            )
            return

        self.game.stood.append(interaction.user.id)

        # Nếu cả 2 đã stand → so điểm
        if len(self.game.stood) >= 2:

            p1_score = blj2.calScore(self.game.hands[self.game.p1.id])
            p2_score = blj2.calScore(self.game.hands[self.game.p2.id])

            if p1_score == p2_score:
                result = "🤝 Hòa!"
            elif p1_score == p2_score and p1_score == "5 perfect cards":
                result = "Đây là trận chiến của những kẻ mạnh sao 😲😲😲😲"
            elif p1_score == p2_score and p1_score == "AA":
                result = "VCL 2 con chó đỏ 🤬🤬🤬🤬"
            elif p1_score == "5 perfect cards":
                if p2_score == "AA":
                    result = f"🏆 {self.game.p2.mention} thắng!"
                else:
                    result = f"🏆 {self.game.p1.mention} thắng!"
            elif p2_score == "5 perfect cards":
                if p1_score == "AA":
                    result = f"🏆 {self.game.p1.mention} thắng!"
                else:
                    result = f"🏆 {self.game.p2.mention} thắng!"
            elif p1_score == "AA":
                result = f"🏆 {self.game.p1.mention} thắng!"
            elif p2_score == "AA":
                result = f"🏆 {self.game.p2.mention} thắng!"
            elif (16 <= p1_score <= 21) and (16 <= p2_score <= 21):
                if p1_score > p2_score:
                    result = f"🏆 {self.game.p1.mention} thắng!"
                else:
                    result = f"🏆 {self.game.p2.mention} thắng!"
            elif p1_score < 16 and (16 <= p2_score <= 21):
                result = f"🏆 {self.game.p2.mention} thắng!\n{self.game.p1.mention} không biết chơi 😓"
            elif p2_score < 16 and (16 <= p1_score <= 21):
                result = f"🏆 {self.game.p1.mention} thắng!\n{self.game.p2.mention} không biết chơi 😓"
            elif p2_score > 21 and (16 <= p1_score <= 21):
                result = f"🏆 {self.game.p1.mention} thắng!"
            elif p1_score > 21 and (16 <= p2_score <= 21):
                result = f"🏆 {self.game.p2.mention} thắng!"
            elif p1_score < 16 and p2_score < 16:
                result = f"2 đứa ngu này không biết chơi 😓"
            elif p1_score > 21 and p2_score > 21:
                result = f"2 đứa gà quắc hết 🤣🤣🤣"

            embed = self.get_embed()
            embed.add_field(name="Kết quả", value=result, inline=False)

            await interaction.response.edit_message(
                embed=embed,
                view=None
            )

            del active_duels[self.game.p1.id]
            del active_duels[self.game.p2.id]
            self.stop()
            return

        # Đổi lượt
        self.game.turn = (
            self.game.p2 if self.game.turn == self.game.p1
            else self.game.p1
        )

        await interaction.response.edit_message(
            embed=self.get_embed(),
            view=self
        )

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id not in [self.game.p1.id, self.game.p2.id]:
            await interaction.response.send_message(
                "Bạn không phải người chơi trận này!",
                ephemeral=True
            )
            return False
        return True

@bot.command()
async def duel(ctx, member: discord.Member):
    if member.bot:
        await ctx.send("Bro thật sự muốn bắt nạt bot hả 🤨")
        return
    
    if member == ctx.author:
        await ctx.send("Bro không có bạn sao 🤣🤣🤣🤣")
        return
    
    if ctx.author.id in active_duels:
        await ctx.send("Bro đang trong trận khác mà 😓")
        return

    if member.id in active_duels:
        await ctx.send("Bro muốn tham gia à, ít nhất cũng phải đợi người ta xong chứ đồ mất lịch sự😓")
        return
    
    await ctx.send(f"{member.mention} sợ à 😏\nVô mà múc nó đi bro 🤣")

    game = DuelGame(ctx.author, member)
    active_duels[ctx.author.id] = game
    active_duels[member.id] = game

    view = DuelView(game)

    embed = view.get_embed()

    msg = await ctx.send(embed=embed, view=view)

    view.message = msg

    if blj2.calScore(game.hands[game.p1.id]) > 21:
        await ctx.send(f"{ctx.author.mention} ngu quá hơn 21 rồi còn bốc 🤣")
    if blj2.calScore(game.hands[game.p2.id]) > 21:
        await ctx.send(f"{member.mention} ngu quá hơn 21 rồi còn bốc 🤣")
    
@bot.command()
async def huyduel(ctx, member:discord.Member):
    del active_duels[ctx.author.id]
    del active_duels[member.id]
    await ctx.send(f"Chưa đánh xong mà trốn rồi hả {ctx.author.mention} {member.mention}")

async def update_bj_embed(user):
    global bj_msg

    embed = discord.Embed(
        title=f"Welcome to Black Jack {user.mention}",
        description=(f"### {user.mention} Score: {blj.playerScore}\n"
                     f"### Your cards: {blj.playerCards}\n"
                     f"### Bot Score: {blj.botScore}\n"
                     f"### Bot Cards: {blj.botCards}\n"
                     "### ✅ to Hit\n"
                     "### ❎ to Stand\n"),
        color=discord.Color.dark_blue())
    await bj_msg.edit(embed=embed)

@bot.command()
async def list(ctx):
    embed = discord.Embed(title="📜 Lệnh hướng dẫn",
                          description=(commands_list),
                          color=discord.Color.dark_gray())
    await ctx.send(embed=embed)

@bot.command()
async def yn(ctx):
    answer = ["Yes", "Nah", "Right", "Nope"]
    await ctx.send(random.choice(answer))

@bot.command()
async def hello(ctx):
    await ctx.send(f'Chào đại ca {ctx.author.mention}!')

@bot.command()
async def goodnight(ctx):
    await ctx.send(f"{ctx.author.mention} Oyasuminasai")

@bot.command()
async def time(ctx):
    hour = datetime.datetime.now().hour
    min = datetime.datetime.now().minute

    await ctx.send(f"Bây giờ là {hour}:{min} nha {ctx.author.mention}")

@bot.command()
async def rps(ctx):

    global poll_rps_id

    embed = discord.Embed(title="Your choice bro 🤖",
                          description=("✌️ -> **Chọn Kéo** \n"
                                       "✊ -> **Chọn Búa** \n"
                                       "🤚 -> **Chọn Bao** \n"
                                       "🎲 -> **Chọn Ngẫu Nhiên** \n"),
                          color=discord.Color.dark_embed())

    msg = await ctx.send(embed=embed)
    poll_rps_id = msg.id

    emojis = ["✌️", "✊", "🤚", "🎲"]
    for emoji in emojis:
        await msg.add_reaction(emoji)

@bot.event
async def on_reaction_add(reaction, user):
    global poll_rps_id, poll_bj_id, bj_msg, hit_counts

    if user.bot:
        return

    emoji = str(reaction.emoji)
    channel = reaction.message.channel

    if reaction.message.id == poll_rps_id:

        if emoji == "✌️":
            await channel.send(f"{user.mention} đã chọn Kéo ✌️")
            botChoice = random.choice(playChoice)
            await channel.send(f"Bot chọn {botChoice} 🤖")

            if botChoice == "Kéo":
                await channel.send(f"We are draw, {user.mention} 😉")
            elif botChoice == "Búa":
                await channel.send(f"{user.mention} is a loser 🤣")
            else:
                await channel.send(f"You are so lucky bitch, {user.mention} 🤬 "
                                   )

        elif emoji == "✊":
            await channel.send(f"{user.mention} đã chọn Búa ✊")
            botChoice = random.choice(playChoice)
            await channel.send(f"Bot chọn {botChoice} 🤖")

            if botChoice == "Búa":
                await channel.send(f"We are draw, {user.mention} 😉")
            elif botChoice == "Bao":
                await channel.send(f"{user.mention} is a loser 🤣")
            else:
                await channel.send(f"You are so lucky bitch, {user.mention} 🤬 "
                                   )

        elif emoji == "🤚":
            await channel.send(f"{user.mention} đã chọn Bao 🤚")
            botChoice = random.choice(playChoice)
            await channel.send(f"Bot chọn {botChoice} 🤖")

            if botChoice == "Bao":
                await channel.send(f"We are draw, {user.mention} 😉")
            elif botChoice == "Kéo":
                await channel.send(f"{user.mention} is a loser 🤣")
            else:
                await channel.send(f"You are so lucky bitch, {user.mention} 🤬 "
                                   )

        elif emoji == "🎲":
            randomChoice = random.choice(playChoice)
            await channel.send(
                f"{user.mention} tung xúc xắc ra: **{randomChoice}** 🎲")
            botChoice = random.choice(playChoice)
            await channel.send(f"Bot chọn {botChoice} 🤖")

            if randomChoice == "Kéo":
                if botChoice == "Kéo":
                    await channel.send(f"We are draw, {user.mention} 😉")
                elif botChoice == "Búa":
                    await channel.send(f"{user.mention} is a loser 🤣")
                elif botChoice == "Bao":
                    await channel.send(
                        f"You are so lucky bitch, {user.mention} 🤬 ")

            if randomChoice == "Búa":
                if botChoice == "Búa":
                    await channel.send(f"We are draw, {user.mention} 😉")
                elif botChoice == "Bao":
                    await channel.send(f"{user.mention} is a loser 🤣")
                elif botChoice == "Kéo":
                    await channel.send(
                        f"You are so lucky bitch, {user.mention} 🤬 ")

            if randomChoice == "Bao":
                if botChoice == "Bao":
                    await channel.send(f"We are draw, {user.mention} 😉")
                elif botChoice == "Kéo":
                    await channel.send(f"{user.mention} is a loser 🤣")
                elif botChoice == "Búa":
                    await channel.send(
                        f"You are so lucky bitch, {user.mention} 🤬 ")

    elif reaction.message.id == poll_bj_id:

        if blj.playerScore == "AA":
            await channel.send(f"You are the King, {user.mention} 🫡")

        await update_bj_embed(user)

        if emoji == "✅":
            await update_bj_embed(user)
            user_id = user.id
            # Nếu chưa có, khởi tạo hit count cho user
            if user_id not in hit_counts:
                hit_counts[user_id] = 0

            # Kiểm tra điều kiện điểm và số lần hit
            if hit_counts[user_id] >= 3:
                await channel.send(f"{user.mention}, you have no chance! 🫡")
                return

            if blj.playerScore > 21:
                await channel.send(
                    f"{user.mention}, you are higher 21, you can't hit anymore! 😘"
                )
                await update_bj_embed(user)
                return

            elif blj.playerScore == "AA":
                await channel.send(f"You are the King, {user.mention} 🫡")
                return

            # Nếu đủ điều kiện thì hit
            new_card = blj.playerDraw()
            hit_counts[user_id] += 1  # tăng số lần hit

            await channel.send(
                f"{user.mention} Risked boy 😎👍, You hitted: {new_card}")
            await update_bj_embed(user)

        elif emoji == "❎":

            await update_bj_embed(user)

            if len(blj.playerCards) == 5 and blj.playerScore < 22:
                blj.playerScore = "5 perfect cards"
                await channel.send(f"That was impressive 😲")
                await update_bj_embed(user)

            if blj.botScore == "AA":
                if blj.playerScore == "AA":
                    await channel.send(f"Shhhhhhhhh, {user.mention} 🤫")
                    return
                elif blj.playerScore == "5 perfect cards":
                    await channel.send(f"Nice try my son, {user.mention} 😎")
                    return
                else:
                    await channel.send(f"Give up 🤣 ?")
                    return

            while blj.botScore < 17 and len(blj.botCards) < 5:
                newCard = blj.botDraw()
                await channel.send(f"I hitted: {newCard} 😎")
                await update_bj_embed(user)

            if blj.botScore < 22 and len(blj.botCards) == 5:
                blj.botScore = "5 perfect cards"
                await update_bj_embed(user)
                if blj.playerScore == "AA":
                    await channel.send(f"You are too strong 😭")
                    return
                elif blj.playerScore == blj.botScore:
                    await channel.send(
                        f"Shhhhh shut the fuck up my baby, {user.mention} 🤫")
                    return
                else:
                    await channel.send(f"Chicken 🤣")
                    return

            if blj.playerScore == "AA":
                await channel.send(f"I want it too 😭")
            elif blj.playerScore == "5 perfect cards":
                await channel.send(f"Good job guy 😎")
            elif blj.playerScore == 16:
                await channel.send(f"Why are you scare, {user.mention}? 🤣👎")
            elif blj.playerScore < 16:
                await channel.send(f"You are too young to be f**k! 🫡")
                await channel.send(f"Because you are a loser 🤣")
                return
            else:
                await channel.send(f"Nice mind control, {user.mention} 😎")

            if blj.botScore > 15 and blj.botScore < 22:
                if blj.playerScore == "AA":
                    await channel.send(
                        f"Dammit It should be me not you, {user.mention} 😭")
                elif blj.playerScore == "5 perfect cards":
                    await channel.send(f"I tried my best 😭")
                elif blj.playerScore > 21:
                    await channel.send(f"You are a loser 🤣")
                elif blj.playerScore > 15 and blj.playerScore < 22:
                    if blj.botScore > blj.playerScore:
                        await channel.send(f"You are a loser 🤣")
                    elif blj.botScore < blj.playerScore:
                        await channel.send(f"You are an elder 🤬")
                    else:
                        await channel.send(f"We are peer 😘")
                return
            elif blj.botScore > 21:
                await channel.send(f"You are too lucky, {user.mention} 🤬")
                return

@bot.command()
async def bj(ctx):
    global poll_bj_id, bj_msg, hit_counts

    hit_counts = {}
    blj.playBlackJack()

    embed = discord.Embed(
        title=f"Welcome to Black Jack {ctx.author.mention}",
        description=(f"### {ctx.author.mention} Score: {blj.playerScore}\n"
                     f"### Your cards: {blj.playerCards}\n"
                     f"### Bot Score: {blj.botScore}\n"
                     f"### Bot Cards: {blj.botCards}\n"
                     "### ✅ to Hit\n"
                     "### ❎ to Stand\n"),
        color=discord.Color.dark_blue())

    bj_msg = await ctx.send(embed=embed)
    poll_bj_id = bj_msg.id

    emojis = ["✅", "❎"]
    for emoji in emojis:
        await bj_msg.add_reaction(emoji)

deck_template = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"] * 4

def card_value(card):
    if card == "A":
        return 1
    if card in ["J", "Q", "K"]:
        return 10
    return int(card)

def is_three_tay(hand):
    return all(card in ("J", "Q", "K") for card in hand)

class Room:
    def __init__(self, channel, players):
        self.channel = channel
        self.players = players
        self.results = {}  # {user_id: điểm}

    async def add_result(self, user, score, hand):
        self.results[user.id] = (user, score, hand)

        # Nếu tất cả đã mở xong
        if len(self.results) == len(self.players):
            await self.show_winner()

    async def show_winner(self):
        # Ưu tiên 3 tây trước
        three_tay_players = [
            data for data in self.results.values()
            if is_three_tay(data[2])
        ]

        if three_tay_players:
            winners = three_tay_players
        else:
            max_score = max(data[1] for data in self.results.values())
            winners = [
                data for data in self.results.values()
                if data[1] == max_score
            ]

        result_text = ""
        for user, score, hand in self.results.values():
            if is_three_tay(hand):
                result_text += f"{user.mention}: {' '.join(hand)} → 3 TÂY 🔥\n"
            else:
                result_text += f"{user.mention}: {' '.join(hand)} → {score} nút\n"

        winner_text = ", ".join(w[0].mention for w in winners)

        await self.channel.send(
            f"🎴 **KẾT QUẢ** 🎴\n\n"
            f"{result_text}\n"
            f"🏆 Người thắng: {winner_text}"
        )


class RevealView(discord.ui.View):
    def __init__(self, player, hand, room):
        super().__init__(timeout=60)
        self.player = player
        self.player_id = player.id
        self.hand = hand
        self.room = room
        self.index = 0
        self.revealed = []

    @discord.ui.button(label="🃏 Mở bài", style=discord.ButtonStyle.green)
    async def reveal_card(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user.id != self.player_id:
            await interaction.response.send_message(
                "Không phải bài của bạn!",
                ephemeral=True
            )
            return

        if self.index < 3:
            card = self.hand[self.index]
            self.revealed.append(card)
            self.index += 1

            await interaction.response.send_message(
                f"Đã mở: {' '.join(self.revealed)}",
                ephemeral=True
            )

        if self.index == 3:

            if is_three_tay(self.hand):
                total = 10  # đại diện cao nhất
                special = True
            else:
                total = sum(card_value(c) for c in self.hand) % 10
                special = False

            button.disabled = True
            self.stop()

            if special:
                await interaction.followup.send(
                    f"🎴 {' '.join(self.hand)}\n"
                    f"🔥 **3 TÂY!!! (Lớn nhất)**",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"🎴 {' '.join(self.hand)}\n"
                    f"🔥 Bạn được **{total} nút**",
                    ephemeral=True
                )

            await self.room.add_result(self.player, total, self.hand)


class JoinView(discord.ui.View):
    def __init__(self, host):
        super().__init__(timeout=60)
        self.players = []
        self.host_id = host.id
        self.message = None

    async def update_embed(self):
        embed = discord.Embed(
            title="🎴 BÀI CÀO",
            description="Nhấn Join để tham gia.\nChủ phòng nhấn Start để bắt đầu.",
            color=discord.Color.green()
        )

        embed.add_field(
            name="👥 Người tham gia",
            value="\n".join(p.mention for p in self.players),
            inline=False
        )

        embed.set_footer(text=f"Tổng: {len(self.players)} người")

        await self.message.edit(embed=embed, view=self)

    # ===== NÚT JOIN =====
    @discord.ui.button(label="🎴 Join", style=discord.ButtonStyle.green)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user in self.players:
            await interaction.response.send_message(
                "Bạn đã tham gia rồi!",
                ephemeral=True
            )
            return

        self.players.append(interaction.user)

        await interaction.response.send_message(
            "Đã tham gia!",
            ephemeral=True
        )

        await self.update_embed()

    # ===== NÚT START =====
    @discord.ui.button(label="▶ Start", style=discord.ButtonStyle.blurple)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user.id != self.host_id:
            await interaction.response.send_message(
                "Chỉ chủ phòng mới được Start!",
                ephemeral=True
            )
            return

        if len(self.players) < 1:
            await interaction.response.send_message(
                "Cần ít nhất 1 người!",
                ephemeral=True
            )
            return

        await interaction.response.send_message("Game bắt đầu!")

        # Disable toàn bộ nút sau khi start
        for child in self.children:
            child.disabled = True

        await self.message.edit(view=self)

        # Gọi hàm chia bài ở đây
        deck = deck_template.copy()
        random.shuffle(deck)

        room = Room(interaction.channel, self.players)

        for player in self.players:
            hand = [deck.pop(), deck.pop(), deck.pop()]
            view = RevealView(player, hand, room)

            await interaction.channel.send(
                f"{player.mention} hãy mở bài của bạn!",
                view=view
            )

        self.stop()

@bot.command()
async def baicao(ctx):
    embed = discord.Embed(
        title="🎴 BÀI CÀO",
        description="Nhấn Join để tham gia.\nChủ phòng nhấn Start để bắt đầu.",
        color=discord.Color.green()
    )

    view = JoinView(host=ctx.author)
    view.players.append(ctx.author)

    message = await ctx.send(embed=embed, view=view)
    view.message = message  # lưu message để edit


bot.run(
    "MTM3NjU4ODc2MzUyNTgwODIzOQ.GvtiCn.TzTtKxe38a3KNqEcVFrdIcdFzZQ8efO951vWCc"
)  # Thay bằng token thật

# client.run("MTM3NjU4ODc2MzUyNTgwODIzOQ.GvtiCn.TzTtKxe38a3KNqEcVFrdIcdFzZQ8efO951vWCc")
