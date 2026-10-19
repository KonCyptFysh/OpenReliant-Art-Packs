mission({name="Reliant - Worn Paint inspection"})
reliant=flight_group("(FG)Reliant", {wing="player"})
reliant_inspection=ship("Reliant - Inspection", {type="reliant", group=reliant})
initialise=part("(F)ReliantInspection", function()
 CreateFlightGroup(reliant)
 return 1
end, {start=true})
