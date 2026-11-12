#!/usr/bin/env python3
"""Source-level guard for the rebuilt Missives board protocol and triggers."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="TiltedEvolution source checkout")
    parser.add_argument("--mod", type=Path, default=Path("mods/missives-board-sync"))
    args = parser.parse_args()
    source = args.source.resolve()
    mod = args.mod.resolve()
    script_dir = mod / "Scripts" / "Source"
    entries = json.loads((mod / "catalog.json").read_text(encoding="utf-8"))
    scripts = list(script_dir.glob("*.psc"))
    require(len(scripts) == 18, f"expected 18 fresh/retained Missives script sources, got {len(scripts)}")
    require(not (script_dir / "STRMissivesBridge.psc").exists(), "old Missives bridge source is still packaged")
    require(not list(mod.rglob("*.esp")) and not list(mod.rglob("*.pex")),
            "source candidate must not ship an old ESP or pretend-uncompiled PEX files")
    require(len(entries) == 264, "catalog must contain all 264 Missives posting aliases")
    require(len({item["quest"] for item in entries}) == 264, "duplicate quest forms in catalog")
    require(all(item["posting_alias"] >= 0 and item["board_alias"] >= 0 for item in entries), "invalid alias index")

    catalog = (source / "Code/client/ModCompat/MissiveBoardCatalog.h").read_text(encoding="utf-8")
    raw_rows = re.findall(
        r"\{0x([0-9a-fA-F]+)u, 0x([0-9a-fA-F]+)u, (\d+)u, (\d+)u\}", catalog
    )
    rows = [(int(row[0], 16), int(row[1], 16), int(row[2]), int(row[3])) for row in raw_rows]
    require(len(rows) == 264, "native catalog row count differs from ESP extraction")
    require(rows == [
        (item["quest"], item["book"], item["posting_alias"], item["board_alias"])
        for item in entries
    ], "native catalog differs from ESP extraction")

    bridge_psc = (script_dir / "STRMissivesBoardBridge.psc").read_text(encoding="utf-8")
    bridge_cpp = (source / "Code/client/ModCompat/MissiveBoardBridge.cpp").read_text(encoding="utf-8")
    declared = set(re.findall(
        r"\b(?:Bool\s+|Int\s+)?Function\s+(\w+)\s*\([^\n]*\)\s+Global\s+Native\b", bridge_psc
    ))
    bound = set(re.findall(r'\{"(\w+)",O::', bridge_cpp))
    require(declared == bound, f"Papyrus/native bridge mismatch: PSC-only={sorted(declared-bound)}, native-only={sorted(bound-declared)}")

    native_calls: set[str] = set()
    for script in script_dir.glob("*.psc"):
        native_calls.update(re.findall(r"STRMissivesBoardBridge\.(\w+)\s*\(", script.read_text(encoding="utf-8")))
    available = declared | {"RefreshPosting", "STRMoveLocalPosting", "STRRemoveLocalPosting"}
    require(native_calls <= available, f"unresolved bridge calls: {sorted(native_calls-available)}")

    activator = (script_dir / "_M_ActivatorScript.psc").read_text(encoding="utf-8")
    alias_claim = (script_dir / "_M_AliasMissiveScript.psc").read_text(encoding="utf-8")
    alias_delivery = (script_dir / "_M_AliasMissiveDeliverScript.psc").read_text(encoding="utf-8")
    require("Event OnTriggerEnter" in activator and "OpenBoard(" in activator, "board enter trigger is not connected")
    require("Event OnTriggerLeave" in activator and "CloseBoard(" in activator, "board leave trigger is not connected")
    require("IsBoardReady(" in activator and "IsBoardAuthority(" in activator, "board handshake/election is not checked")
    require("STRMaintainNonEmptyBoard()" in activator, "empty-board recovery path is missing")
    require(all(f"STRRefreshList({name})" in activator for name in ("QuestsLow", "QuestsMed", "QuestsHigh", "QuestsVeryHigh"))
            and "If STRInside" in activator and "RegisterForSingleUpdate(1.0)" in activator,
            "an open physical board does not keep polling listing changes")
    refresh_posting = bridge_psc[bridge_psc.index("Function RefreshPosting"):bridge_psc.index("Function STRMoveLocalPosting")]
    require("status == 1 || status == 3" in refresh_posting and "STRRemoveLocalPosting(letter, sourceBoard, targetBoard)" in refresh_posting,
            "a remotely claimed or retired posting is not removed from the local physical board")
    client_service = (source / "Code/client/Services/Generic/MissiveBoardService.cpp").read_text(encoding="utf-8")
    server_service = (source / "Code/server/Services/MissiveBoardService.cpp").read_text(encoding="utf-8")
    require("NotifyMissivesBoard::Operation::Taken ? 1" in client_service
            and "SetListing(questId, boardId, acMessage.Listing.Id, state)" in client_service
            and "Broadcast(*record, NotifyMissivesBoard::Operation::Taken)" in server_service,
            "a board claim is not broadcast and reflected in every client's local listing state")
    require("Claim(" in alias_claim and "GetPostingStatus(" in alias_claim, "posting pickup trigger is not connected")
    require("Claim(" in alias_delivery and "GetPostingStatus(" in alias_delivery, "delivery posting pickup trigger is not connected")
    for name, alias in (("ordinary", alias_claim), ("delivery", alias_delivery)):
        require(re.search(
            r"Int status\s*=\s*STRMissivesBoardBridge\.GetPostingStatus\(mission\.GetFormID\(\), board\.GetFormID\(\)\)"
            r"[\s\S]*?If status == 0[\s\S]*?Claim\(mission\.GetFormID\(\), board\.GetFormID\(\)\)"
            r"[\s\S]*?EndIf[\s\S]*?If status <= 0[\s\S]*?RegisterForSingleUpdate\(1\.0\)", alias
        ) is not None,
                f"{name} pickup path does not retry unconfirmed claims")
    require("stage < 20 && status <= 0 && letter && Game.GetPlayer().GetItemCount(letter) > 0" in bridge_psc,
            "picked posting may be moved off the player before the listing/claim response arrives")
    require(re.search(r"If status < 0 && IsBoardAuthority\(boardId\) && CanGenerate\(questId, boardId\)[\s\S]*?Publish\(questId, boardId\)", bridge_psc) is not None,
            "the board authority does not retry an unacknowledged publication while the picked posting is pending")
    require("stage < 20 && status <= 0 && letter && Game.GetPlayer().GetItemCount(letter) > 0" in bridge_psc,
            "picked posting may be moved off the player before the listing/claim response arrives")
    require("If status == 2" in bridge_psc and "mission.SetStage(20)" in bridge_psc, "only-granted claimant path is missing")
    require("status == 1 || status == 3" in bridge_psc and "mission.Stop()" in bridge_psc, "non-claimant cleanup path is missing")

    require("IsLocalPublisher(questId, boardId)" in refresh_posting,
            "a stopped guest shadow quest can be mistaken for an expired authority posting")
    require("AcknowledgeRemoval(questId, boardId)" in refresh_posting,
            "physical posting removal is not acknowledged")
    require("s_listings[key] = {aId, aStatus}" in bridge_cpp
            and "case Operation::AcknowledgeRemoval:" in bridge_cpp
            and "if (state == 3)" in bridge_cpp,
            "retirement must survive until script cleanup and preserve newer/claimed rows")
    require("listing.Status = 3" in bridge_cpp,
            "snapshot replacement must retain removed rows for physical cleanup")
    require(all("ObjectReference STRClaimBoard" in alias
                and "STRClaimBoard = board" in alias
                and "ObjectReference board = STRClaimBoard" in alias
                and "!STRMissivesBoardBridge.IsBoardReady(board.GetFormID())" in alias
                for alias in (alias_claim, alias_delivery)),
            "claim retries must keep the actual board and wait through incomplete snapshots")
    require("m_pendingFinish[*it] = now" in client_service,
            "completed personal claims must retry until server retirement is confirmed")

    listing = (source / "Code/encoding/Structs/MissiveBoardListing.h").read_text(encoding="utf-8")
    require(set(re.findall(r"^\s+(?:uint64_t|GameId)\s+(\w+)", listing, re.M)) == {"Id", "Board", "Quest", "Book"},
            "wire listing contains task state or lacks a public-line identifier")
    request = (source / "Code/encoding/Messages/RequestMissivesBoard.h").read_text(encoding="utf-8")
    notify = (source / "Code/encoding/Messages/NotifyMissivesBoard.h").read_text(encoding="utf-8")
    protocol_declarations = re.sub(r"//.*", "", request + notify + listing)
    require(not re.search(r"Progress|Objective|Reward|Stage|Alias|Global", protocol_declarations, re.I),
            "task objective/progress fields leaked into board protocol")
    ledger = (source / "Code/server/Game/Inventory/MissiveBoardLedger.h").read_text(encoding="utf-8")
    require("Key(acListing.Board, acListing.Quest)" in ledger and "Listing.Board != acBoard" in ledger,
            "claim identity is not scoped to the physical board")

    quest_service = (source / "Code/client/Services/Generic/QuestService.cpp").read_text(encoding="utf-8")
    refs = (source / "Code/client/Games/Skyrim/TESObjectREFR.cpp").read_text(encoding="utf-8")
    object_service = (source / "Code/client/Services/Generic/ObjectService.cpp").read_text(encoding="utf-8")
    inventory_service = (source / "Code/client/Services/Generic/InventoryService.cpp").read_text(encoding="utf-8")
    require("MissiveBoardSync::IsMissivesForm" in quest_service, "Missives quest stages are still eligible for synchronization")
    require("MissiveBoardSync::IsPersonalQuestData" in refs and "arEntry.IsPersonalQuestItem" in refs,
            "personal Missives objective item isolation is missing")
    require("MissiveBoardSync::IsBoard" in object_service and "MissiveBoardSync::IsBoard" in inventory_service,
            "ordinary board object/inventory sync is still enabled")
    bsscript = (source / "Code/client/Games/Misc/BSScript.cpp").read_text(encoding="utf-8")
    client_world = (source / "Code/client/World.cpp").read_text(encoding="utf-8")
    server_world = (source / "Code/server/World.cpp").read_text(encoding="utf-8")
    require("RegisterMissiveBoardBridge" in bsscript and "MissiveBoardService" in client_world and "MissiveBoardService" in server_world,
            "native Papyrus/server/client services are not all registered")
    require("m_openBoards" in client_service and "retrying open for board" in client_service
            and "RequestMissivesBoard::Operation::Open" in client_service,
            "an open board does not retry until its server snapshot completes")
    open_handler = client_service[client_service.index("if (acEvent.Action == O::Open || acEvent.Action == O::Close)"):]
    open_tracking = open_handler.find("m_openBoards[acEvent.Quest]")
    open_mapping = open_handler.find("GetServerModId(acEvent.Quest")
    require(open_tracking >= 0 and open_mapping >= 0 and open_tracking < open_mapping,
            "a board open can be lost before its local-to-server form mapping is ready")
    require("retry.NextRequest = now + std::chrono::seconds(2);\n        if (sent)" in client_service,
            "failed board-open sends are not rate-limited and retried")
    require("cannot map server board id" in client_service and "cannot map server quest id" in client_service,
            "unmapped incoming snapshot IDs are silently discarded")

    old_active = [
        source / "Code/client/Services/Generic/MissivesService.cpp",
        source / "Code/server/Services/MissivesService.cpp",
        source / "Code/encoding/Structs/MissivesData.h",
        mod.parent / "missives2",
    ]
    require(not any(path.exists() for path in old_active), "old Missives sharing implementation is still active in the deliverable")

    print(json.dumps({
        "catalog_entries": len(entries),
        "papyrus_native_functions": len(declared),
        "trigger_integration": "source-verified",
        "board_claim_scope": "physical-board-id",
        "claim_retry": "one-second-until-server-result",
        "snapshot_retry": "reopens-until-snapshot-end",
        "task_progress_wire_fields": 0,
        "personal_task_item_filter": "present",
        "old_board_implementation": "absent",
        "gameplay_two-client_test": "not-run-here",
    }, indent=2))


if __name__ == "__main__":
    main()
