"""Drag & drop on "Heute": own order of decks, moving a deck into another (or back to the top)."""

import tempfile
from pathlib import Path

from muisti.core import Core

core = Core(str(Path(tempfile.mkdtemp()) / "c.anki2"))
col = core._col
ids = {n: core.create_deck(n) for n in ["Analysis", "Analysis::Integrale", "Analysis::Reihen", "DBIS", "Spanisch", "SWEN"]}
names = lambda nodes: [d["short"] for d in nodes]  # noqa: E731

assert names(core.decks())[:4] == ["Analysis", "DBIS", "Spanisch", "SWEN"]  # Anki's order: by name

# own order, top level and within a parent; decks not in the list follow by name
core.set_deck_order([ids["SWEN"], ids["Analysis"], ids["Analysis::Reihen"]])
tree = core.decks()
assert names(tree)[:2] == ["SWEN", "Analysis"], names(tree)
assert names(tree[1]["children"]) == ["Reihen", "Integrale"]

# into another deck, with its subdecks; the id (and so the learning state) stays
core.add_note("Basic", "Analysis::Integrale", {"Front": "∫", "Back": "x"})
assert core.move_deck(ids["Analysis"], ids["SWEN"]) == 1
assert col.decks.name(ids["Analysis::Integrale"]) == "SWEN::Analysis::Integrale"
assert core.search("deck:SWEN::Analysis::Integrale")
# back to the top level
assert core.move_deck(ids["Analysis"], None) == 1
assert col.decks.name(ids["Analysis"]) == "Analysis"

# into its own subdeck: nothing happens; a taken name gets a "+"
assert core.move_deck(ids["Analysis"], ids["Analysis::Reihen"]) == 0
other = core.create_deck("DBIS::Reihen")
core.move_deck(other, ids["Analysis"])
assert col.decks.name(other) == "Analysis::Reihen+"

core._close()
print("ok")
