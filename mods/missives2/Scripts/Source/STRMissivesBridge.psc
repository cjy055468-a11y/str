Scriptname STRMissivesBridge Hidden
Bool Function IsConnected() Global Native
Bool Function IsAuthority() Global Native
Bool Function CanGenerate(Int questId) Global Native
Bool Function IsPersonalQuest(Int questId) Global Native
Bool Function Claim(Int questId) Global Native
Function StageChanged(Int questId, Int stageId) Global Native
Function OpenBoard(Int boardId, Int controllerId) Global Native
Function CloseBoard(Int boardId) Global Native
Int Function GetState(Int questId) Global Native
Int Function GetPostingAlias(Int questId) Global Native
Int Function GetBoardAlias(Int questId) Global Native
Int Function GetRecipient(Int questId) Global Native
Function Released(Int questId) Global Native
Function BoardChanged(Int boardId) Global Native

; Inventory operations deliberately run through Papyrus's own VM marshalling.
; Holder identity is recorded by the original alias container-change event.
Function RefreshPosting(Quest mission) Global
    If !mission || !IsConnected()
        Return
    EndIf
    Int questId = mission.GetFormID()
    Int status = GetState(questId)
    If status < 0 || status == 1
        Return
    EndIf
    If status >= 4 && !mission.IsRunning()
        Released(questId)
        Return
    EndIf
    ReferenceAlias postAlias = mission.GetAlias(GetPostingAlias(questId)) as ReferenceAlias
    ReferenceAlias boardAlias = mission.GetAlias(GetBoardAlias(questId)) as ReferenceAlias
    If !postAlias || !boardAlias
        Return
    EndIf
    ObjectReference letter = postAlias.GetReference()
    ObjectReference board = boardAlias.GetReference()
    If !letter || !board
        Return
    EndIf
    ObjectReference holder = GetPostingHolder(postAlias)
    If !holder && status == 0 && board.GetItemCount(letter) > 0
        ; Migration of an already running offline posting. New postings always
        ; record the exact reference transfer through OnContainerChanged.
        holder = board
    EndIf
    Actor player = Game.GetPlayer()
    If status == 0
        If holder == player
            Claim(questId)
        ElseIf holder != board
            letter.Enable()
            board.AddItem(letter, 1, True)
        EndIf
    ElseIf status == 2
        If holder == board
            board.RemoveItem(letter, 1, True, player)
        ElseIf holder != player
            letter.Enable()
            player.AddItem(letter, 1, True)
        EndIf
        If mission.GetStage() < 20
            mission.SetStage(20)
        EndIf
    Else
        If holder == board
            board.RemoveItem(letter, 1, True)
        ElseIf holder == player && !IsPersonalQuest(questId)
            player.RemoveItem(letter, 1, True)
        EndIf
        If status >= 4
            mission.Stop()
            Released(questId)
        EndIf
    EndIf
EndFunction

ObjectReference Function GetPostingHolder(ReferenceAlias postAlias) Global
    _M_AliasMissiveScript ordinary = postAlias as _M_AliasMissiveScript
    If ordinary
        Return ordinary.STRGetHolder()
    EndIf
    _M_AliasMissiveDeliverScript delivery = postAlias as _M_AliasMissiveDeliverScript
    If delivery
        Return delivery.STRGetHolder()
    EndIf
    Return None
EndFunction

Function RemovePosting(Quest mission, ReferenceAlias postAlias, ReferenceAlias boardAlias) Global
    If !postAlias || !boardAlias
        Return
    EndIf
    ObjectReference letter = postAlias.GetReference()
    ObjectReference board = boardAlias.GetReference()
    If !letter || !board
        Return
    EndIf
    ObjectReference holder = GetPostingHolder(postAlias)
    If IsConnected()
        If holder == board
            board.RemoveItem(letter, 1, True)
        ElseIf holder == Game.GetPlayer() && IsPersonalQuest(mission.GetFormID())
            Game.GetPlayer().RemoveItem(letter, 1, True)
        EndIf
    Else
        If board.GetItemCount(letter) > 0
            board.RemoveItem(letter)
        ElseIf Game.GetPlayer().GetItemCount(letter) > 0
            Game.GetPlayer().RemoveItem(letter)
        EndIf
    EndIf
EndFunction
