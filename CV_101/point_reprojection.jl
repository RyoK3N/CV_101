"""
This file contains the implementation of point reprojection.
"""

using LinearAlgebra
using Plots

"""
    project_point(point3d::Vector{Float64}, camera_matrix::Matrix{Float64}, 
                 rotation_matrix::Matrix{Float64}, translation_vector::Vector{Float64})

Projects a 3D point onto a 2D image plane using perspective projection.

Arguments:
- point3d: 3D point coordinates [X, Y, Z]
- camera_matrix: 3x3 intrinsic camera matrix K
- rotation_matrix: 3x3 rotation matrix R
- translation_vector: 3x1 translation vector t

Returns:
- Vector{Float64}: 2D projected point coordinates [x, y]
"""
function project_point(point3d::Vector{Float64}, 
                      camera_matrix::Matrix{Float64},
                      rotation_matrix::Matrix{Float64}, 
                      translation_vector::Vector{Float64})
    # Ensure input dimensions are correct
    @assert length(point3d) == 3 "3D point must have 3 coordinates"
    @assert size(camera_matrix) == (3,3) "Camera matrix must be 3x3"
    @assert size(rotation_matrix) == (3,3) "Rotation matrix must be 3x3"
    @assert length(translation_vector) == 3 "Translation vector must have 3 elements"
    
    # Convert point to homogeneous coordinates
    point_homogeneous = [point3d; 1.0]
    
    # Create transformation matrix [R|t]
    transformation = hcat(rotation_matrix, translation_vector)
    
    # Project point using P = K[R|t]
    projection_matrix = camera_matrix * transformation
    
    # Apply projection
    projected_point = projection_matrix * point_homogeneous
    
    # Convert back from homogeneous coordinates to 2D
    x = projected_point[1] / projected_point[3]
    y = projected_point[2] / projected_point[3]
    
    return [x, y]
end

;