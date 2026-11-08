Scriptname STRMissivesBoardBridge Hidden Native

Bool Function IsConnected() Global Native
Bool Function IsReady() Global Native
Bool Function IsBoardReady(Int boardId) Global Native
Bool Function IsBoardAuthority(Int boardId) Global Native
Bool Function CanGenerate(Int questId, Int boardId) Global Native
Bool Function IsPersonalQuest(Int questId) Global Native
Int Function GetPostingStatus(Int questId, Int boardId) Global Native
Int Function GetPostingCount(Int boardId) Global Native
Int Function GetPostingAlias(Int questId) Global Native
Int Function GetBoardAlias(Int questId) Global Native
Function OpenBoard(Int boardId, Int controllerId) Global Native
Function CloseBoard(Int boardId) Global Native
Function Publish(Int questId, Int boardId) Global Native
Bool Function Claim(Int questId, Int boardId) Global Native
Function Finish(Int questId, Int boardId) Global Native

Function RefreshPosting(Quest mission, ObjectReference targetBoard) Global
    If !mission || !targetBoard || !IsConnected() || !IsBoardReady(targetBoard.GetFormID())
        Return
    EndIf

    Int questId = mission.GetFormID()
    Int boardId = targetBoard.GetFormID()
    Int stage = mission.GetStage()
    If IsPersonalQuest(questId) && stage >= 20 && stage < 103
        Return
    EndIf

    Int postingId = GetPostingAlias(questId)
    Int boardAliasId = GetBoardAlias(questId)
    If postingId < 0 || boardAliasId < 0
        Return
    EndIf
    ReferenceAlias postingAlias = mission.GetAlias(postingId) as ReferenceAlias
    ReferenceAlias boardAlias = mission.GetAlias(boardAliasId) as ReferenceAlias
    If !postingAlias || !boardAlias
        Return
    EndIf
    ObjectReference letter = postingAlias.GetReference()
    ObjectReference sourceBoard = boardAlias.GetReference()

    Int status = GetPostingStatus(questId, boardId)
    If status == 0 && (stage >= 103 || !mission.IsRunning())
        Finish(questId, boardId)
        STRRemoveLocalPosting(letter, sourceBoard, targetBoard)
        Return
    EndIf
    If status == 2
        If mission.IsRunning() && stage < 20
            Debug.Trace("STR Missives board: server confirmed local claim for quest " + questId)
            mission.SetStage(20)
        EndIf
        Return
    EndIf

    If status == 0
        If !mission.IsRunning()
            mission.Start()
            Return
        EndIf
        If stage >= 20
            Return
        EndIf
        If letter && Game.GetPlayer().GetItemCount(letter) > 0
            ; Wait for the server's atomic claim result. Leave the picked letter
            ; with its claimant until the board service replies.
            Return
        EndIf
        STRMoveLocalPosting(letter, sourceBoard, targetBoard)
        Return
    EndIf

    If status == 1 || status == 3
        STRRemoveLocalPosting(letter, sourceBoard, targetBoard)
        If mission.IsRunning()
            ; Stop avoids running any task or reward stage on a non-claimant.
            mission.Stop()
        EndIf
        Return
    EndIf

    If IsBoardAuthority(boardId)
        If mission.IsRunning() && stage == 0 && letter && CanGenerate(questId, boardId)
            STRMoveLocalPosting(letter, sourceBoard, targetBoard)
            Publish(questId, boardId)
        EndIf
    ElseIf mission.IsRunning() && stage == 0
        STRRemoveLocalPosting(letter, sourceBoard, targetBoard)
        mission.Stop()
    EndIf
EndFunction

Function STRMoveLocalPosting(ObjectReference letter, ObjectReference sourceBoard, ObjectReference targetBoard) Global
    If !letter || !targetBoard
        Return
    EndIf
    If sourceBoard && sourceBoard != targetBoard && sourceBoard.GetItemCount(letter) > 0
        sourceBoard.RemoveItem(letter, 1, True)
    EndIf
    If Game.GetPlayer().GetItemCount(letter) > 0
        Game.GetPlayer().RemoveItem(letter, 1, True)
    EndIf
    If targetBoard.GetItemCount(letter) <= 0
        targetBoard.AddItem(letter, 1, True)
    EndIf
EndFunction

Function STRRemoveLocalPosting(ObjectReference letter, ObjectReference sourceBoard, ObjectReference targetBoard) Global
    If !letter
        Return
    EndIf
    If targetBoard && targetBoard.GetItemCount(letter) > 0
        targetBoard.RemoveItem(letter, 1, True)
    EndIf
    If sourceBoard && sourceBoard != targetBoard && sourceBoard.GetItemCount(letter) > 0
        sourceBoard.RemoveItem(letter, 1, True)
    EndIf
    If Game.GetPlayer().GetItemCount(letter) > 0
        Game.GetPlayer().RemoveItem(letter, 1, True)
    EndIf
EndFunction
