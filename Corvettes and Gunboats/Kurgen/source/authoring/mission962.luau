mission({ name = "Kurgen - Worn Paint inspection" })
kurgen = flight_group("(FG)Kurgen", { wing = "player" })
kurgen_inspection = ship("Kurgen - Inspection", { type = "kurgan", group = kurgen })
initialise = part("(F)KurgenInspection", function()
    CreateFlightGroup(kurgen)
    return 1
end, { start = true })
