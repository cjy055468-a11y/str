;BEGIN FRAGMENT CODE - Do not edit anything between this and the end comment
;NEXT FRAGMENT INDEX 11
Scriptname _M_QuestKillScript Extends Quest Hidden

;BEGIN ALIAS PROPERTY Dungeon
;ALIAS PROPERTY TYPE LocationAlias
LocationAlias Property Alias_Dungeon Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Steward
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_Steward Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Hold
;ALIAS PROPERTY TYPE LocationAlias
LocationAlias Property Alias_Hold Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY target
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_target Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Jarl
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_Jarl Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY MissiveBoard
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_MissiveBoard Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Missive
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_Missive Auto
;END ALIAS PROPERTY

;BEGIN FRAGMENT Fragment_2
Function Fragment_2()
    STRMissivesBridge.StageChanged(GetFormID(), GetStage())
;BEGIN CODE
If STRMissivesBridge.IsPersonalQuest(GetFormID())
    SetObjectiveCompleted(20)
EndIf
if(Alias_Steward.GetRef())
If STRMissivesBridge.IsPersonalQuest(GetFormID())
    SetObjectiveDisplayed(40)
EndIf
else
If STRMissivesBridge.IsPersonalQuest(GetFormID())
    SetObjectiveDisplayed(41)
EndIf
endIf
;END CODE
EndFunction
;END FRAGMENT

;BEGIN FRAGMENT Fragment_0
Function Fragment_0()
    STRMissivesBridge.StageChanged(GetFormID(), GetStage())
;BEGIN CODE
If STRMissivesBridge.IsPersonalQuest(GetFormID())
    SetObjectiveDisplayed(20)
EndIf

if(Alias_Target.GetActorRef().IsDead())
SetStage(40)
endIf
;END CODE
EndFunction
;END FRAGMENT

;BEGIN FRAGMENT Fragment_7
Function Fragment_7()
    STRMissivesBridge.StageChanged(GetFormID(), GetStage())
;BEGIN CODE
If STRMissivesBridge.IsPersonalQuest(GetFormID())
    FailAllObjectives()
EndIf
SetStage(110)
;END CODE
EndFunction
;END FRAGMENT

;BEGIN FRAGMENT Fragment_9
Function Fragment_9()
    STRMissivesBridge.StageChanged(GetFormID(), GetStage())
;BEGIN CODE
STRMissivesBridge.RemovePosting(Self, Alias_Missive, Alias_MissiveBoard)

Stop()
;END CODE
EndFunction
;END FRAGMENT

;BEGIN FRAGMENT Fragment_4
Function Fragment_4()
    STRMissivesBridge.StageChanged(GetFormID(), GetStage())
;BEGIN CODE
If STRMissivesBridge.IsPersonalQuest(GetFormID())
    CompleteAllObjectives()
EndIf
If STRMissivesBridge.IsPersonalQuest(GetFormID())
    Game.GetPlayer().AddItem(Gold001, GoldReward.GetValue() as int)
EndIf
SetStage(110)
;END CODE
EndFunction
;END FRAGMENT

;END FRAGMENT CODE - Do not edit anything between this and the begin comment

MiscObject Property Gold001  Auto  

GlobalVariable Property GoldReward  Auto  
