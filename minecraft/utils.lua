local r = require("robot")
local serialization = require("serialization")
local sides = require("sides")
local com = require("component")

local inv = com.inventory_controller
local nav = com.navigation
local serialize = serialization.serialize

local logFile = io.open("scanner.log", "a")

function log(msg)
  print(msg)
  logFile:write(msg .. "\n")
end

function locVal()
  x, y, z = nav.getPosition()
  return x - 0.5, y - 0.5, z - 0.5
end

function loc()
  return table.concat({locVal()}, "/")
end

function move(dir, distance)
  targetFace = sides[dir]
  if targetFace == nil then
    log("Bad direction to move: " .. dir)
    return false
  end

  if distance == nil then
    distance = 1
  end

  log("starting from " .. loc())
  log(distance .. " steps heading " .. dir)
  turnTo(dir)

  went = 0
  go = r.forward
  if targetFace == sides.top then
    go = r.up
  elseif targetFace == sides.bottom then
    go = r.down
  end

  while went < distance do
    if go() then
      went = went + 1
    else
      log("Can't go further after " .. went .. " steps. Now at " .. loc())
      return false
    end
  end

  log("Now at " .. loc())
  return true
end

function turnTo(dir)
  target = sides[dir]
  if dir == sides.up or dir == sides.down then
    log("not turning " .. dir)
    return
  end
  log("turning to " .. sides[target] .. ", currently facing " .. sides[nav.getFacing()])
  spin = 0
  while nav.getFacing() ~= target and spin < 4 do
    r.turnLeft()
    spin = spin + 1
  end
  if spin == 4 then
    log("I'm confused.")
    die()
  end
end

function goTo(destination)
  log("going to " .. serialize(destination) .. " from " .. loc())
  cur = {}
  dest = {}
  
  cur.x, cur.y, cur.z = locVal()
  dest.x, dest.y, dest.z = destination[1], destination[2], destination[3]

  delta = {
    x = dest.x - cur.x,
    y = dest.y - cur.y,
    z = dest.z - cur.z,
  }

  log("delta: " .. serialize(delta))
  facing = nav.getFacing()

  for _, k in pairs({"x", "y", "z"}) do
    if delta[k] ~= 0 then
      log("moving " .. delta[k] .. " in direction " .. k)
      move("pos" .. k, delta[k])
      log ("now at " .. loc())
    end
  end

  log("Arriving...")
  turnTo(sides[facing])
end

return true
