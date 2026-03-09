#!/usr/bin/env python3
"""Hunter x Hunter: Trails of the Exam
A text-based RPG inspired by Life in Adventure gameplay loops.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Callable, Dict, List, Optional


STAT_NAMES = ["STR", "AGI", "INT", "WILL", "CHA"]


@dataclass
class Player:
    name: str
    origin: str
    aura_type: str
    hp: int = 30
    max_hp: int = 30
    aura: int = 12
    zenny: int = 25
    fame: int = 0
    morality: int = 0  # -10 ruthless ... +10 compassionate
    day: int = 1
    stats: Dict[str, int] = field(default_factory=lambda: {
        "STR": 2,
        "AGI": 2,
        "INT": 2,
        "WILL": 2,
        "CHA": 2,
    })
    inventory: List[str] = field(default_factory=lambda: ["Ration", "Bandage"])
    flags: Dict[str, bool] = field(default_factory=dict)

    def is_alive(self) -> bool:
        return self.hp > 0


def d20() -> int:
    return random.randint(1, 20)


def check(player: Player, stat: str, dc: int, bonus: int = 0) -> bool:
    roll = d20()
    total = roll + player.stats.get(stat, 0) + bonus
    print(f"\n🎲 Check [{stat}] vs DC {dc}: rolled {roll} + stat {player.stats.get(stat,0)} + bonus {bonus} = {total}")
    return total >= dc


def choose(prompt: str, options: List[str]) -> int:
    print(f"\n{prompt}")
    for i, opt in enumerate(options, start=1):
        print(f"  {i}. {opt}")
    while True:
        raw = input("\nChoose an action: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return int(raw) - 1
        print("Invalid choice. Pick a valid number.")


def print_status(player: Player) -> None:
    stat_line = " | ".join([f"{k}:{v}" for k, v in player.stats.items()])
    print("\n" + "=" * 72)
    print(f"Day {player.day} | {player.name} the {player.origin} ({player.aura_type})")
    print(f"HP {player.hp}/{player.max_hp} | Aura {player.aura} | Zenny {player.zenny} | Fame {player.fame} | Morality {player.morality}")
    print(f"Stats: {stat_line}")
    print(f"Inventory: {', '.join(player.inventory) if player.inventory else 'Empty'}")
    print("=" * 72)


def combat(player: Player, enemy_name: str, enemy_hp: int, enemy_power: int, enemy_dc: int) -> bool:
    print(f"\n⚔️  Combat starts! {enemy_name} appears.")
    while enemy_hp > 0 and player.is_alive():
        print(f"\n{enemy_name} HP: {enemy_hp} | Your HP: {player.hp} | Aura: {player.aura}")
        action = choose(
            "Combat action:",
            [
                "Basic strike (STR)",
                "Swift maneuver (AGI)",
                "Nen burst (uses 2 Aura, WILL)",
                "Defend (reduce next damage)",
                "Use bandage (+8 HP if available)",
            ],
        )

        defended = False
        if action == 0:
            if check(player, "STR", enemy_dc):
                dmg = random.randint(4, 8) + player.stats["STR"]
                print(f"Hit! You deal {dmg} damage.")
                enemy_hp -= dmg
            else:
                print("Missed strike.")
        elif action == 1:
            if check(player, "AGI", enemy_dc + 1):
                dmg = random.randint(3, 7) + player.stats["AGI"]
                print(f"You outstep and slash for {dmg} damage.")
                enemy_hp -= dmg
            else:
                print("You fail to find an opening.")
        elif action == 2:
            if player.aura < 2:
                print("Not enough Aura!")
            else:
                player.aura -= 2
                if check(player, "WILL", enemy_dc):
                    dmg = random.randint(6, 12) + player.stats["WILL"]
                    print(f"Nen impact! {dmg} damage dealt.")
                    enemy_hp -= dmg
                else:
                    print("Your aura control wavers.")
        elif action == 3:
            defended = True
            print("You brace for impact.")
        elif action == 4:
            if "Bandage" in player.inventory:
                player.inventory.remove("Bandage")
                heal = 8
                player.hp = min(player.max_hp, player.hp + heal)
                print(f"You patch yourself and recover {heal} HP.")
            else:
                print("No bandage left!")

        if enemy_hp <= 0:
            break

        incoming = random.randint(enemy_power - 2, enemy_power + 2)
        if defended:
            incoming = max(1, incoming // 2)
        print(f"{enemy_name} attacks for {incoming} damage!")
        player.hp -= incoming

    if player.is_alive():
        print(f"\n✅ You defeated {enemy_name}!")
        return True
    print("\n☠️ You were defeated.")
    return False


def intro() -> Player:
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    HUNTER x HUNTER: TRAILS OF THE EXAM              ║
║       A text adventure inspired by Life in Adventure gameplay        ║
╚══════════════════════════════════════════════════════════════════════╝
""")
    name = input("Enter your Hunter codename: ").strip() or "Rookie"
    origin_idx = choose("Choose your origin:", ["Whale Island Drifter", "Kakin Backstreet", "Heavens Arena Disciple"])
    aura_idx = choose("Choose your natural aura tendency:", ["Enhancer", "Transmuter", "Specialist"])

    origin = ["Whale Island Drifter", "Kakin Backstreet", "Heavens Arena Disciple"][origin_idx]
    aura_type = ["Enhancer", "Transmuter", "Specialist"][aura_idx]
    player = Player(name=name, origin=origin, aura_type=aura_type)

    if origin_idx == 0:
        player.stats["WILL"] += 1
        player.stats["AGI"] += 1
    elif origin_idx == 1:
        player.stats["CHA"] += 1
        player.zenny += 20
    else:
        player.stats["STR"] += 1
        player.stats["AGI"] += 1

    if aura_idx == 0:
        player.stats["STR"] += 1
    elif aura_idx == 1:
        player.stats["AGI"] += 1
    else:
        player.stats["INT"] += 1

    return player


def event_lost_child(player: Player) -> None:
    print("\nA crying child in Zevil Port says a fake Hunter stole his badge.")
    c = choose("How do you respond?", ["Track the thief", "Ignore and move on", "Comfort child and buy food (5 zenny)"])
    if c == 0:
        if check(player, "AGI", 12):
            print("You corner the thief and return the badge. The crowd cheers.")
            player.fame += 2
            player.morality += 2
            player.zenny += 10
        else:
            print("The thief slips away; you scrape your knee in pursuit.")
            player.hp -= 4
    elif c == 1:
        print("You conserve energy, but feel your resolve dim.")
        player.morality -= 1
    else:
        if player.zenny >= 5:
            player.zenny -= 5
            player.morality += 2
            player.fame += 1
            print("Kindness matters. The child smiles through tears.")
        else:
            print("You can't afford it; awkward silence follows.")


def event_examiner_riddle(player: Player) -> None:
    print("\nAn Examiner blocks the canyon path: 'Answer, or turn back.'")
    c = choose("Your play:", ["Solve with logic", "Charm your way through", "Force your way past"])
    if c == 0:
        if check(player, "INT", 13):
            print("Your answer is flawless. The Examiner nods.")
            player.fame += 2
            player.flags["examiner_favor"] = True
        else:
            print("Wrong answer. You lose precious time and stamina.")
            player.hp -= 5
    elif c == 1:
        if check(player, "CHA", 12):
            print("The Examiner laughs and lets you pass.")
            player.fame += 1
        else:
            print("Your bluff fails.")
            player.morality -= 1
    else:
        if combat(player, "Exam Beast", enemy_hp=18, enemy_power=5, enemy_dc=11):
            player.fame += 1
            player.morality -= 1


def event_blacklist_offer(player: Player) -> None:
    print("\nA Blacklist broker offers a high-paying, morally gray contract.")
    c = choose("Accept the deal?", ["Accept", "Refuse", "Negotiate terms"])
    if c == 0:
        print("You complete the mission, but rumors spread.")
        player.zenny += 40
        player.morality -= 3
    elif c == 1:
        print("You refuse dirty work and keep your conscience clear.")
        player.morality += 2
        player.fame += 1
    else:
        if check(player, "CHA", 13):
            print("You renegotiate: only non-lethal capture.")
            player.zenny += 25
            player.fame += 2
            player.morality += 1
        else:
            print("Talks collapse. The broker marks your face.")
            player.flags["underworld_enemy"] = True


def event_phantom_ambush(player: Player) -> None:
    print("\nIn Yorknew's shadows, a Spider affiliate targets you.")
    if combat(player, "Spider Affiliate", enemy_hp=24, enemy_power=7, enemy_dc=12):
        player.fame += 3
        player.zenny += 20
        player.flags["spider_survivor"] = True


def event_rest(player: Player) -> None:
    print("\nYou find a quiet inn to recover and train Ten.")
    heal = random.randint(6, 12)
    player.hp = min(player.max_hp, player.hp + heal)
    player.aura = min(12, player.aura + 3)
    stat = random.choice(STAT_NAMES)
    player.stats[stat] += 1
    print(f"Recovered {heal} HP, +3 Aura, and {stat} increased by 1.")


def ending(player: Player) -> None:
    print("\n" + "#" * 72)
    print("FINAL REPORT")
    if not player.is_alive():
        print("You fell before earning your true Hunter legacy.")
    elif player.fame >= 8 and player.morality >= 3:
        print("🌟 Ending: Beacon Hunter — a legend of strength and compassion.")
    elif player.fame >= 8 and player.morality < 3:
        print("🕷️ Ending: Infamous Prodigy — feared, brilliant, and unstoppable.")
    elif player.flags.get("underworld_enemy"):
        print("🎯 Ending: Marked by the Underworld — every job is now a duel.")
    else:
        print("🧭 Ending: Wandering Hunter — your real adventure has just begun.")
    print(f"Days survived: {player.day} | Fame: {player.fame} | Morality: {player.morality} | Zenny: {player.zenny}")
    print("#" * 72)


def run_game() -> None:
    player = intro()
    events: List[Callable[[Player], None]] = [
        event_lost_child,
        event_examiner_riddle,
        event_blacklist_offer,
        event_rest,
        event_phantom_ambush,
    ]

    print("\nYour Hunter journey begins. Survive 8 days of trials.\n")
    while player.day <= 8 and player.is_alive():
        print_status(player)
        event = random.choice(events)
        event(player)
        player.day += 1
        player.aura = min(12, player.aura + 1)

    ending(player)


if __name__ == "__main__":
    run_game()
