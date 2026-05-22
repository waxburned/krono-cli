-- writes EOF flag on natural end, or current position on early quit
local flag_file = os.getenv("KRONO_EOF_FILE")
if not flag_file then return end

local reached_eof = false

mp.register_event("end-file", function(event)
    if event.reason == "eof" then
        reached_eof = true
        local f = io.open(flag_file, "w")
        if f then f:write("eof"); f:close() end
    end
end)

mp.register_event("shutdown", function()
    if not reached_eof then
        local pos = mp.get_property_number("time-pos", 0)
        local f = io.open(flag_file, "w")
        if f then f:write(string.format("%.0f", pos)); f:close() end
    end
end)
