-- SPDX-License-Identifier: GPL-3.0-or-later
-- Copyright 2021, CZ.NIC z.s.p.o. (http://www.nic.cz/)
local auth = "/usr/share/lighttpd-turris-auth/cgiauth.py"

local logged = false
if lighty.request.Cookie then
	for cookiepair in lighty.request.Cookie:gmatch("[^;]+") do
		local key, value = cookiepair:match("(%S+)=(.*);?")
		if key == "turrisauth" then
			logged = os.execute(auth .. " --verify '" .. value .. "'") == 0
			break
		end
	end
end


if not logged then
	lighty.header["Location"] = "/login?orig=" .. lighty.env["request.uri"]
	return 302
end
