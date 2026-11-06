;BEGIN FRAGMENT CODE - Do not edit anything between this and the end comment
;NEXT FRAGMENT INDEX 10
Scriptname _M_QuestTrackFugitiveScript Extends Quest Hidden

;BEGIN ALIAS PROPERTY Inn2
;ALIAS PROPERTY TYPE LocationAlias
LocationAlias Property Alias_Inn2 Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Missive
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_Missive Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY OtherHold
;ALIAS PROPERTY TYPE LocationAlias
LocationAlias Property Alias_OtherHold Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Hold
;ALIAS PROPERTY TYPE LocationAlias
LocationAlias Property Alias_Hold Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY InnMarker2
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_InnMarker2 Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Steward
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_Steward Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Inn1
;ALIAS PROPERTY TYPE LocationAlias
LocationAlias Property Alias_Inn1 Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Criminal
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_Criminal Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Jarl
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_Jarl Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY InnMarker1
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_InnMarker1 Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY MissiveBoard
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_MissiveBoard Auto
;END ALIAS PROPERTY

;BEGIN FRAGMENT Fragment_0
Function Fragment_0()
    STRMissivesBridge.StageChanged(GetFormID(), GetStage())
;BEGIN CODE
If STRMissivesBridge.IsPersonalQuest(GetFormID())
    SetObjectiveDisplayed(20)
EndIf

if(Alias_Criminal.GetActorRef().IsDead())
SetStage(40)
endIf
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

;BEGIN FRAGMENT Fragment_8
Function Fragment_8()
    STRMissivesBridge.StageChanged(GetFormID(), GetStage())
;BEGIN CODE
STRMissivesBridge.RemovePosting(Self, Alias_Missive, Alias_MissiveBoard)

while(Alias_Criminal.GetRef().Is3DLoaded())
Utility.Wait(1.0)
endWhile
Alias_Criminal.GetRef().Disable()

Stop()
;END CODE
EndFunction
;END FRAGMENT

;BEGIN FRAGMENT Fragment_6
Function Fragment_6()
    STRMissivesBridge.StageChanged(GetFormID(), GetStage())
;BEGIN CODE
If STRMissivesBridge.IsPersonalQuest(GetFormID())
    FailAllObjectives()
EndIf
SetStage(110)
;END CODE
EndFunction
;END FRAGMENT

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

;END FRAGMENT CODE - Do not edit anything between this and the begin comment

MiscObject Property Gold001  Auto  

GlobalVariable Property GoldReward  Auto  
