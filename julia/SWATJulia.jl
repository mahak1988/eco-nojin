# High-performance SWAT core in Julia
# 10-100x faster than Python for numerical computations

module SWATJulia

using DifferentialEquations
using LinearAlgebra
using Statistics

export scs_curve_number, penman_monteith_et, muskingum_routing

"""
SCS Curve Number Method (vectorized)
"""
function scs_curve_number(precipitation::Vector{Float64}, cn::Float64)
    S = (1000.0 / cn) - 10.0
    Ia = 0.2 * S
    
    runoff = similar(precipitation)
    @. runoff = ifelse.(precipitation .> Ia, 
                       ((precipitation .- Ia).^2) ./ (precipitation .+ 0.8*S), 
                       0.0)
    return runoff
end

"""
Penman-Monteith ET (simplified Hargreaves)
"""
function penman_monteith_et(temperature::Vector{Float64}, veg_cover::Float64)
    Ra = 15.0  # MJ/m²/day
    eto = @. 0.0023 * Ra * (temperature + 17.8)
    return eto .* veg_cover
end

"""
Muskingum routing (optimized)
"""
function muskingum_routing(inflow::Vector{Float64}, k::Float64=1.0, x::Float64=0.2)
    n = length(inflow)
    outflow = zeros(n)
    
    dt = 1.0
    c0 = (dt - 2*k*x) / (2*k*(1-x) + dt)
    c1 = (dt + 2*k*x) / (2*k*(1-x) + dt)
    c2 = (2*k*(1-x) - dt) / (2*k*(1-x) + dt)
    
    # Normalize
    c_sum = c0 + c1 + c2
    c0, c1, c2 = c0/c_sum, c1/c_sum, c2/c_sum
    
    q_prev = 0.0
    for i in 1:n
        if i == 1
            outflow[i] = c0*inflow[i] + c1*inflow[i] + c2*q_prev
        else
            outflow[i] = c0*inflow[i] + c1*outflow[i-1] + c2*q_prev
        end
        q_prev = outflow[i]
    end
    
    return outflow
end

"""
Full SWAT simulation (high performance)
"""
function run_swat(precip::Vector{Float64}, temp::Vector{Float64}, 
                  cn::Float64, area_km2::Float64, veg_cover::Float64)
    # Runoff (SCS)
    runoff = scs_curve_number(precip, cn)
    
    # ET
    et = penman_monteith_et(temp, veg_cover)
    
    # Routing
    inflow = runoff .* area_km2 .* 1000 .* 1.5
    streamflow = muskingum_routing(inflow) ./ 86400
    
    return (runoff=runoff, et=et, streamflow=streamflow)
end

end # module
