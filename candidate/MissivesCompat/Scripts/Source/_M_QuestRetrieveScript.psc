;BEGIN FRAGMENT CODE - Do not edit anything between this and the end comment
;NEXT FRAGMENT INDEX 9
Scriptname _M_QuestRetrieveScript Extends Quest Hidden

;BEGIN ALIAS PROPERTY Dungeon
;ALIAS PROPERTY TYPE LocationAlias
LocationAlias Property Alias_Dungeon Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY chest
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_chest Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Hold
;ALIAS PROPERTY TYPE LocationAlias
LocationAlias Property Alias_Hold Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY QuestGiver
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_QuestGiver Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY MissiveBoard
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_MissiveBoard Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Item
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_Item Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Missive
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_Missive Auto
;END ALIAS PROPERTY

;BEGIN FRAGMENT Fragment_0
Function Fragment_0()
    STRMissivesBridge.StageChanged(GetFormID(), GetStage())
    If STRMissivesBridge.IsConnected() && STRMissivesBridge.IsPersonalQuest(GetFormID()) && !STRMissivesBridge.IsSourceQuest(GetFormID())
        ; Forced aliases suppress independent created items. Place this exact
        ; personal item in the canonical chest once on acceptance.
        Alias_Item.GetRef().Enable()
        Alias_Chest.GetRef().AddItem(Alias_Item.GetRef(), 1, True)
    EndIf
;BEGIN CODE
If STRMissivesBridge.IsPersonalQuest(GetFormID())
    SetObjectiveDisplayed(20)
EndIf
if(STRMissivesBridge.IsPersonalQuest(GetFormID()) && Game.GetPlayer().GetItemCount(Alias_Item.GetRef()))
If STRMissivesBridge.IsPersonalQuest(GetFormID())
    SetObjectiveCompleted(20)
EndIf
If STRMissivesBridge.IsPersonalQuest(GetFormID())
    SetObjectiveDisplayed(40)
EndIf
endIf
;END CODE
EndFunction
;END FRAGMENT

;BEGIN FRAGMENT Fragment_7
Function Fragment_7()
    STRMissivesBridge.StageChanged(GetFormID(), GetStage())
;BEGIN CODE
STRMissivesBridge.RemovePosting(Self, Alias_Missive, Alias_MissiveBoard)

if(Alias_Chest.GetRef().GetItemCount(Alias_Item.GetRef()) > 0)
Alias_Chest.GetRef().RemoveItem(Alias_Item.GetRef())
endIf

Stop()
;END CODE
EndFunction
;END FRAGMENT

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

;END FRAGMENT CODE - Do not edit anything between this and the begin comment

MiscObject Property Gold001  Auto  

GlobalVariable Property GoldReward  Auto  
