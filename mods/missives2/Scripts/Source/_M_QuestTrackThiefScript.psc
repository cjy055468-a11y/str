;BEGIN FRAGMENT CODE - Do not edit anything between this and the end comment
;NEXT FRAGMENT INDEX 10
Scriptname _M_QuestTrackThiefScript Extends Quest Hidden

;BEGIN ALIAS PROPERTY Hold
;ALIAS PROPERTY TYPE LocationAlias
LocationAlias Property Alias_Hold Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Inn1
;ALIAS PROPERTY TYPE LocationAlias
LocationAlias Property Alias_Inn1 Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Thief
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_Thief Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Item
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_Item Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY InnMarker2
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_InnMarker2 Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Inn2
;ALIAS PROPERTY TYPE LocationAlias
LocationAlias Property Alias_Inn2 Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY InnMarker1
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_InnMarker1 Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY OtherHold
;ALIAS PROPERTY TYPE LocationAlias
LocationAlias Property Alias_OtherHold Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY MissiveBoard
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_MissiveBoard Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY QuestGiver
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_QuestGiver Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Missive
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_Missive Auto
;END ALIAS PROPERTY

;BEGIN FRAGMENT Fragment_5
Function Fragment_5()
    STRMissivesBridge.StageChanged(GetFormID(), GetStage())
;BEGIN CODE
If STRMissivesBridge.IsPersonalQuest(GetFormID())
    FailAllObjectives()
EndIf
SetStage(110)
;END CODE
EndFunction
;END FRAGMENT

;BEGIN FRAGMENT Fragment_0
Function Fragment_0()
    STRMissivesBridge.StageChanged(GetFormID(), GetStage())
;BEGIN CODE
;
;END CODE
EndFunction
;END FRAGMENT

;BEGIN FRAGMENT Fragment_3
Function Fragment_3()
    STRMissivesBridge.StageChanged(GetFormID(), GetStage())
;BEGIN CODE
If STRMissivesBridge.IsPersonalQuest(GetFormID())
    CompleteAllObjectives()
EndIf
If STRMissivesBridge.IsPersonalQuest(GetFormID())
    Game.GetPlayer().RemoveItem(Alias_Item.GetRef())
EndIf
If STRMissivesBridge.IsPersonalQuest(GetFormID())
    Game.GetPlayer().AddItem(Gold001, GoldReward.GetValue() as int)
EndIf
SetStage(110)
;END CODE
EndFunction
;END FRAGMENT

;BEGIN FRAGMENT Fragment_7
Function Fragment_7()
    STRMissivesBridge.StageChanged(GetFormID(), GetStage())
;BEGIN CODE
STRMissivesBridge.RemovePosting(Self, Alias_Missive, Alias_MissiveBoard)

while(Alias_Thief.GetRef().Is3DLoaded())
Utility.Wait(1.0)
endWhile
Alias_Thief.GetRef().Disable()

Stop()
;END CODE
EndFunction
;END FRAGMENT

;BEGIN FRAGMENT Fragment_2
Function Fragment_2()
    STRMissivesBridge.StageChanged(GetFormID(), GetStage())
;BEGIN CODE
If STRMissivesBridge.IsPersonalQuest(GetFormID())
    SetObjectiveDisplayed(10)
EndIf
Alias_Thief.GetRef().Enable()
Alias_Item.GetRef().Enable()
Alias_Thief.GetRef().AddItem(Alias_Item.GetRef())
;END CODE
EndFunction
;END FRAGMENT

;END FRAGMENT CODE - Do not edit anything between this and the begin comment

MiscObject Property Gold001  Auto  

GlobalVariable Property GoldReward  Auto  
