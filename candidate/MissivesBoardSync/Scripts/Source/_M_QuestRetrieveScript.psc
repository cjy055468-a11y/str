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
;BEGIN CODE
SetObjectiveDisplayed(20)
if(Game.GetPlayer().GetItemCount(Alias_Item.GetRef()))
SetObjectiveCompleted(20)
SetObjectiveDisplayed(40)
endIf
;END CODE
EndFunction
;END FRAGMENT

;BEGIN FRAGMENT Fragment_7
Function Fragment_7()
;BEGIN CODE
if(Alias_MissiveBoard.GetRef().GetItemCount(Alias_Missive.GetRef()) > 0)
Alias_MissiveBoard.GetRef().RemoveItem(Alias_Missive.GetRef())
;Debug.Trace("Missive Removed from Board")
elseif(Game.GetPlayer().GetItemCount(Alias_Missive.GetRef()) > 0)
Game.GetPlayer().RemoveItem(Alias_Missive.GetRef())
;Debug.Trace("Missive Removed from Player")
endIf

if(Alias_Chest.GetRef().GetItemCount(Alias_Item.GetRef()) > 0)
Alias_Chest.GetRef().RemoveItem(Alias_Item.GetRef())
endIf

Stop()
;END CODE
EndFunction
;END FRAGMENT

;BEGIN FRAGMENT Fragment_5
Function Fragment_5()
;BEGIN CODE
FailAllObjectives()
SetStage(110)
;END CODE
EndFunction
;END FRAGMENT

;BEGIN FRAGMENT Fragment_3
Function Fragment_3()
;BEGIN CODE
CompleteAllObjectives()
Game.GetPlayer().RemoveItem(Alias_Item.GetRef())
Game.GetPlayer().AddItem(Gold001, GoldReward.GetValue() as int)
SetStage(110)
;END CODE
EndFunction
;END FRAGMENT

;END FRAGMENT CODE - Do not edit anything between this and the begin comment

MiscObject Property Gold001  Auto

GlobalVariable Property GoldReward  Auto
