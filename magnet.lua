-- SPDX-License-Identifier: GPL-3.0-or-later
-- Copyright 2021, CZ.NIC z.s.p.o. (http://www.nic.cz/)
local auth = "/usr/share/lighttpd-turris-auth/cgiauth.py"

local function valid_cookie(cookie)
	if cookie:len() ~= 64 then
		return false
	end
	for i = 1,64,1 do
		local byte = cookie:byte(i)
		-- ASCII: a=97, b=122
		if byte < 97 or byte > 122 then
			return false
		end
	end
	return true
end

local logged = false
if lighty.request.Cookie then
	for cookiepair in lighty.request.Cookie:gmatch("[^;]+") do
		local key, value = cookiepair:match("(%S+)=(.*);?")
		if key == "turrisauth" and valid_cookie(value) then
			logged = os.execute(auth .. " --verify '" .. value .. "'") == 0
			break
		end
	end
end


if not logged then
	lighty.header["Location"] = "/login?orig=" .. lighty.env["request.uri"]
	return 302
end
