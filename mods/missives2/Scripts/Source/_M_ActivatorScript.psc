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

float LastUpdate = -100.0

bool STRInside = false

Event OnTriggerEnter(ObjectReference akActionRef)
    If akActionRef == Game.GetPlayer()
        STRInside = True
        If STRMissivesBridge.IsConnected()
            STRMissivesBridge.OpenBoard(MissiveBoard.GetFormID(), GetFormID())
            RegisterForSingleUpdate(0.2)
        Else
            STRUpdateBoard()
        EndIf
    EndIf
EndEvent

Event OnTriggerLeave(ObjectReference akActionRef)
    If akActionRef == Game.GetPlayer()
        STRInside = False
        STRMissivesBridge.CloseBoard(MissiveBoard.GetFormID())
    EndIf
EndEvent

Event OnUpdate()
    If STRMissivesBridge.IsConnected()
        If STRMissivesBridge.IsAuthority()
            STRUpdateBoard()
        EndIf
        STRRefreshList(QuestsLow)
        STRRefreshList(QuestsMed)
        STRRefreshList(QuestsHigh)
        STRRefreshList(QuestsVeryHigh)
        STRMissivesBridge.BoardChanged(MissiveBoard.GetFormID())
        If STRInside
            RegisterForSingleUpdate(0.2)
        EndIf
    EndIf
EndEvent

Function STRRefreshList(FormList missions)
    Int i = 0
    While i < missions.GetSize()
        STRMissivesBridge.RefreshPosting(missions.GetAt(i) as Quest)
        i += 1
    EndWhile
EndFunction

Function STRUpdateBoard()
	if(GameDaysPassed.GetValue() > LastUpdate + RefreshRate.GetValue())
		Debug.Trace("Missives: Update Trigger Triggered")
		LastUpdate = GameDaysPassed.GetValue()
		
		MissiveBoard.BlockActivation(true)

		UpdateQuests(QuestChanceLow.GetValue(), QuestsLow)
		UpdateQuests(QuestChanceMed.GetValue(), QuestsMed)
		UpdateQuests(QuestChanceHigh.GetValue(), QuestsHigh)
		UpdateQuests(QuestChanceVeryHigh.GetValue(), QuestsVeryHigh)

		MissiveBoard.BlockActivation(false)

		Debug.Trace("Missives: Quests Updated")
	endIf

EndFunction

Function UpdateQuests(float QuestChance, FormList QuestList)
	int QuestIndex = 0
	while(QuestIndex < QuestList.GetSize())
		if(Utility.RandomInt() < QuestChance)
			Quest MissiveQuest = QuestList.GetAt(QuestIndex) as Quest
            If !STRMissivesBridge.IsConnected() || STRMissivesBridge.CanGenerate(MissiveQuest.GetFormID(), MissiveBoard.GetFormID())

			;If the quest isn't running, start it up
			;If the quest is running, but hasn't been picked up by the player, reset it
			if(!MissiveQuest.IsRunning())
				bool Started = MissiveQuest.Start()
				if(Started)
					Debug.Trace("Missives: Starting Quest " + QuestIndex + ":" + MissiveQuest + ", in Quest List: " + QuestList)
				else
					Debug.Trace("Missives: Failed to Start Quest " + QuestIndex + ":" + MissiveQuest + ", in Quest List: " + QuestList)
				endIf
			elseif(MissiveQuest.GetStage() == 0)
				Debug.Trace("Missives: Stoping Quest " + QuestIndex + ":" + MissiveQuest + ", in Quest List: " + QuestList)
				MissiveQuest.SetStage(110)
			endIf
		endIf
            EndIf
		QuestIndex += 1
	endWhile
endFunction