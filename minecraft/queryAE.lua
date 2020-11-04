me = components.me_interface

craftables = me.getCraftables()
print("Found " .. craftables.n .. " patterns.")

matches = {}

for word in arg do
  for k, v in pairs(craftables) do
    info = v.getItemStack()
    label = info.label
    name = info.name
    if string.find(info .. "/" .. name, word) then
      table.insert(matches, info)
    end
  end
  craftables = matches
end

print("Found " .. matches.n .. " matches.")

for k, v in pairs(matches) do
  info = v.getItemStack()
  print(info.label .. ": " .. info.name)
end
