import random
import game


def test_check_returns_bool():
    p = game.Player(name="t", origin="o", aura_type="a")
    random.seed(1)
    assert isinstance(game.check(p, "STR", 10), bool)


def test_combat_player_can_win_with_strong_stats(monkeypatch):
    p = game.Player(name="t", origin="o", aura_type="a")
    p.stats["STR"] = 10

    # Always choose basic strike
    monkeypatch.setattr(game, "choose", lambda prompt, opts: 0)
    # Force high rolls
    monkeypatch.setattr(game, "d20", lambda: 20)
    random.seed(2)

    won = game.combat(p, "Dummy", enemy_hp=5, enemy_power=1, enemy_dc=5)
    assert won is True
    assert p.is_alive()


def test_player_is_alive_flag():
    p = game.Player(name="t", origin="o", aura_type="a", hp=0)
    assert p.is_alive() is False
