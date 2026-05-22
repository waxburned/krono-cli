-- tracks playback position and writes EOF or last position on exit
local flag_file = os.getenv("KRONO_EOF_FILE")
if not flag_file then return end

local last_pos = 0
local reached_eof = false

-- update position every second
mp.add_periodic_timer(1, function()
    local pos = mp.get_property_number("time-pos")
    if pos then last_pos = pos end
end)

mp.register_event("end-file", function(event)
    if event.reason == "eof" then
        reached_eof = true
        local f = io.open(flag_file, "w")
        if f then f:write("eof"); f:close() end
    end
end)

mp.register_event("shutdown", function()
    if not reached_eof then
        local f = io.open(flag_file, "w")
        if f then f:write(string.format("%.0f", last_pos)); f:close() end
    end
end)
