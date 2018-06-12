local json = require "misc/json"
local req_body = ""
local req_operation_name = ""

local function file_contents(file)
  local f = io.open(file, "r")
  if f~=nil then
    local content = f:read("*all")
    io.close(f)
    return content
  else
    error("file not found: " .. file)
  end
end

function init(args)
  local queryFile = args[1]
  local operationName = args[2]
  local query = file_contents(queryFile)
  req_body = json.encode({query=query,operationName=operationName})
  -- req_body = query
  req_operation_name = operationName
end

function request()
  wrk.method = "POST"
  wrk.headers["Content-Type"] = "application/json"
  -- wrk.headers["Content-Type"] = "application/graphql"
  wrk.body = req_body
  return wrk.format()
end

local function get_stat_summary(stat)
  local dist = {}
  for _, p in pairs({ 95, 98, 99 }) do
    dist[tostring(p)] = stat:percentile(p)
  end
  return {
    min=stat.min,
    max=stat.max,
    stdev=stat.stdev,
    mean=stat.mean,
    dist=dist
  }
end

logfile = io.open("wrk.log", "w");
local cnt = 0;
resp = "";

function response(status, header, body)
  if cnt == 0 then
     resp = body
     logfile:write(body)
     logfile:close()
    --  logfile:write("status:" .. status .. "\n");
     cnt = cnt + 1;
    --  logfile:write("status:" .. status .. "\n" .. body .. "\n-------------------------------------------------\n");
  end
end

function done(s, l, r)
  
  local f = assert(io.open("wrk.log", "r"))
  local t = f:read("*all")
  f:close()
  
  -- print("done", t)
  io.stderr:write(
    json.encode({
        latency=get_stat_summary(l),
        summary=s,
        requests=get_stat_summary(r),
        response=t,
    })
  )
  io.stderr:write('\n')
end
