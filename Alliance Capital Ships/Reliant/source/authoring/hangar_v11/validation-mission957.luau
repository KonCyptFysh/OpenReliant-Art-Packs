-- Native Reliant launch, free flight, and permission-to-land review.
-- Build with the official 0.18.0 sltool; first ship is always the player.
mission({ name = "Reliant - Patriot launch and landing review" })

alpha = flight_group("(FG)Review pilot", { wing = "player" })
carrier_group = flight_group("(FG)Reliant")
player = ship("Patriot - Review", {
    type = "patriot", group = alpha, launch = { from = "reliant", gate = 1 },
})
reliant = ship("ANS Reliant", {
    type = "reliant", group = carrier_group, pilot = "reliant_bridge_officer",
})

start = part("(F)Launch and free flight", function()
    game.landing_cleared = 0
    game.mission_over = 0
    game.mission_success = 3
    CreateFlightGroup(carrier_group)
    SetHostile(reliant, 0)
    SetInvulnerability(reliant, 1)
    DoNotDisturb(reliant, 1)
    DisableGuns(reliant, 1)
    DisableMissiles(reliant, 1)
    SetAI(reliant, "do_nothing", 1, nil)
    CreateFlightGroup(alpha)
    SetInvulnerability(player, 1)
    StartLaunch(alpha)
    WaitForJumpOrLaunch(alpha)
    game.landing_cleared = 1
    SetPrimaryTarget(reliant)
    PrintDebugMessage("Review flight: COMMS > BASE > PERMISSION TO LAND ends the mission.")
    spawn(doors)
    return 1
end, { start = true })

doors = part("(F)Exterior door cycle", function()
    -- Native tracks include a return leg: stop at their open pose for inspection.
    -- The attached mission script suppresses ALL these animation commands once
    -- Land is ordered, including Stop, so the native landing owns its door.
    Wait(3)
    StartShipAnimation(reliant, "opendoor")
    StartShipAnimation(reliant, "opendoor2")
    Wait(1)
    StopShipAnimation(reliant, "opendoor")
    StopShipAnimation(reliant, "opendoor2")
    Wait(12)
    StartShipAnimationReverse(reliant, "opendoor")
    StartShipAnimationReverse(reliant, "opendoor2")
    Wait(2)
    StopShipAnimation(reliant, "opendoor")
    StopShipAnimation(reliant, "opendoor2")
    Wait(9)
    spawn(doors)
    return 1
end)

autoland = part("(F)Validation landing", function()
 Wait(48)
 SetAI(player,"land",1,reliant)
 return 1
end,{start=true})
