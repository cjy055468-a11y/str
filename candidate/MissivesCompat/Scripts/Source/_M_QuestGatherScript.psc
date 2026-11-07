;BEGIN FRAGMENT CODE - Do not edit anything between this and the end comment
;NEXT FRAGMENT INDEX 11
Scriptname _M_QuestGatherScript Extends Quest Hidden

;BEGIN ALIAS PROPERTY QuestGiver
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_QuestGiver Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Item
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_Item Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY MissiveBoard
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_MissiveBoard Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Missive
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_Missive Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Player
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_Player Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Hold
;ALIAS PROPERTY TYPE LocationAlias
LocationAlias Property Alias_Hold Auto
;END ALIAS PROPERTY

;BEGIN FRAGMENT Fragment_5
Function Fragment_5()
    STRMissivesBridge.StageChanged(GetFormID(), GetStage())
;BEGIN CODE
If STRMissivesBridge.IsPersonalQuest(GetFormID())
    ItemCount.SetValue(Game.GetPlayer().GetItemCount(Alias_Item.GetRef().GetBaseObject()))
EndIf
UpdateCurrentInstanceGlobal(ItemCount)
ItemTotal.SetValue(Utility.RandomInt(ItemTotalMin.GetValue() as int, ItemTotalMax.GetValue() as int))
UpdateCurrentInstanceGlobal(ItemTotal)
If STRMissivesBridge.IsPersonalQuest(GetFormID())
    SetObjectiveDisplayed(20)
EndIf

if(ItemCount.GetValue() > ItemTotal.GetValue())
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
    CompleteAllObjectives()
EndIf
If STRMissivesBridge.IsPersonalQuest(GetFormID())
    Game.GetPlayer().RemoveItem(Alias_Item.GetRef().GetBaseObject(), ItemTotal.GetValue() as int)
EndIf
If STRMissivesBridge.IsPersonalQuest(GetFormID())
    Game.GetPlayer().AddItem(Gold001, GoldReward.GetValue() as int)
EndIf
If STRMissivesBridge.IsPersonalQuest(GetFormID())
    Game.GetPlayer().AddItem(Reward)
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

;END FRAGMENT CODE - Do not edit anything between this and the begin comment

GlobalVariable Property ItemCount  Auto  

GlobalVariable Property ItemTotal  Auto  

GlobalVariable Property ItemTotalMax  Auto  

GlobalVariable Property ItemTotalMin  Auto  

MiscObject Property Gold001  Auto  

GlobalVariable Property GoldReward  Auto  

LeveledItem Property Reward  Auto  
