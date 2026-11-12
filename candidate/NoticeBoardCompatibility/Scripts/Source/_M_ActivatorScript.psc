Scriptname _M_ActivatorScript extends ObjectReference

GlobalVariable Property QuestChanceLow Auto
GlobalVariable Property QuestChanceMed Auto
GlobalVariable Property QuestChanceHigh Auto
GlobalVariable Property QuestChanceVeryHigh Auto
FormList Property QuestsLow Auto
FormList Property QuestsMed Auto
FormList Property QuestsHigh Auto
FormList Property QuestsVeryHigh Auto
GlobalVariable Property GameDaysPassed Auto
GlobalVariable Property RefreshRate Auto
ObjectReference Property MissiveBoard Auto

Float LastUpdate = -100.0
Bool NoticeInside = False
Bool NoticeWasOnline = False
Int NoticeCursor = 0
Int NoticeRefreshTicks = 30
Int NoticePollGeneration = 0
Bool NoticeSeeded = False

Event OnInit()
    RegisterForSingleUpdate(0.5)
EndEvent

Event OnLoad()
    RegisterForSingleUpdate(0.5)
EndEvent

Event OnCellAttach()
    RegisterForSingleUpdate(0.5)
EndEvent

Event OnCellDetach()
    If NoticeInside && MissiveBoard && STRNoticeBridge.IsConnected()
        STRNoticeBridge.CloseBoard(MissiveBoard.GetFormID())
    EndIf
    NoticeInside = False
    NoticePollGeneration += 1
    UnregisterForUpdate()
EndEvent

Event OnTriggerEnter(ObjectReference akActionRef)
    If akActionRef == Game.GetPlayer() && !NoticeInside
        NoticeInside = True
        PollBoard()
    EndIf
EndEvent

Event OnTrigger(ObjectReference akActionRef)
    If akActionRef == Game.GetPlayer() && !NoticeInside
        NoticeInside = True
        PollBoard()
    EndIf
EndEvent

Event OnTriggerLeave(ObjectReference akActionRef)
    If akActionRef == Game.GetPlayer()
        NoticeInside = False
        NoticePollGeneration += 1
        If MissiveBoard && STRNoticeBridge.IsConnected()
            STRNoticeBridge.CloseBoard(MissiveBoard.GetFormID())
        EndIf
        UnregisterForUpdate()
    EndIf
EndEvent

Event OnUpdate()
    If NoticeInside && MissiveBoard
        PollBoard()
    EndIf
EndEvent

Function PollBoard()
    NoticePollGeneration += 1
    Int generation = NoticePollGeneration
    ; WaitMenuMode continues while the container menu is open. A generation
    ; invalidates older saved/re-entered loops without multiplying pollers.
    While NoticeInside && MissiveBoard && generation == NoticePollGeneration
        RefreshBoard()
        Utility.WaitMenuMode(1.0)
    EndWhile
EndFunction

Function RefreshBoard()
    Bool online = STRNoticeBridge.IsConnected()
    Int boardId = MissiveBoard.GetFormID()
    If online
        If !NoticeWasOnline || !STRNoticeBridge.IsBoardReady(boardId)
            STRNoticeBridge.OpenBoard(boardId)
        EndIf
        If STRNoticeBridge.IsBoardReady(boardId)
            RenderList(QuestsLow, True)
            RenderList(QuestsMed, True)
            RenderList(QuestsHigh, True)
            RenderList(QuestsVeryHigh, True)
            If STRNoticeBridge.IsBoardAuthority(boardId)
                FillPublicBoard()
            EndIf
        EndIf
    Else
        ; Proxy slips are only public online notices, never solo task letters.
        RenderList(QuestsLow, False)
        RenderList(QuestsMed, False)
        RenderList(QuestsHigh, False)
        RenderList(QuestsVeryHigh, False)
        UpdateOfflineBoard()
    EndIf
    NoticeWasOnline = online
EndFunction

Function RenderList(FormList missions, Bool online)
    If !missions
        Return
    EndIf
    Int index = 0
    While index < missions.GetSize()
        Quest mission = missions.GetAt(index) as Quest
        If mission
            Int questId = mission.GetFormID()
            Form proxy = Game.GetForm(STRNoticeBridge.GetProxyBook(questId))
            If proxy
                Int count = MissiveBoard.GetItemCount(proxy)
                Int noticeStatus = -1
                If online
                    noticeStatus = STRNoticeBridge.GetNoticeState(questId, MissiveBoard.GetFormID())
                EndIf
                If noticeStatus == 0
                    If count == 0
                        MissiveBoard.AddItem(proxy, 1, True)
                    ElseIf count > 1
                        MissiveBoard.RemoveItem(proxy, count - 1, True)
                    EndIf
                ElseIf count > 0
                    MissiveBoard.RemoveItem(proxy, count, True)
                EndIf
            EndIf
            If online && !STRNoticeBridge.IsOriginalBookProtected(questId)
                Form original = Game.GetForm(STRNoticeBridge.GetOriginalBook(questId))
                If original
                    Int originals = MissiveBoard.GetItemCount(original)
                    If originals > 0
                        MissiveBoard.RemoveItem(original, originals, True)
                    EndIf
                EndIf
            EndIf
        EndIf
        index += 1
    EndWhile
EndFunction

Function FillPublicBoard()
    Int boardId = MissiveBoard.GetFormID()
    Int available = STRNoticeBridge.GetPostingCount(boardId)
    If available >= 6
        Return
    EndIf
    NoticeRefreshTicks += 1
    Bool allowRecycle = NoticeRefreshTicks >= 30
    If allowRecycle
        NoticeRefreshTicks = 0
    EndIf
    Int total = QuestsLow.GetSize() + QuestsMed.GetSize() + QuestsHigh.GetSize() + QuestsVeryHigh.GetSize()
    If !NoticeSeeded && total > 0
        NoticeCursor = Utility.RandomInt(0, total - 1)
        NoticeSeeded = True
    EndIf
    Int visited = 0
    Int offered = 0
    While visited < total && offered < 6 - available
        If NoticeCursor >= total
            NoticeCursor = 0
        EndIf
        Quest mission = GetTemplate(NoticeCursor)
        NoticeCursor += 1
        visited += 1
        If mission
            Int noticeStatus = STRNoticeBridge.GetNoticeState(mission.GetFormID(), boardId)
            ; Public availability cannot depend on the publishing visitor's
            ; personal tasks. Each claimant is checked separately on pickup.
            If noticeStatus < 0 || noticeStatus == 5 || (noticeStatus == 3 && allowRecycle)
                STRNoticeBridge.Offer(mission.GetFormID(), boardId)
                offered += 1
            EndIf
        EndIf
    EndWhile
EndFunction

Quest Function GetTemplate(Int index)
    If index < QuestsLow.GetSize()
        Return QuestsLow.GetAt(index) as Quest
    EndIf
    index -= QuestsLow.GetSize()
    If index < QuestsMed.GetSize()
        Return QuestsMed.GetAt(index) as Quest
    EndIf
    index -= QuestsMed.GetSize()
    If index < QuestsHigh.GetSize()
        Return QuestsHigh.GetAt(index) as Quest
    EndIf
    index -= QuestsHigh.GetSize()
    If index < QuestsVeryHigh.GetSize()
        Return QuestsVeryHigh.GetAt(index) as Quest
    EndIf
    Return None
EndFunction

Function UpdateOfflineBoard()
    If GameDaysPassed.GetValue() <= LastUpdate + RefreshRate.GetValue()
        Return
    EndIf
    LastUpdate = GameDaysPassed.GetValue()
    MissiveBoard.BlockActivation(True)
    UpdateQuests(QuestChanceLow.GetValue(), QuestsLow)
    UpdateQuests(QuestChanceMed.GetValue(), QuestsMed)
    UpdateQuests(QuestChanceHigh.GetValue(), QuestsHigh)
    UpdateQuests(QuestChanceVeryHigh.GetValue(), QuestsVeryHigh)
    MissiveBoard.BlockActivation(False)
EndFunction

; Only the original offline mode starts tasks while populating a board.
Function UpdateQuests(Float chance, FormList missions)
    Int index = 0
    While index < missions.GetSize()
        If Utility.RandomInt() < chance
            Quest mission = missions.GetAt(index) as Quest
            If mission && !STRNoticeBridge.IsClaimPending(mission.GetFormID())
                If !mission.IsRunning()
                    mission.Start()
                ElseIf mission.GetStage() == 0
                    mission.SetStage(110)
                EndIf
            EndIf
        EndIf
        index += 1
    EndWhile
EndFunction
