"""Archive: a deck leaves "Heute", its cards are paused, restoring brings back only what the archive paused."""

import tempfile
from pathlib import Path

from muisti.core import Core

core = Core(str(Path(tempfile.mkdtemp()) / "c.anki2"))
col = core._col
for deck, front in [("Mathe", "1+1"), ("Mathe::Analysis", "lim"), ("Mathe::Analysis", "dx"), ("Spanisch", "hola")]:
    core.add_note("Basic", deck, {"Front": front, "Back": "?"})
mathe, analysis = col.decks.id("Mathe"), col.decks.id("Mathe::Analysis")
mine = col.find_cards('dx')
core.suspend(mine)  # suspended by hand before archiving: must stay suspended afterwards

assert core.archive_deck(mathe) == 2  # 1+1 and lim, dx was already suspended
assert core.archive_deck(mathe) == 0  # twice is a no-op
tree = {d["name"]: d for d in core.decks()}
assert tree["Mathe"]["archived"] and tree["Mathe"]["children"][0]["archived"]  # subdecks go along
assert not tree["Spanisch"]["archived"]
assert tree["Mathe"]["new"] == 0 and core.stats()["due_today"] == 1  # nothing from Mathe comes due

assert core.restore_deck(mathe) == 2
assert not {d["name"]: d for d in core.decks()}["Mathe"]["archived"]
assert core.stats()["due_today"] == 3
assert col.get_card(mine[0]).queue == -1  # still suspended by hand

# a deleted card doesn't break restoring; archiving a subdeck alone works too
core.archive_deck(analysis)
core.delete_notes([col.get_card(col.find_cards('lim')[0]).nid])
assert core.restore_deck(analysis) == 0
assert core.restore_deck(analysis) == 0  # not archived: no-op

# filtered decks can't be archived
fid = core.create_filtered_deck("Pauken", "deck:Spanisch")
try:
    core.archive_deck(fid)
    raise AssertionError("filtered deck archived")
except ValueError:
    pass

core._close()
print("ok")
