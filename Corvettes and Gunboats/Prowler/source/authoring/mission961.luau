mission({name="Prowler - Worn Paint inspection"})
prowler=flight_group("(FG)Prowler", {wing="player"})
prowler_inspection=ship("Prowler - Inspection", {type="prowler", group=prowler})
initialise=part("(F)ProwlerInspection", function() CreateFlightGroup(prowler) return 1 end, {start=true})
