-- mission963.dte as mission source, written by sltool dte decompile.
mission({ name = "Scimitar inspection - launch" })

-- Flight groups

scimitar = flight_group("(FG)Scimitar", { wing = "player" })
torpedoes = flight_group("(FG)Torpedoes")

-- Ships

scimitar_inspection = ship("Scimitar - Inspection", { type = "scimitar", group = scimitar })
carried_torpedo_1 = ship("Carried torpedo 1", {
    type = "russian_torpedo",
    group = torpedoes,
    launch = { from = "scimitar", gate = 0 },
})
carried_torpedo_2 = ship("Carried torpedo 2", {
    type = "russian_torpedo",
    group = torpedoes,
    launch = { from = "scimitar", gate = 1 },
})

-- Parts

scimitar_inspection_2 = part("(F)ScimitarInspection", function()
    CreateFlightGroup(scimitar)
    CreateFlightGroup(torpedoes)
    Wait(8)
    StartLaunch(carried_torpedo_1)
    Wait(6)
    StartLaunch(carried_torpedo_2)
    return 1
end, { start = true })
