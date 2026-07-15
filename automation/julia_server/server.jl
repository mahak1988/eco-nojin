import HTTP
import JSON

function heavy_computation(params::Dict)
    sleep(2)
    return "Computation result for " * get(params, "watershed_id", "unknown")
end

HTTP.serve("0.0.0.0", 8080) do request
    if request.method == "POST" && request.resource == "/compute"
        body = JSON.parse(String(request.body))
        result = heavy_computation(body)
        return HTTP.Response(200, JSON.json(Dict("result" => result)))
    else
        return HTTP.Response(200, JSON.json(Dict("status" => "Julia server is running")))
    end
end
