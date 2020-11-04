require("utils")

local r = require("robot")
local string = require("string")
local serialization = require("serialization")
local sides = require("sides")
local com = require("component")

local inv = com.inventory_controller
local f = sides.forward
local serialize = serialization.serialize

local driveName = "appliedenergistics2:drive"
logFile = io.open("scanner.log", "a")

local stats = {
  count = 0,
  fullTypes = 0,
  fullData = 0,
}

local state = {
  hasRoom = {},
}

function checkDrive()
  log("checking drive at " .. loc())
  if not isDrive() then
    return
  end

  for slot=1, 10 do
    if inv.getSlotStackSize(f, slot) > 0 then
      stats.count = stats.count + 1
      content = inv.getStackInSlot(f, slot)
      if string.find(content.name, "appliedenergistics2:") == nil then
        log("slot " .. slot .. ": Not an AE2 drive: " .. content.name)
      else
        if not content.canHoldNewItem then
          stats.fullTypes = stats.fullTypes + 1
        end
        if content.freeBytes < 1000 then
          stats.fullData = stats.fullData + 1
        end
      end
    else
      log("slot " .. slot .. ": Empty")
      k = loc()
      if state.hasRoom[k] == nil then
        state.hasRoom[k] = 1
      else
        state.hasRoom[k] = state.hasRoom[k] + 1
      end
    end
  end
end

function isDrive()
  name = inv.getInventoryName(f)
  if name == nil then
    return false
  end
  if name ~= driveName then
    log("not a drive: " .. name)
    return false
  end
  return true
end

local home = {locVal()}
local cont = true
local heading = "up"
while cont do
  checkDrive()
  if move(heading) then
    if not isDrive(f) then
      log("end of column, moving to next")
      move(sides.left)
      move(sides.down)
      r.turnRight()
      if heading == "up" then
        heading = "down"
      else
        heading = "up"
      end
      move(heading)
      cont = isDrive(f)
    end
  else
    cont = false
  end
end

log("heading home")
goTo(home)
log(serialize(stats, true))
log(serialize(state, true))
