import random
import time
import pygame


class Card(object):
    def __init__(self, name, value, suit):
        self.value = value
        self.name = name
        self.suit = suit
        self.filename = "cards_index/" + name + suit[0] + ".png"

    def __repr__(self):
        return f"{self.name}{self.suit}"

    def __gt__(self, other):
        return self.value > other.value


class Deck:
    def __init__(self):
        self.cards = []
        suits = {"hearts": "♥",
                 "spades": "♠",
                 "diamonds": "♦",
                 "clubs": "♣"}
        values = {
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "10": 10,
            "J": 11,
            "Q": 12,
            "K": 13,
            "A": 14
        }
        for name in values:
            for suit in suits:
                self.cards.append(Card(name, values[name], suit))

    def shuffle(self):
        random.shuffle(self.cards)


class Player:
    def __init__(self, deck):
        self.cards = [deck.cards.pop(), deck.cards.pop()]
        self.score = 0
        self.hand = ""
        self.hand_text = {
            1: "Ace",
            2: "deuce",
            3: "three",
            4: "four",
            5: "five",
            6: "six",
            7: "seven",
            8: "eight",
            9: "nine",
            10: "ten",
            11: "Jack",
            12: "Queen",
            13: "King",
            14: "Ace"
        }
        self.cards_coordinates = [(), ()]
        self.balance = 1000
        self.fold = False
        self.call = False
        self.bet = False
        self.check = False
        self.allin = False

    def fold(self):
        self.fold = False

    def call(self, pot_value, amount):
        self.balance -= amount
        pot_value += amount
        self.call = False

    def bet(self, pot_value, amount):
        self.balance -= amount
        pot_value += amount
        self.bet = False

    def check(self):
        self.check = False

    def allin(self, pot_value):
        pot_value += self.balance
        self.balance = 0
        self.allin = False


class RoyalFlush:
    def equal(self, other):
        return True

    def verify(self, cards, player):
        color_frequency_array = []

        for index in range(4):
            color_frequency_array.append(0)

        for card in cards:
            if card.suit == "♥":
                color_frequency_array[0] += 1
            if card.suit == "♠":
                color_frequency_array[1] += 1
            if card.suit == "♦":
                color_frequency_array[2] += 1
            if card.suit == "♣":
                color_frequency_array[3] += 1

        index = 0
        while index < 4:
            if color_frequency_array[index] >= 5:
                if index == 0:
                    suit = "♥"
                    break
                if index == 1:
                    suit = "♠"
                    break
                if index == 2:
                    suit = "♦"
                    break
                if index == 3:
                    suit = "♣"
                    break
            index += 1
        else:
            return False

        flush_cards = []

        for card in cards:
            if card.suit == suit:
                flush_cards.append(card.value)

        flush_cards.sort()
        if 10 in flush_cards and 11 in flush_cards and 12 in flush_cards and 13 in flush_cards and 14 in flush_cards:
            player.score = 10
            player.hand = "a royal flush"
            return True
        return False


class StraightFlush:
    def __init__(self):
        self.high_card = 0

    def equal(self, other):
        return self.high_card == other.high_card

    def compare(self, other):
        hands = []

        if self.high_card > other.high_card:
            hands.append(self)
            hands.append(other)
        else:
            hands.append(other)
            hands.append(self)

        return hands

    def verify(self, cards, player):
        color_frequency_array = []

        for index in range(4):
            color_frequency_array.append(0)

        for card in cards:
            if card.suit == "hearts":
                color_frequency_array[0] += 1
            if card.suit == "spades":
                color_frequency_array[1] += 1
            if card.suit == "diamonds":
                color_frequency_array[2] += 1
            if card.suit == "clubs":
                color_frequency_array[3] += 1

        index = 0
        while index < 4:
            if color_frequency_array[index] >= 5:
                if index == 0:
                    suit = "hearts"
                    break
                if index == 1:
                    suit = "spades"
                    break
                if index == 2:
                    suit = "diamonds"
                    break
                if index == 3:
                    suit = "clubs"
                    break
            index += 1
        else:
            return False

        flush_cards = []

        for card in cards:
            if card.suit == suit:
                flush_cards.append(card)

        flush_cards.sort()

        values = []
        value_frequency_array = []

        for index in range(15):
            value_frequency_array.append(0)

        for card in flush_cards:
            values.append(card.value)

        for value in values:
            value_frequency_array[value] += 1
            if value == 14:
                value_frequency_array[1] += 1

        cards_count = 0
        longest_straight = 0
        high_card_index = 0
        index = 0
        while index < 15:
            if value_frequency_array[index] > 0:
                cards_count += 1
                if cards_count > longest_straight:
                    longest_straight = cards_count
                    high_card_index = index
            else:
                cards_count = 0
            index += 1

        if longest_straight >= 5:
            self.high_card = high_card_index
            player.score = 9
            player.hand = f"a straight flush, {player.hand_text[self.high_card]} high"
            return True
        return False


class FourOfAKind:
    def __init__(self):
        self.quads = 0
        self.kicker = 0

    def equal(self, other):
        return self.quads == other.quads and self.kicker == other.kicker

    def compare(self, other):
        hands = []
        order = True

        if self.quads == other.quads:
            if self.kicker < other.kicker:
                order = False
        elif self.quads < other.quads:
            order = False

        if order:
            hands.append(self)
            hands.append(other)
        else:
            hands.append(other)
            hands.append(self)

        return hands

    def verify(self, cards, player):
        values = []
        frequency_array = []

        for index in range(15):
            frequency_array.append(0)

        for card in cards:
            values.append(card.value)

        for value in values:
            frequency_array[value] += 1

        index = 0
        while index < 15:
            if frequency_array[index] == 4:
                self.quads = index
                break
            index += 1
        else:
            return False

        for value in values:
            if value != self.quads and value > self.kicker:
                self.kicker = value

        player.score = 8
        if self.quads == 6:
            player.hand = f"four of a kind, {player.hand_text[self.quads]}es"
        else:
            player.hand = f"four of a kind, {player.hand_text[self.quads]}s"
        return True


# sixes
class FullHouse:
    def __init__(self):
        self.trio = 0
        self.pair = 0

    def equal(self, other):
        return self.trio == other.trio and self.pair == other.pair

    def compare(self, other):
        hands = []
        order = True

        if self.trio == other.trio:
            if self.pair < other.pair:
                order = False
        elif self.trio < other.trio:
            order = False

        if order:
            hands.append(self)
            hands.append(other)
        else:
            hands.append(other)
            hands.append(self)

        return hands

    def verify(self, cards, player):
        values = []
        frequency_array = []

        for index in range(15):
            frequency_array.append(0)

        for card in cards:
            values.append(card.value)

        for value in values:
            frequency_array[value] += 1

        index = 0
        while index < 15:
            if frequency_array[index] == 3 and index > self.trio:
                self.trio = index
            index += 1

        if self.trio == 0:
            return False

        index = 0
        while index < 15:
            if frequency_array[index] >= 2 and index != self.trio and index > self.pair:
                self.pair = index
            index += 1

        if self.pair == 0:
            return False

        player.score = 7
        player.hand = f"a full house, {player.hand_text[self.trio]}s full of {player.hand_text[self.pair]}s"
        return True


class Flush:
    def __init__(self):
        self.high_card = 0
        self.kicker1 = 0
        self.kicker2 = 0
        self.kicker3 = 0
        self.kicker4 = 0

    def equal(self, other):
        return self.high_card == other.high_card and self.kicker1 == other.kicker1 and self.kicker2 == other.kicker2 \
               and self.kicker3 == other.kicker3 and self.kicker4 == other.kicker4

    def compare(self, other):
        hands = []
        order = True

        if self.high_card == other.high_card:
            if self.kicker1 == other.kicker1:
                if self.kicker2 == other.kicker2:
                    if self.kicker3 == other.kicker3:
                        if self.kicker4 < other.kicker4:
                            order = False
                    elif self.kicker3 < other.kicker3:
                        order = False
                elif self.kicker2 < other.kicker2:
                    order = False
            elif self.kicker1 < other.kicker1:
                order = False
        elif self.high_card < other.high_card:
            order = False

        if order:
            hands.append(self)
            hands.append(other)
        else:
            hands.append(other)
            hands.append(self)

        return hands

    def verify(self, cards, player):
        frequency_array = []

        for index in range(4):
            frequency_array.append(0)

        for card in cards:
            if card.suit == "hearts":
                frequency_array[0] += 1
            if card.suit == "spades":
                frequency_array[1] += 1
            if card.suit == "diamonds":
                frequency_array[2] += 1
            if card.suit == "clubs":
                frequency_array[3] += 1

        index = 0
        while index < 4:
            if frequency_array[index] >= 5:
                if index == 0:
                    suit = "hearts"
                    break
                if index == 1:
                    suit = "spades"
                    break
                if index == 2:
                    suit = "diamonds"
                    break
                if index == 3:
                    suit = "clubs"
                    break
            index += 1
        else:
            return False

        flush_cards = []

        for card in cards:
            if card.suit == suit:
                flush_cards.append(card)

        flush_cards.sort()
        flush_cards_len = len(flush_cards)

        self.high_card = flush_cards[flush_cards_len - 1].value
        self.kicker1 = flush_cards[flush_cards_len - 2].value
        self.kicker2 = flush_cards[flush_cards_len - 3].value
        self.kicker3 = flush_cards[flush_cards_len - 4].value
        self.kicker4 = flush_cards[flush_cards_len - 5].value

        player.score = 6
        player.hand = f"a flush, {player.hand_text[self.high_card]} high"
        return True


class Straight:
    def __init__(self):
        self.high_card = 0

    def equal(self, other):
        return self.high_card == other.high_card

    def compare(self, other):
        hands = []

        if self.high_card > other.high_card:
            hands.append(self)
            hands.append(other)
        else:
            hands.append(other)
            hands.append(self)

        return hands

    def verify(self, cards, player):
        values = []
        frequency_array = []

        for index in range(15):
            frequency_array.append(0)

        for card in cards:
            values.append(card.value)

        for value in values:
            frequency_array[value] += 1
            if value == 14:
                frequency_array[1] += 1

        cards_count = 0
        longest_straight = 0
        high_card_index = 0
        index = 0
        while index < 15:
            if frequency_array[index] > 0:
                cards_count += 1
                if cards_count > longest_straight:
                    longest_straight = cards_count
                    high_card_index = index
            else:
                cards_count = 0
            index += 1

        if longest_straight >= 5:
            self.high_card = high_card_index
            player.score = 5
            player.hand = f"a straight, {player.hand_text[self.high_card - 4]} to {player.hand_text[self.high_card]}"
            return True
        return False


class ThreeOfAKind:
    def __init__(self):
        self.trio = 0
        self.kicker1 = 0
        self.kicker2 = 0

    def equal(self, other):
        return self.trio == other.trio and self.kicker1 == other.kicker1 and self.kicker2 == other.kicker2

    def compare(self, other):
        hands = []
        order = True

        if self.trio == other.trio:
            if self.kicker1 == other.kicker1:
                if self.kicker2 < other.kicker2:
                    order = False
            elif self.kicker1 < other.kicker1:
                order = False
        elif self.trio < other.trio:
            order = False

        if order:
            hands.append(self)
            hands.append(other)
        else:
            hands.append(other)
            hands.append(self)

        return hands

    def verify(self, cards, player):
        values = []
        frequency_array = []

        for index in range(15):
            frequency_array.append(0)

        for card in cards:
            values.append(card.value)

        for value in values:
            frequency_array[value] += 1

        index = 0
        while index < 15:
            if frequency_array[index] == 3:
                self.trio = index
                break
            index += 1
        else:
            return False

        for value in values:
            if value != self.trio and value > self.kicker1:
                self.kicker1 = value

        for value in values:
            if value != self.trio and value != self.kicker1 and value > self.kicker2:
                self.kicker2 = value

        player.score = 4
        if self.trio == 6:
            player.hand = f"three of a kind, {player.hand_text[self.trio]}es"
        else:
            player.hand = f"three of a kind, {player.hand_text[self.trio]}s"
        return True


# sixes
class TwoPair:
    def __init__(self):
        self.pair1 = 0
        self.pair2 = 0
        self.kicker = 0

    def equal(self, other):
        return self.pair1 == other.pair1 and self.pair2 == other.pair2 and self.kicker == other.kicker

    def compare(self, other):
        hands = []
        order = True

        if self.pair1 == other.pair1:
            if self.pair2 == other.pair2:
                if self.kicker < other.kicker:
                    order = False
            elif self.pair2 < other.pair2:
                order = False
        elif self.pair1 < other.pair1:
            order = False

        if order:
            hands.append(self)
            hands.append(other)
        else:
            hands.append(other)
            hands.append(self)

        return hands

    def verify(self, cards, player):
        values = []
        frequency_array = []
        pair_values = []

        for index in range(3):
            pair_values.append(0)

        for index in range(15):
            frequency_array.append(0)

        for card in cards:
            values.append(card.value)

        for value in values:
            frequency_array[value] += 1

        index = 0
        while index < 15:
            if frequency_array[index] == 2:
                pair_values[0] = index
                break
            index += 1
        else:
            return False

        index += 1
        while index < 15:
            if frequency_array[index] == 2:
                pair_values[1] = index
                break
            index += 1
        else:
            return False

        # third pair
        index += 1
        while index < 15:
            if frequency_array[index] == 2:
                pair_values[2] = index
                break
            index += 1

        pair_values.sort()
        self.pair1 = pair_values[2]
        self.pair2 = pair_values[1]

        for value in values:
            if value != self.pair1 and value != self.pair2 and value > self.kicker:
                self.kicker = value

        player.score = 3
        player.hand = f"two pair, {player.hand_text[self.pair1]}s and {player.hand_text[self.pair2]}s"
        return True


class OnePair:
    def __init__(self):
        self.pair = 0
        self.kicker1 = 0
        self.kicker2 = 0
        self.kicker3 = 0

    def equal(self, other):
        return self.pair == other.pair and self.kicker1 == other.kicker1 and self.kicker2 == other.kicker2 \
               and self.kicker3 == other.kicker3

    def compare(self, other):
        hands = []
        order = True

        if self.pair == other.pair:
            if self.kicker1 == other.kicker1:
                if self.kicker2 == other.kicker2:
                    if self.kicker3 < other.kicker3:
                        order = False
                elif self.kicker2 < other.kicker2:
                    order = False
            elif self.kicker1 < other.kicker1:
                order = False
        elif self.pair < other.pair:
            order = False

        if order:
            hands.append(self)
            hands.append(other)
        else:
            hands.append(other)
            hands.append(self)

        return hands

    def verify(self, cards, player):
        values = []
        frequency_array = []

        for index in range(15):
            frequency_array.append(0)

        for card in cards:
            values.append(card.value)

        for value in values:
            frequency_array[value] += 1

        index = 0
        while index < 15:
            if frequency_array[index] == 2:
                self.pair = index
                break
            index += 1

        else:
            return False

        index = 0
        while index < 7:
            if self.pair == values[index]:
                pair_index = index
                break
            index += 1

        values.pop(pair_index)
        values.pop(pair_index)

        self.kicker1 = values[4]
        self.kicker2 = values[3]
        self.kicker3 = values[2]

        player.score = 2
        if self.pair == 6:
            player.hand = f"a pair of {player.hand_text[self.pair]}es"
        else:
            player.hand = f"a pair of {player.hand_text[self.pair]}s"
        return True


class HighCard:
    def __init__(self):
        self.high_card = 0
        self.kicker1 = 0
        self.kicker2 = 0
        self.kicker3 = 0
        self.kicker4 = 0

    def equal(self, other):
        return self.high_card == other.high_card and self.kicker1 == other.kicker1 and self.kicker2 == other.kicker2 \
               and self.kicker3 == other.kicker3 and self.kicker4 == other.kicker4

    def compare(self, other):
        hands = []
        order = True

        if self.high_card == other.high_card:
            if self.kicker1 == other.kicker1:
                if self.kicker2 == other.kicker2:
                    if self.kicker3 == other.kicker3:
                        if self.kicker4 < other.kicker4:
                            order = False
                    elif self.kicker3 < other.kicker3:
                        order = False
                elif self.kicker2 < other.kicker2:
                    order = False
            elif self.kicker1 < other.kicker1:
                order = False
        elif self.high_card < other.high_card:
            order = False

        if order:
            hands.append(self)
            hands.append(other)
        else:
            hands.append(other)
            hands.append(self)

        return hands

    def verify(self, cards, player):
        self.high_card = cards[6].value
        self.kicker1 = cards[5].value
        self.kicker2 = cards[4].value
        self.kicker3 = cards[3].value
        self.kicker4 = cards[2].value

        player.score = 1
        player.hand = f"high card {player.hand_text[self.high_card]}"
        return True


def scoreboard(cards, player):
    cards.sort()
    while True:
        royal_flush = RoyalFlush()
        if royal_flush.verify(cards, player):
            return royal_flush

        straight_flush = StraightFlush()
        if straight_flush.verify(cards, player):
            return straight_flush

        four_of_a_kind = FourOfAKind()
        if four_of_a_kind.verify(cards, player):
            return four_of_a_kind

        full_house = FullHouse()
        if full_house.verify(cards, player):
            return full_house

        flush = Flush()
        if flush.verify(cards, player):
            return flush

        straight = Straight()
        if straight.verify(cards, player):
            return straight

        three_of_a_kind = ThreeOfAKind()
        if three_of_a_kind.verify(cards, player):
            return three_of_a_kind

        two_pair = TwoPair()
        if two_pair.verify(cards, player):
            return two_pair

        one_pair = OnePair()
        if one_pair.verify(cards, player):
            return one_pair

        high_card = HighCard()
        if high_card.verify(cards, player):
            return high_card


# general
display_resolution = (1400, 808)
number_of_players = 2

pygame.init()
screen = pygame.display.set_mode(display_resolution)

pygame.display.set_caption("Poker")
icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)
background = pygame.image.load("background.png")

# buttons
buttons_coordinates = [(975, 730), (1110, 730), (1245, 730)]
card_back = pygame.image.load("cards_index/card_back.png")
bet_button = pygame.image.load("buttons/bet_button.png")
raise_button = pygame.image.load("buttons/raise_button.png")
fold_button = pygame.image.load("buttons/fold_button.png")
check_button = pygame.image.load("buttons/check_button.png")
call_button = pygame.image.load("buttons/call_button.png")
allin_button = pygame.image.load("buttons/allin_button.png")

# avatars
avatars_coordinates = [(525, 37), (525, 542)]
avatars = [pygame.image.load("player1_avatar.png"), pygame.image.load("player2_avatar.png")]
fonts = [pygame.font.Font("BebasNeue-Regular.otf", 30),
         pygame.font.Font("BebasNeue-Regular.otf", 24),
         pygame.font.Font("jai.TTF", 25)]
text_color = (230, 230, 230)
balance_coordinates = [(720, 95), (720, 599)]

# pot
pot_value = 0
pot_image_coordinates = (445, 305)
pot_text_coordinates = (474, 378)
pot_image = pygame.image.load("pot.png")

# bets
current_bets = [0, 0]
bet_chips = pygame.image.load("chips.png")
bet_chips_coordinates = [(797, 135), (797, 457)]
bet_text_coordinates = [(831, 203), (831, 525)]

# winner hand text box
winner_hand_text_box_coordinates = (17, 620)
winner_hand_text_coordinates = [(313, 710), (313, 747)]
winner_hand_text_box = pygame.image.load("winner_hand.png")

# players cards
deck = Deck()
deck.shuffle()
players = []
for i in range(number_of_players):
    players.append(Player(deck))

players_cards_coordinates = [[(632, 146), (692, 146)], [(632, 470), (692, 470)]]
players_cards = [[None, None], [None, None]]
for i in range(number_of_players):
    for j in range(2):
        players_cards[i][j] = pygame.image.load(players[i].cards[j].filename)

# board cards
board = []
for i in range(5):
    board.append(deck.cards.pop())

board_coordinates = [(544, 307), (604, 307), (664, 307), (724, 307), (784, 307)]
board_cards = []
for i in range(5):
    board_cards.append(pygame.image.load(board[i].filename))

running = True
while running:
    screen.blit(background, (0, 0))

    # avatars
    for i in range(2):
        screen.blit(avatars[i], avatars_coordinates[i])
        balance_text = fonts[0].render(f"${players[i].balance}", True, text_color)
        balance_text_rect = balance_text.get_rect()
        balance_text_rect.center = balance_coordinates[i]
        screen.blit(balance_text, balance_text_rect)

    # pot
    screen.blit(pot_image, pot_image_coordinates)
    pot_text = fonts[1].render(f"Pot: ${pot_value}", True, text_color)
    pot_text_rect = pot_text.get_rect()
    pot_text_rect.center = pot_text_coordinates
    screen.blit(pot_text, pot_text_rect)

    # bets
    for i in range(number_of_players):
        screen.blit(bet_chips, bet_chips_coordinates[i])
        bet_text = fonts[1].render(f"${current_bets[i]}", True, text_color)
        bet_text_rect = bet_text.get_rect()
        bet_text_rect.center = bet_text_coordinates[i]
        screen.blit(bet_text, bet_text_rect)

    # buttons
    screen.blit(fold_button, buttons_coordinates[0])
    screen.blit(call_button, buttons_coordinates[1])
    screen.blit(raise_button, buttons_coordinates[2])

    # players cards
    for i in range(number_of_players):
        for j in range(2):
            screen.blit(players_cards[i][j], players_cards_coordinates[i][j])

    # board cards
    for i in range(5):
        screen.blit(board_cards[i], board_coordinates[i])

    # winner hand
    hands = [scoreboard(players[0].cards + board, players[0]), scoreboard(players[1].cards + board, players[1])]
    result = [False, False, False]

    if players[0].score < players[1].score:
        result[0] = True
    elif players[0].score > players[1].score:
        result[1] = True
    else:
        if hands[0].equal(hands[1]):
            result[2] = True
        else:
            hands_sorted = hands[0].compare(hands[1])
            if hands_sorted[0] == hands[0]:
                result[1] = True
            else:
                result[0] = True

    screen.blit(winner_hand_text_box, winner_hand_text_box_coordinates)

    if result[0]:
        winner_hand_texts = [fonts[1].render(f"You win the pot ({pot_value})", True, text_color),
                             fonts[1].render(f"with {players[1].hand}.", True, text_color)]
    elif result[1]:
        winner_hand_texts = [fonts[1].render(f"John wins the pot ({pot_value})", True, text_color),
                             fonts[1].render(f"with {players[0].hand}.", True, text_color)]
    else:
        winner_hand_texts = [fonts[1].render(f"You split the pot ({pot_value}) with John.", True, text_color),
                             fonts[1].render(f"Both players have {players[0].hand}.", True, text_color)]

    winner_hand_texts_rect = [winner_hand_texts[0].get_rect(), winner_hand_texts[1].get_rect()]
    for i in range(2):
        winner_hand_texts_rect[i].center = winner_hand_text_coordinates[i]
        screen.blit(winner_hand_texts[i], winner_hand_texts_rect[i])

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.display.update()
