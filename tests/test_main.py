"""
Tests for main.py — menu structure and routing logic, no API calls.

Covers GAME_ACTIONS entries, MODE_LABELS, CHARACTER_RUNNERS,
and the dispatch logic for procedural modes (first_contact).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import main


# ── GAME_ACTIONS structure ────────────────────────────────────────────────────────

class TestGameActionsStructure:
    def _keys(self, game: str) -> list[str]:
        return [k for k, _ in main.GAME_ACTIONS[game]]

    def test_all_four_games_present(self):
        for game in ("dnd", "traveller", "firefly", "scum"):
            assert game in main.GAME_ACTIONS, f"Game '{game}' missing from GAME_ACTIONS"

    def test_traveller_has_alien_mode(self):
        assert "alien" in self._keys("traveller")

    def test_traveller_has_synthetic_mode(self):
        assert "synthetic" in self._keys("traveller")

    def test_traveller_has_first_contact_mode(self):
        assert "first_contact" in self._keys("traveller")

    def test_scum_has_stardancer_mode(self):
        assert "stardancer" in self._keys("scum")

    def test_dnd_does_not_have_alien_mode(self):
        assert "alien" not in self._keys("dnd")

    def test_dnd_does_not_have_synthetic_mode(self):
        assert "synthetic" not in self._keys("dnd")

    def test_dnd_does_not_have_first_contact_mode(self):
        assert "first_contact" not in self._keys("dnd")

    def test_firefly_does_not_have_alien_mode(self):
        assert "alien" not in self._keys("firefly")

    def test_scum_does_not_have_alien_mode(self):
        # alien is Traveller-only
        assert "alien" not in self._keys("scum")

    def test_traveller_does_not_have_stardancer(self):
        # stardancer is S&V-only
        assert "stardancer" not in self._keys("traveller")

    def test_traveller_core_modes_preserved(self):
        keys = self._keys("traveller")
        for mode in ("full", "npc", "patron", "party", "cluster",
                     "encounter", "ship", "location", "rumor", "event"):
            assert mode in keys, f"Core mode '{mode}' missing from traveller"

    def test_scum_core_modes_preserved(self):
        keys = self._keys("scum")
        for mode in ("full", "npc", "scorecontact", "party", "cluster",
                     "encounter", "ship", "location", "rumor", "event"):
            assert mode in keys, f"Core mode '{mode}' missing from scum"

    def test_each_action_has_label(self):
        for game, actions in main.GAME_ACTIONS.items():
            for key, label in actions:
                assert isinstance(label, str) and len(label) > 0, \
                    f"Empty label for {game}/{key}"


# ── MODE_LABELS ───────────────────────────────────────────────────────────────────

class TestModeLabels:
    def test_alien_has_label(self):
        assert "alien" in main.MODE_LABELS

    def test_synthetic_has_label(self):
        assert "synthetic" in main.MODE_LABELS

    def test_stardancer_has_label(self):
        assert "stardancer" in main.MODE_LABELS

    def test_first_contact_not_in_mode_labels(self):
        # first_contact is fully procedural — handled before the label lookup,
        # so it must NOT be in MODE_LABELS (which would cause a KeyError if reached)
        assert "first_contact" not in main.MODE_LABELS

    def test_existing_modes_still_present(self):
        for mode in ("full", "npc", "patron", "scorecontact", "jobcontact", "questgiver"):
            assert mode in main.MODE_LABELS, f"Mode '{mode}' missing from MODE_LABELS"

    def test_labels_are_non_empty_strings(self):
        for mode, label in main.MODE_LABELS.items():
            assert isinstance(label, str) and len(label) > 0, \
                f"Empty label for mode '{mode}'"


# ── CHARACTER_RUNNERS ─────────────────────────────────────────────────────────────

class TestCharacterRunners:
    def test_all_four_games_have_runners(self):
        for game in ("dnd", "traveller", "firefly", "scum"):
            assert game in main.CHARACTER_RUNNERS, f"No runner for game '{game}'"

    def test_runners_are_callable(self):
        for game, runner in main.CHARACTER_RUNNERS.items():
            assert callable(runner), f"Runner for '{game}' is not callable"

    def test_traveller_runner_is_traveller_agent(self):
        from agents import traveller_agent
        assert main.CHARACTER_RUNNERS["traveller"] is traveller_agent.run

    def test_scum_runner_is_scum_agent(self):
        from agents import scum_villainy_agent
        assert main.CHARACTER_RUNNERS["scum"] is scum_villainy_agent.run


# ── GAMES list ────────────────────────────────────────────────────────────────────

class TestGamesList:
    def test_four_games_listed(self):
        assert len(main.GAMES) == 4

    def test_all_game_keys_match_game_actions(self):
        listed_keys = {k for k, _ in main.GAMES}
        assert listed_keys == set(main.GAME_ACTIONS.keys())

    def test_games_have_display_labels(self):
        for key, label in main.GAMES:
            assert isinstance(label, str) and len(label) > 0, \
                f"Empty label for game '{key}'"
